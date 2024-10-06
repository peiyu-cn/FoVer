from typing import Any, Literal, TypedDict

import json
from logging import Logger, getLogger

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from z3.z3 import CheckSatResult

	Label = Literal['True', 'False', 'Uncertain']

class Entry(TypedDict):
	story_id: int
	example_id: int
	premises: str
	conclusion: str
	label: "Label"

def convert_label(label: "Label"):
	from z3.z3 import sat
	match label:
		case 'True':
			return True
		case 'False':
			return False
		case 'Uncertain':
			return sat

def get_data(
	data_path='data/FOLIO/folio_v2_train.jsonl',
) -> "list[Entry]":
	with open(data_path, 'r', encoding='utf-8') as file:
		return [
			parse_record(line)
			for line in file
		]

def parse_record(record: str) -> Entry:
	j = json.loads(record)
	return { # type: ignore # idiot Pylance
		k: j[k]
		for k in Entry.__annotations__.keys()
	}

def generate_prompt(entry: Entry):
	return 'Premises:\n' + entry['premises'] + '\n\nConclusion: ' + entry['conclusion'] + \
		'\n(Simple case does not need complex predicates and common knowledge apart from distinction and equivalence.)'

def generate_prompts(
	data_path='data/FOLIO/folio_v2_train.jsonl',
):
	data = get_data(data_path)
	return [
		generate_prompt(entry)
		for entry in data
	]

def _result_equal(
	judge_result: "bool | CheckSatResult",
	answer: "Label",
	allow_unknown: bool = False,
) -> "bool | CheckSatResult":
	from z3 import unknown

	if judge_result == unknown:
		return unknown
	return (allow_unknown and answer == 'Uncertain') or judge_result == convert_label(answer)

def check_result(
	results: "list[bool | CheckSatResult]",
	data: Entry,
	allow_unknown: bool = False,
	logger: Logger = getLogger(__name__),
) -> tuple[Literal[0, 1], Literal[0, 1], Literal[0, 1], Literal[1]]:
	from z3 import unknown

	#assert len(results) == 1, f'Multiple results: {results}'
	if len(results) != 1:
		logger.error('Multiple results: %s', results)
	result = results[0]

	is_equal = _result_equal(result, data['label'], allow_unknown=allow_unknown)
	if not isinstance(is_equal, bool):
		assert is_equal == unknown
		logger.error('Failed: %d: %s', data['example_id'], data['label'])
		return 0, 0, 1, 1
	elif is_equal:
		return 1, 0, 0, 1
	else:
		logger.warning('WA: %d: %s - %s', data['example_id'], result, data['label'])
		return 0, 1, 0, 1
