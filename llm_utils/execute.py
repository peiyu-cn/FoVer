from typing import Any, Awaitable, Iterable, Literal, Optional

import ast
import asyncio
from logging import Logger, getLogger, DEBUG
from multiprocessing import Process, Queue
import re

from async_utils import wrap_function_async
from z3_utils import Logic

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from z3.z3 import CheckSatResult

def get_function_name(code: str) -> str:
	tree = ast.parse(code)
	node = tree.body[0]
	assert isinstance(node, ast.FunctionDef), f'Expected FunctionDef, but got {type(node)}'
	return node.name

import re
from typing import List, Tuple, Match

import re
from typing import List, Tuple, Match, Optional

class AssertionProcessor:
	@staticmethod
	def find_assertions_list(p: Literal['claims', 'assertions'], text: str) -> Optional[Tuple[int, int, str]]:
		# 使用正则表达式找到l.assertions的开始
		match = re.search(fr'l\.{p}\s*=\s*\[', text)
		if not match:
			return None
		
		start_pos = match.end()
		# 手动追踪嵌套的方括号
		bracket_level = 1
		for i in range(start_pos, len(text)):
			if text[i] == '[':
				bracket_level += 1
			elif text[i] == ']':
				bracket_level -= 1
				if bracket_level == 0:
					# 找到匹配的闭合方括号
					return (match.start(), i + 1, text[start_pos:i])
		
		return None

	@staticmethod
	def parse_assertions(assertions_str: str) -> List[Tuple[int, int, str, str]]:
		results = []
		
		# 跟踪圆括号和方括号
		round_level = 0
		square_level = 0
		current_tuple = ""
		start_pos = 0
		
		i = 0
		while i < len(assertions_str):
			char = assertions_str[i]
			
			if char == '(':
				if round_level == 0:
					start_pos = i
				round_level += 1
			elif char == ')':
				round_level -= 1
				if round_level == 0:
					# 找到完整的元组
					tuple_content = assertions_str[start_pos+1:i]
					# 分离字符串和表达式部分
					try:
						# 寻找第一个非转义的引号结束位置
						in_escape = False
						quote_end = -1
						for j, c in enumerate(tuple_content):
							if c == '\\':
								in_escape = not in_escape
							elif c == '"' and not in_escape:
								if tuple_content[j:j+2] == '",':
									quote_end = j
									break
							else:
								in_escape = False
						
						if quote_end != -1:
							string_part = tuple_content[:quote_end+1]
							expr_part = tuple_content[quote_end+2:].strip()
							results.append((start_pos, i+1, string_part, expr_part))
					except ValueError:
						pass
			elif char == '[':
				square_level += 1
			elif char == ']':
				square_level -= 1
				
			i += 1
		
		return results

	@staticmethod
	def process_tuple(string_part: str, expr_part: str) -> Tuple[str, str]:
		# 计算string_part中的either数量
		either_count = len(re.findall(r'\b[Ee]ither\b', string_part))
		
		# 计算expr_part中的Xor数量
		xor_count = expr_part.count('Xor')
		
		if xor_count < either_count:
			# 找到最后一个Xor后的Or
			last_xor_index = expr_part.rfind('Xor')
			if last_xor_index == -1:
				last_xor_index = 0
			remaining_expr = expr_part[last_xor_index:]
			or_matches = list(re.finditer(r'\bOr\b', remaining_expr))
			
			# 只替换需要的数量
			replacements_needed = min(either_count - xor_count, len(or_matches))
			
			# 从后往前替换，以避免位置变化
			modified_expr = list(expr_part)
			for i in range(replacements_needed):
				or_match = or_matches[i]
				absolute_pos = last_xor_index + or_match.start()
				modified_expr[absolute_pos:absolute_pos+2] = 'Xor'
			
				expr_part = ''.join(modified_expr)
		
		return string_part, expr_part

	@staticmethod
	def process_text(p: Literal['claims', 'assertions'], text: str) -> str:
		# 找到assertions列表
		assertions_info = AssertionProcessor.find_assertions_list(p, text)
		if not assertions_info:
			return text
		
		list_start, list_end, assertions_str = assertions_info
		tuples = AssertionProcessor.parse_assertions(assertions_str)
		
		# 从后往前处理每个元组，以避免位置变化影响
		modified_text = list(text)
		for start_pos, end_pos, string_part, expr_part in reversed(tuples):
			processed_string, processed_expr = AssertionProcessor.process_tuple(string_part, expr_part)
			new_tuple = f"({processed_string}, {processed_expr})"
			
			# 计算在完整文本中的实际位置
			actual_start = list_start + len(f'l.{p} = [') + start_pos
			actual_end = list_start + len(f'l.{p} = [') + end_pos
			modified_text[actual_start:actual_end] = new_tuple
		
		return ''.join(modified_text)

	@staticmethod
	def process_all(text: str) -> str:
		text = AssertionProcessor.process_text('claims', text)
		text = AssertionProcessor.process_text('assertions', text)
		return text

