from typing import Callable, Literal, Union

import asyncio
from logging import Logger, getLogger
from z3 import CheckSatResult, unknown

from .execute import execute_codes

from typing import TYPE_CHECKING

_logger = getLogger(__name__)

def process_response(content: str):
	content = content.strip()
	if content.__contains__('```'):
		start_idx = content.find('```')
		content = content[start_idx + 3:]
		#assert content.endswith('```'), f'Expecting code block to end with "```", got "{content[-10:]}".'
		lf_idx = content.find('\n')
		assert lf_idx != -1, 'No line feed found in code block.'
		end_idx = content.find('```')
		return content[lf_idx + 1:end_idx].rstrip()
	else:
		assert content.startswith('def '), f'Expecting code block to start with "def ", got "{content[:10]}".'
		#assert content.endswith('return l'), f'Expecting code block to end with "return l", got "{content[-10:]}".'
		return content

def check_responses(
	responses: list[str],
	check_cb: Callable[[int, list[bool | CheckSatResult]], tuple[int, int, int, int]],
	use_definitions: bool = True,
	use_common_knowledge: bool = True,
	sync: bool = False,
	logger: Logger = _logger,
):
	return asyncio.run(check_responses_async(responses, check_cb, use_definitions, use_common_knowledge, sync, logger))

async def check_responses_async(
	responses: list[str],
	check_cb: Callable[[int, list[bool | CheckSatResult]], tuple[int, int, int, int]],
	use_definitions: bool,
	use_common_knowledge: bool,
	sync: bool,
	logger: Logger,
):
	correct = 0
	wrong = 0
	llm_failed = 0
	z3_failed = 0
	total = 0

	logger.debug('Executing %d responses...', len(responses))
	tasks = execute_codes(
		responses,
		use_definitions=use_definitions,
		use_common_knowledge=use_common_knowledge,
		sync=sync,
	)

	results = [] # type: list[Union[tuple[Literal[True], list[bool | CheckSatResult]], tuple[Literal[False], Exception]]]
	i = -1
	for task in tasks:
		i += 1
		logger.info('Checking response #%d...', i)
		result = await task
		results.append(result)
		if result[0] == True or result[0] == False and isinstance(result[1], TimeoutError):
			if isinstance(result[1], TimeoutError):
				# Execution timed out. It should be a Z3 failure, however, it is very possible that the result is False.
				logger.error('Execution timed out for #%d.', i)
				c, w, f, t = check_cb(i, [unknown])
			else:
				if TYPE_CHECKING:
					assert result[0] == True # very stupid
				c, w, f, t = check_cb(i, result[1])
			correct += c
			wrong += w
			z3_failed += f
			total += t
			continue
		else:
			llm_failed += 1
			total += 1
			logger.error('Failed to execute #%d: %s', i, result[1])

	print([
		r[1][0] if r[0] == True else None
		for r in results
	])

	return correct, wrong, llm_failed, z3_failed, total
