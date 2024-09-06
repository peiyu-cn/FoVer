from typing import Callable, Literal

import json
from z3 import CheckSatResult

from .execute import process_response, execute_code

def get_assistant_content(result: str):
	j = json.loads(result)
	choices: list[dict] = j['response']['body']['choices']
	assert len(choices) == 1
	message: dict[str, str] = choices[0]['message']
	assert message['role'] == 'assistant'
	content = message['content']
	return process_response(content)

def check_batch_response(
	response_file_path: str,
	check_cb: Callable[[int, list[bool | CheckSatResult]], tuple[int, int, int, int]],
):
	with open(response_file_path, 'r', encoding='utf-8') as file:
		responses = [
			get_assistant_content(line)
			for line in file
		]

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
