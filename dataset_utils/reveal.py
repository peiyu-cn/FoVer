from typing import Any, Literal, Sequence, TypedDict

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
):
	return [
		generate_prompt(record)
		for record in get_reveal_data(data_path)
	]
