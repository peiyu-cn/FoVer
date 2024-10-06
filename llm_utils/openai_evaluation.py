from typing import Any, Optional

import json

def get_input_file(
	output_path: str,
	data: list[dict[str, Any]],
):
	with open(output_path, 'w', encoding='utf-8') as file:
		for entry in data:
			print(json.dumps(entry), file=file)

def _convert_slice(s: str):
	if s == ':':
		return slice(None)
	elif s.startswith(':'):
		return slice(None, int(s[1:]))
	elif s.endswith(':'):
		return slice(int(s[:-1]))
	elif ':' in s:
		splits = s.split(':')
		return slice(*[int(split) for split in splits])
	else:
		return slice(int(s))

if __name__ == '__main__':
	from argparse import ArgumentParser

	parser = ArgumentParser()
	parser.add_argument(
		'dataset',
		type=str.lower,
		choices=['folio'],
		help='The dataset to generate evaluation file for.'
	)
	parser.add_argument('data_path', type=str, help='The path to the data file.')
	parser.add_argument('output_path', type=str, help='The path to save the generated evaluation file.')
	parser.add_argument('-s', '--slice', type=_convert_slice, help='The slice of the data to use.')
	args = parser.parse_args()

	match args.dataset:
		case 'folio':
			from dataset_utils.folio import get_data
			data = get_data(args.data_path)
		case _:
			raise ValueError(f'Unsupported dataset: {args.dataset}')

	if args.slice:
		data = data[args.slice]

	get_input_file(args.output_path, data) # type: ignore # TypedDict is not a subtype of dict[str, Any]???
