from typing import Any, Literal

from logging import Logger, getLogger
import json

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from typing import TypedDict
	from z3 import CheckSatResult
	from z3_utils import Logic

	class Question(TypedDict):
		id: str
		question: str
		answer: bool | Literal['Unknown']

	class Entry(TypedDict):
		id: str
		theory: str
		questions: list[Question]

def parse_record(record: str) -> "Entry":
	j = json.loads(record)
	id: str = j['id']
	theory: str = j['theory']
	questions: dict[str, Any] = j['questions']

	qs: "list[Question]" = [
		{
			"id": key,
			"question": value['question'],
			"answer": value['answer'],
		}
		for key, value in questions.items()
	]

	return {
		"id": id,
		"theory": theory,
		"questions": qs,
	}

def generate_prompt(entry: "Entry"):
	return 'Theory: ' + entry['theory'] \
		+ '\n\nQuestion: Which of the following statements can be inferred from the theory?\n' \
		+ '\n'.join([
		q['id'] + '. ' + q['question']
		for q in entry['questions']
	])

def generate_prompts(
	data_path: str,
):
	with open(data_path, 'r', encoding='utf-8') as file:
		return [
			generate_prompt(parse_record(line))
			for line in file
		]

def _result_equal(
	judge_result: "bool | CheckSatResult",
	answer: "bool | Literal['Unknown']"
) -> "bool | CheckSatResult":
	from z3 import sat

	if isinstance(judge_result, bool):
		return judge_result == answer
	elif judge_result == sat:
		return answer == 'Unknown'
	else: # unsat or unknown, unsat -> contradiction, unknown -> Z3 failure
		return judge_result

def _binarize(n: int):
	return 1 if n > 0 else 0

def check_result(
	results: "list[bool | CheckSatResult]",
	data: "Entry",
	logger: Logger = getLogger(__name__),
):
	correct = 0
	wrong = 0
	failed = 0
	total = len(data['questions'])
	assert len(results) == total

	for i in range(total):
		is_equal = _result_equal(results[i], data['questions'][i]['answer'])
		if is_equal == True:
			correct += 1
		elif is_equal == False:
			logger.info('WA: Q%d: %s - %s', i, results[i], data['questions'][i]['answer'])
			wrong += 1
		else:
			logger.info('Failed: Q%d: %s', i, data['questions'][i]['answer'])
			failed += 1

	if wrong > 0:
		logger.info('Wrong answers for %s', data['id'])

	#return correct, wrong, failed, total
	return _binarize(correct), _binarize(wrong), _binarize(failed), _binarize(total)
