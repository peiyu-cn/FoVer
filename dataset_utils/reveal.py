from typing import Any, Callable, Literal, Optional, Sequence, TypedDict

from logging import Logger, getLogger

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from z3 import CheckSatResult

class RevealRecord(TypedDict):
	answer_id: str
	question_id: str
	dataset: str
	question: str
	full_answer: str
	answer_is_logically_correct: bool

def get_reveal_data(
	data_path = 'data/reveal/eval/reveal_eval.csv',
	filter: Optional[Callable[[RevealRecord], bool]] = None,
) -> Sequence[RevealRecord]:
	import pandas as pd

	df = pd.read_csv(data_path, encoding='utf-8')

	df = df[[k for k in RevealRecord.__annotations__.keys()]]
	df = df.drop_duplicates(['answer_id'])

	d = df.to_dict(orient='records')

	return [
		r for r in d if filter is None or filter(r) # type: ignore
	]

def generate_prompt(record: RevealRecord):
	return 'Question: ' + record['question'] + '\nAnswer:\n' + record['full_answer']

def generate_prompts(
	data_path = 'data/reveal/eval/reveal_eval.csv',
	filter: Optional[Callable[[RevealRecord], bool]] = None,
	return_ids = False,
):
	prompts: list[str] = []
	ids: list[str] = []

	for record in get_reveal_data(data_path, filter):
		prompts.append(generate_prompt(record))
		if return_ids:
			ids.append(record['answer_id'])

	if return_ids:
		return prompts, ids
	else:
		return prompts

def _result_equal(
	judge_result: "bool | CheckSatResult",
	answer: bool
) -> "bool | CheckSatResult":
	from z3 import sat, unknown

	if answer == True:
		return judge_result == True
	elif judge_result == unknown:
		return unknown
	else:
		return judge_result == False or judge_result == sat

def check_result(
	results: "list[bool | CheckSatResult]",
	data: RevealRecord,
	logger: Logger = getLogger(__name__),
) -> tuple[Literal[0, 1], Literal[0, 1], Literal[0, 1], Literal[1]]:
	from z3 import unknown

	assert len(results) == 1
	result = results[0]

	is_equal = _result_equal(result, data['answer_is_logically_correct'])
	if not isinstance(is_equal, bool):
		assert is_equal == unknown
		logger.warning('Failed: %s: %s', data['answer_id'], data['answer_is_logically_correct'])
		return 0, 0, 1, 1 # correct, wrong, failed, total
	elif is_equal:
		return 1, 0, 0, 1
	else:
		logger.warning('WA: %s: %s - %s', data['answer_id'], result, data['answer_is_logically_correct'])
		return 0, 1, 0, 1
