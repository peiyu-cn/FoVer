from typing import Callable, Literal

from z3 import CheckSatResult

from .execute import execute_code

def process_response(content: str):
	content = content.strip()
	if content.startswith('```'):
		assert content.endswith('```')
		lf_idx = content.find('\n')
		assert lf_idx != -1
		return content[lf_idx + 1:-3].rstrip()
	else:
		assert content.startswith('def ')
		assert content.endswith('return l')
		return content

def check_responses(
	responses: list[str],
	check_cb: Callable[[int, list[bool | CheckSatResult]], tuple[int, int, int, int]],
):
	correct = 0
	wrong = 0
	llm_failed = 0
	z3_failed = 0
	total = 0

	for i, response in enumerate(responses):
		execute_result = execute_code(response)
		if execute_result[0] == False:
			llm_failed += 1
			total += 1
			print(execute_result[1])
			continue
		else:
			results = execute_result[1]
			c, w, f, t = check_cb(i, results)
			correct += c
			wrong += w
			z3_failed += f
			total += t

	return correct, wrong, llm_failed, z3_failed, total
