from typing import Callable, Optional

from logging import Logger, getLogger
import json
from z3 import CheckSatResult

from .response import process_response, check_responses

def check_langchain_response(
	response_file_path: str,
	check_cb: Callable[[int, list[bool | CheckSatResult]], tuple[int, int, int, int]],
	prefill: Optional[str] = None,
	logger: Logger = getLogger(__name__),
):
	with open(response_file_path, 'r', encoding='utf-8') as file:
		j = json.load(file)

	failures: list[int] = []
	responses: list[str] = []
	for i, item in enumerate(j):
		response = item['response']
		if not isinstance(response, str):
			failures.append(i)
			logger.error('Response #%d failed: %s', i, response['type'])
			continue
		try:
			if prefill:
				response = prefill + response
			r = process_response(response)
			responses.append(r)
		except AssertionError as e:
			failures.append(i)
			logger.error('Response #%d failed: %s', i, e)

	i_r = list(set(range(len(j))) - set(failures)) # [0, 1, 2, 3] -> [0, 1, 3, 6]
	# i_map = {i: i_r.index(i) for i in i_r} # [0, 1, 3, 6] -> [0, 1, 2, 3]
	def check_cb_wrapper(i: int, results: list[bool | CheckSatResult]):
		"""
		Args:
			i: index of the response ([0, 1, 2, 3])
		"""
		# i_r = i + c, where c is the number of failures before i
		# if [2, 4, 5] fails, [0, 1, 2, 3, 4, 5, 6] -> [0, 1, 3, 6]
		# i_r[0] = 0, i_r[1] = 1, i_r[2] = 3, i_r[3] = 6
		# c[0] = 0, c[1] = 0, c[2] = 1, c[3] = 3
		# c[i] = count(failures < i_r[i])
		# TOO COMPLICATED
		return check_cb(i_r[i], results)

	correct, wrong, llm_failed, z3_failed, total = check_responses(responses, check_cb_wrapper)
	return correct, wrong, llm_failed + len(failures), z3_failed, total + len(failures)
