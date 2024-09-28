from typing import Any, Awaitable, Iterable, Literal, Optional
import ast
import asyncio
from concurrent.futures import ProcessPoolExecutor
from logging import Logger, getLogger, DEBUG
from multiprocessing import Process, Queue
import re

from z3_utils import Logic

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from z3.z3 import CheckSatResult

def get_function_name(code: str) -> str:
	tree = ast.parse(code)
	node = tree.body[0]
	assert isinstance(node, ast.FunctionDef), f'Expected FunctionDef, but got {type(node)}'
	return node.name

def _switch_sorts_context(code: str) -> str:
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
	timeout: Optional[float] = 5,
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
	loop = asyncio.get_running_loop()
	with ProcessPoolExecutor() as pool:
		tasks = [
			loop.run_in_executor(
				pool,
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
	return asyncio.as_completed(tasks)

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
