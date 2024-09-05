from typing import Any
import ast
from logging import Logger, getLogger

from z3_utils import Logic

def get_function_name(code: str) -> str:
	tree = ast.parse(code)
	node = tree.body[0]
	assert isinstance(node, ast.FunctionDef)
	return node.name

def execute_code(
	code: str,
	context: dict[str, Any] = {},
	logger: Logger = getLogger(__name__),
):
	exec('''from z3 import *
from z3_utils import Logic
''', context)
	try:
		exec(code, context)
		logger.debug('Code imported.')
	except Exception as e:
		logger.error('Failed to import code.')
		return False, e

	function_name = get_function_name(code)

	logger.debug(f'Executing {function_name}...')
	logic: Logic
	try:
		logic = context[function_name]()
		logger.debug(f'{function_name} executed.')
	except Exception as e:
		logger.error(f'Failed to execute {function_name}.')
		return False, e

	logger.debug('Judging...')
	# TODO: handle common exceptions
	try:
		logic.judge()
		logger.debug('Judged.')
		return True, logic
	except Exception as e:
		logger.error('Failed to judge.')
		return False, e
