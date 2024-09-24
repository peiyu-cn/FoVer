from typing import Callable, Literal

import asyncio
from logging import Logger, getLogger
from z3 import CheckSatResult

from .execute import execute_codes

def process_response(content: str):
	content = content.strip()
	if content.startswith('```'):
		assert content.endswith('```'), f'Expecting code block to end with "```", got "{content[-10:]}".'
		lf_idx = content.find('\n')
		assert lf_idx != -1, 'No line feed found in code block.'
		return content[lf_idx + 1:-3].rstrip()
	else:
		assert content.startswith('def '), f'Expecting code block to start with "def ", got "{content[:10]}".'
		assert content.endswith('return l'), f'Expecting code block to end with "return l", got "{content[-10:]}".'
		return content

def check_responses(
	responses: list[str],
	check_cb: Callable[[int, list[bool | CheckSatResult]], tuple[int, int, int, int]],
	logger: Logger = getLogger(__name__),
):
	return asyncio.run(check_responses_async(responses, check_cb, logger))

async def check_responses_async(
	responses: list[str],
	check_cb: Callable[[int, list[bool | CheckSatResult]], tuple[int, int, int, int]],
	logger: Logger = getLogger(__name__),
):
	correct = 0
	wrong = 0
	llm_failed = 0
	z3_failed = 0
	total = 0

	tasks = execute_codes(
		responses,
		use_common_knowledge=False,
	)

	for i, result in enumerate(tasks):
		logger.info('Checking response #%d...', i)
		result = await tasks[i]
		if result[0] == False:
			llm_failed += 1
			total += 1
			logger.error('Failed to execute #%d: %s', i, result[1])
			continue
		else:
			c, w, f, t = check_cb(i, result[1])
			correct += c
			wrong += w
			z3_failed += f
			total += t

	return correct, wrong, llm_failed, z3_failed, total
