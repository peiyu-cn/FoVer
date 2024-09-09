from typing import Any, Callable, Literal, Optional, Sequence, TypedDict

import pandas as pd

class RevealRecord(TypedDict):
	answer_id: str
	question_id: str
	dataset: str
	question: str
	full_answer: str
	answer_is_logically_correct: bool

def get_reveal_data(
	data_path: str,
) -> Sequence[RevealRecord]:
	df = pd.read_csv(data_path, encoding='utf-8')

	df = df[[k for k in RevealRecord.__annotations__.keys()]]
	df = df.drop_duplicates(['answer_id'])

	d = df.to_dict(orient='records')

	return d # type: ignore

def generate_prompt(record: RevealRecord):
	return 'Question: ' + record['question'] + '\nAnswer:\n' + record['full_answer']

def generate_prompts(
	data_path='data/reveal/eval/reveal_eval.csv',
	filter: Optional[Callable[[RevealRecord], bool]] = None,
	return_ids = False,
):
	prompts: list[str] = []
	ids: list[str] = []

	for record in get_reveal_data(data_path):
		if filter and not filter(record):
			continue
		prompts.append(generate_prompt(record))
		if return_ids:
			ids.append(record['answer_id'])

	if return_ids:
		return prompts, ids
	else:
		return prompts
