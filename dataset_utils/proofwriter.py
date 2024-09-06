from typing import Any

import json

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from typing import TypedDict

	class Question(TypedDict):
		id: str
		question: str
		answer: bool

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
