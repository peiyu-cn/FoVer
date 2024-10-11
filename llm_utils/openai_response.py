from typing import Callable, Literal

import json
from z3 import CheckSatResult

from .response import process_response, check_responses

def get_assistant_content(result: str):
	j = json.loads(result)
	choices: list[dict] = j['response']['body']['choices']
	assert len(choices) == 1
	message: dict[str, str] = choices[0]['message']
	assert message['role'] == 'assistant'
	content = message['content']
	return content

def check_batch_response(
	response_file_path: str,
	check_cb: Callable[[int, list[bool | CheckSatResult]], tuple[int, int, int, int]],
	use_definitions: bool = True,
	use_common_knowledge: bool = True,
	sync: bool = False,
):
	with open(response_file_path, 'r', encoding='utf-8') as file:
		responses = [
			process_response(get_assistant_content(line))
			for line in file
		]
	return check_responses(responses, check_cb, use_definitions, use_common_knowledge, sync)
