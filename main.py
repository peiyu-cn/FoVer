from typing import Callable, Literal, Optional

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from dataset_utils.proofwriter import Entry
	from dataset_utils.reveal import RevealRecord

def openai_request():
	from llm_utils.openai_request import generate_batch, submit_batch
	from dataset_utils.proofwriter import generate_prompts
	# from dataset_utils.reveal import generate_prompts

	#prompts, ids = generate_prompts(
	#	filter=lambda record: record['dataset'] == 'strategy_qa',
	#	return_ids=True,
	#)
	#if TYPE_CHECKING:
	#	assert isinstance(prompts, list) # idiot pylance
	#	assert isinstance(ids, list) # even more idiot
	prompts = generate_prompts('data/proofwriter/OWA/depth-5/meta-dev.jsonl')
	outfile = generate_batch(
		prompts,
		0, 100,
		'z3py-3-shot-v20-proofwriter-owa5-gpt4o0806',
		'gpt-4o-2024-08-06',
		#custom_ids=ids,
		max_tokens=4096,
	)
	input('Press Enter to submit batch.')
	submit_batch(outfile)

def langchain_request():
	from llm_utils.langchain_request import request_and_save, get_anthropic, get_anthropic_api_error
	from private.apikey import anthropic_base_url, anthropic_key
	from dataset_utils.reveal import generate_prompts

	model = get_anthropic(
		'reveal-strategyqa',
		'claude-3-5-sonnet-20240620',
		anthropic_key,
		anthropic_base_url,
		temperature=0,
		top_p=1,
	)
	prompts, ids = generate_prompts(
		filter=lambda record: record['dataset'] == 'strategy_qa',
		return_ids=True,
	)
	if TYPE_CHECKING:
		assert isinstance(prompts, list) # idiot pylance
		assert isinstance(ids, list) # even more idiot
	request_and_save(
		ids[0:20],
		prompts[0:20],
		model,
		'data/langchain_response/z3py-3-shot-v20-reveal-strategyqa-claude35sonnet-0000-0020.json',
		prefill='def',
		max_concurrency=2,
		retry_if_exception_type=(get_anthropic_api_error(),),
	)

def _reveal(
	data_path: str = 'data/reveal/eval/reveal_eval.csv',
	s: Optional[slice] = None,
	filter: "Optional[Callable[[RevealRecord], bool]]" = lambda record: record['dataset'] == 'strategy_qa',
):
	from dataset_utils.reveal import check_result, get_data
	source = get_data(data_path, filter=filter)
	if s:
		source = source[s]
	return source, check_result

def _proofwriter(
	data_path: str = 'data/proofwriter/OWA/depth-5/meta-dev.jsonl',
	s: Optional[slice] = None,
):
	from dataset_utils.proofwriter import check_result, get_data
	source = get_data(data_path)
	if s:
		source = source[s]
	return source, check_result

def openai_check(
	dataset: Literal['reveal', 'proofwriter'] = 'proofwriter',
	data_path: str = 'data/proofwriter/OWA/depth-5/meta-dev.jsonl',
	s: Optional[str] = None,
):
	from llm_utils.openai_response import check_batch_response
	# from dataset_utils.proofwriter import check_result, get_data
	from dataset_utils.reveal import check_result, get_data

	source = get_data(filter = lambda record: record['dataset'] == 'strategy_qa')
	source = source[0:20]
	#source = get_data('data/proofwriter/OWA/depth-5/meta-dev.jsonl')
	#source = source[0:100]

	correct, wrong, llm_failed, z3_failed, total = check_batch_response(
		'data/batch_response/z3py-3-shot-v20-reveal-strategyqa-gpt4o0806-0000-0020.jsonl',
		lambda i, results: check_result(results, source[i]),
		#'data/batch_response/z3py-3-shot-v20-proofwriter-owa5-gpt4o0806-0000-0100-2.jsonl',
		#lambda i, results: check_result(results, source[i], allow_unknown=False),
	)
	print(f'Correct: {correct}, Wrong: {wrong}, LLM failed: {llm_failed}, Z3 failed: {z3_failed}, Total: {total}')

def langchain_check():
	from llm_utils.langchain_response import check_langchain_response
	# from dataset_utils.proofwriter import check_result, parse_record
	from dataset_utils.reveal import check_result, get_data

	source = get_data(filter = lambda record: record['dataset'] == 'strategy_qa')
	source = source[0:20]

	correct, wrong, llm_failed, z3_failed, total = check_langchain_response(
		'data/langchain_response/z3py-3-shot-v20-reveal-strategyqa-claude35sonnet-0000-0020.json',
		lambda i, results: check_result(results, source[i]),
		prefill='def',
	)
	print(f'Correct: {correct}, Wrong: {wrong}, LLM failed: {llm_failed}, Z3 failed: {z3_failed}, Total: {total}')

if __name__ == '__main__':
	from argparse import ArgumentParser
	import logging

	parser = ArgumentParser()
	parser.add_argument('method',
		choices=[
			method.__name__
			for method in [openai_request, langchain_request, openai_check, langchain_check]
		],
		help='method to run')
	parser.add_argument('-l', '--log-level',
		choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
		type=str.upper,
		help='set log level', default='INFO')
	parser.add_argument('args', nargs='*', help='method arguments')
	args = parser.parse_args()

	if args.log_level:
		logging.basicConfig(level=args.log_level.upper())
	if args.method:
		positional_args: list[str] = []
		keyword_args: dict[str, str] = {}
		for arg in args.args:
			if '=' in arg:
				key, value = arg.split('=', 1)
				keyword_args[key] = value
			else:
				positional_args.append(arg)
		globals()[args.method](*positional_args, **keyword_args)
