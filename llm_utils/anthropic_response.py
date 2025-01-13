from typing import Callable, Optional

import json

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from z3.z3 import CheckSatResult

def get_assistant_content(result: str, prefill: Optional[str] = None):
	j = json.loads(result)
	content: list[dict] = j['content']
	assert len(content) == 1
	text: str = content[0]['text']
	if prefill:
		text = prefill + text
	return text

def get_assistant_batch_content(
	result: str,
	prefill: Optional[str] = None,
) -> str:
	j = json.loads(result)
	_result: dict = j['result']
	message: dict = _result['message']
	content: list[dict] = message['content']
	assert len(content) == 1
	text: str = content[0]['text']
	if prefill:
		text = prefill + text
	return text

def check_batch_response(
	response_file_path: str,
	check_cb: "Callable[[int, list[bool | CheckSatResult]], tuple[int, int, int, int]]",
	batch: bool = False,
	prefill: Optional[str] = None,
	use_definitions: bool = True,
	use_common_knowledge: bool = True,
	sync: bool = False,
):
	from .response import process_response, check_responses

	get_content = get_assistant_batch_content if batch else get_assistant_content

	with open(response_file_path, 'r', encoding='utf-8') as file:
		responses = [
			process_response(get_content(line, prefill))
			for line in file
		]
	return check_responses(responses, check_cb, use_definitions, use_common_knowledge, sync)