def _switch_sorts_context(code: str) -> str:
	#code = re.sub(r'l.definitions = \[[^\[\]]*\]', 'l.definitions = []', code, flags=re.MULTILINE)
	#code = re.sub(r'l.common_knowledge = \[[^\[\]]*\]', 'l.common_knowledge = []', code, flags=re.MULTILINE)
	#code = AssertionProcessor.process_all(code)
	return code
	#return re.sub(r"EnumSort\(([^\(]+)\)", r"EnumSort(\1, ctx=l.context)", code, flags=re.MULTILINE)
	#code = _switch_sort_context('DeclareSort', code)
	#code = _switch_sort_context('EnumSort', code)
	code = re.sub(r"([A-Z][a-z]+Sort)\(([^\(\)]+)\)", r"\1(\2, ctx=l.context)", code, flags=re.MULTILINE)
	code = re.sub(r"([A-Z][a-z]+Sort)\(\)", r"\1(ctx=l.context)", code)
	code = re.sub(r"(Bool|Int)s\('([^\(\)']+)'\)", r"\1s('\2', ctx=l.context)", code)
	return code

_logger = getLogger(__name__)

def execute_code(
	code: str,
	context: dict[str, Any],
	logger: Logger,
	use_definitions: bool,
	use_common_knowledge: bool,
	translate: bool,
	timeout: Optional[float],
) -> "tuple[Literal[True], list[bool | CheckSatResult]] | tuple[Literal[False], Exception]":
	queue = Queue()
	process = Process(target=_execute_code, args=(queue, code, context, logger, use_definitions, use_common_knowledge, translate))
	process.start()
	process.join(timeout)
	if process.is_alive():
		logger.error('Execution timed out after %.2f seconds.', timeout)
		process.terminate()
		return False, TimeoutError(f'Execution timed out after {timeout} seconds.')
	else:
		return queue.get()

def execute_codes(
	codes: list[str],
	contexts: Optional[list[dict[str, Any]]] = None,
	logger: Logger = _logger,
	use_definitions: bool = True,
	use_common_knowledge: bool = True,
	translate: bool = False,
	timeout: Optional[float] = 30,
	sync: bool = False,
) -> "Iterable[Awaitable[tuple[Literal[True], list[bool | CheckSatResult]] | tuple[Literal[False], Exception]]]":
	if sync:
		return _execute_codes_sync(codes, contexts, logger, use_definitions, use_common_knowledge, translate, timeout)
	else:
		return _execute_codes_async(codes, contexts, logger, use_definitions, use_common_knowledge, translate, timeout)

def _execute_codes_sync(
	codes: list[str],
	contexts: Optional[list[dict[str, Any]]],
	logger: Logger,
	use_definitions: bool,
	use_common_knowledge: bool,
	translate: bool,
	timeout: Optional[float],
):
	from async_utils import SyncAwaitable
	return [
		SyncAwaitable(
			execute_code,
			code,
			context,
			logger,
			use_definitions,
			use_common_knowledge,
			translate,
			timeout,
		)
		for code, context in zip(codes, contexts or [{}] * len(codes))
	]

def _execute_codes_async(
	codes: list[str],
	contexts: Optional[list[dict[str, Any]]],
	logger: Logger,
	use_definitions: bool,
	use_common_knowledge: bool,
	translate: bool,
	timeout: Optional[float],
):
	tasks = [
		asyncio.create_task(
			wrap_function_async(
				execute_code,
				code,
				context,
				logger,
				use_definitions,
				use_common_knowledge,
				translate,
				timeout,
			)
		)
		for code, context in zip(codes, contexts or [{}] * len(codes))
	]
	return tasks

def _execute_code(
	queue: Queue,
	code: str,
	context: dict[str, Any],
	logger: Logger,
	use_definitions: bool,
	use_common_knowledge: bool,
	translate: bool,
):
	exec('''from z3.z3 import *
from z3_utils import Logic
''', context)
	try:
		code = _switch_sorts_context(code)
		exec(code, context)
		logger.debug('Code imported.')
	except Exception as e:
		logger.error('Failed to import code.')
		queue.put((False, e))
		return

	function_name = get_function_name(code)

	logger.debug(f'Executing {function_name}...')
	logic: Logic
	try:
		logic = context[function_name](
			use_definitions=use_definitions,
			use_common_knowledge=use_common_knowledge,
			translate=translate,
		)
		logger.debug(f'{function_name} executed.')
	except Exception as e:
		logger.error(f'Failed to execute {function_name}.')
		logger.debug(code)
		if logger.isEnabledFor(DEBUG):
			logger.exception(e, stack_info=True, stacklevel=5)
		queue.put((False, e))
		return

	logger.debug('Judging...')
	# TODO: handle common exceptions
	try:
		result = logic.judge()
		logger.debug('Judged.')
		queue.put((True, result))
		return
	except Exception as e:
		logger.error('Failed to judge.')
		if logger.isEnabledFor(DEBUG):
			logger.exception(e, stack_info=True, stacklevel=5)
		queue.put((False, e))
		return
