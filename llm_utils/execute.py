from typing import Any
import ast
from logging import Logger, getLogger
import re

from z3_utils import Logic

def get_function_name(code: str) -> str:
	tree = ast.parse(code)
	node = tree.body[0]
	assert isinstance(node, ast.FunctionDef)
	return node.name

def _switch_enum_context(code: str) -> str:
	return re.sub(r"EnumSort\(([^\(]+)\)", r"EnumSort(\1, ctx=l.context)", code, flags=re.MULTILINE)

def execute_code(
	code: str,
	context: dict[str, Any] = {},
	logger: Logger = getLogger(__name__),
	use_common_knowledge: bool = True,
):
	exec('''from z3 import *
from z3_utils import Logic
''', context)
	try:
		code = _switch_enum_context(code)
		exec(code, context)
		logger.debug('Code imported.')
	except Exception as e:
		logger.error('Failed to import code.')
		return False, e

	function_name = get_function_name(code)

	logger.debug(f'Executing {function_name}...')
	logic: Logic
	try:
		logic = context[function_name](use_common_knowledge=use_common_knowledge)
		logger.debug(f'{function_name} executed.')
	except Exception as e:
		logger.error(f'Failed to execute {function_name}.')
		logger.debug(code)
		return False, e

	logger.debug('Judging...')
	# TODO: handle common exceptions
	try:
		result = logic.judge()
		logger.debug('Judged.')
		return True, result
	except Exception as e:
		logger.error('Failed to judge.')
		return False, e
