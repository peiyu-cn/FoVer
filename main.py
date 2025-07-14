from typing import Any, Callable, Literal, Optional, TypeVar, ParamSpec

import asyncio
import importlib

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from dataset_utils.proofwriter import Entry
	from dataset_utils.reveal import RevealRecord

def openai_request():
	from llm_utils.openai_request import generate_batch, submit_batch
	#from dataset_utils.folio import generate_prompts
	#from dataset_utils.proofwriter import generate_prompts
	from dataset_utils.reveal import generate_prompts

	#prompts = generate_prompts('data/FOLIO/folio_v2_validation.jsonl')
	#prompts = generate_prompts('data/FOLIO/folio_v2_validation_reshuffle_2.jsonl')
	prompts, ids = generate_prompts(
		#'data/proofwriter/owa-baseline-test.jsonl',
		#'data/proofwriter/test-80.jsonl',
		#'data/proofwriter/OWA/depth-5/meta-test.jsonl',
		'data/reveal/eval/musique_test.csv',
		#filter=lambda record: record['dataset'] == 'musique',
		return_ids=True,
		#baseline=True,
	)
	outfile = generate_batch(
		prompts,
		0, 120,
		#'baseline-proofwriter-test-80-cot-gpt4o0806',
		#'z3py-3-shot-v24-reveal-musique-test-gpt4o0806',
		#'z3py-3-shot-v24-proofwriter-owa5-test-gpt4o0806',
		#'z3py-3-shot-v24-proofwriter-test-single-gpt4o0806',
		#'z3py-3-shot-v24-folio-v14-val-all-gpt4o0806',
		#'z3py-3-shot-v25-reveal-musique-gpt4o0806',
		'z3py-3-shot-v24-reveal-musique-ablation-identifier-gpt4o0806',
		'gpt-4o-2024-08-06',
		#demos_path='demos/baselines/ProofWriter_CoT.txt',
		demos_path='demos/ablations/identifier.py',
		#additional_path='demos/folio.py',
		#replace=True,
		custom_ids=ids,
		max_tokens=4096,
	)
	input('Press Enter to submit batch.')
	submit_batch(outfile)

def langchain_request():
	from llm_utils.langchain_request import request_and_save, get_anthropic, get_anthropic_api_error
	from private.apikey import anthropic_base_url, anthropic_key
	#from dataset_utils.folio import generate_prompts
	from dataset_utils.proofwriter import generate_prompts
	#from dataset_utils.reveal import generate_prompts

	model = get_anthropic(
		#'folio-train',
		'proofwriter-owa5',
		#'reveal-strategyqa',
		'claude-3-5-sonnet-20240620',
		anthropic_key,
		anthropic_base_url,
		temperature=0,
		top_p=1,
	)
	#prompts = generate_prompts('data/FOLIO/folio_v2_train.jsonl')
	prompts, ids = generate_prompts(
		'data/proofwriter/OWA/depth-5/meta-dev.jsonl',
	#	filter=lambda record: record['dataset'] == 'strategy_qa',
		return_ids=True,
	)
	prompts = prompts[0:20]
	#ids = [str(i) for i in range(20)]
	if TYPE_CHECKING:
		assert isinstance(prompts, list) # idiot pylance
		assert isinstance(ids, list) # even more idiot
	request_and_save(
		ids,
		prompts,
		model,
		#'data/langchain_response/z3py-3-shot-v23-folio-train-claude35sonnet-0000-0020.json',
		'data/langchain_response/z3py-3-shot-v24-proofwriter-owa5-claude35sonnet-0000-0020.json',
		#'data/langchain_response/z3py-3-shot-v21-reveal-strategyqa-claude35sonnet-0000-0020.json',
		prefill='def',
		max_concurrency=2,
		retry_if_exception_type=(get_anthropic_api_error(),),
	)

def anthropic_request():
	from llm_utils.anthropic_request import batch_request_async, generate_batch, submit_batch
	#from dataset_utils.folio import generate_prompts
	from dataset_utils.proofwriter import generate_prompts
	#from dataset_utils.reveal import generate_prompts

	#prompts = generate_prompts('data/FOLIO/folio_v2_validation.jsonl')
	#prompts = generate_prompts('data/FOLIO/folio_v2_validation_reshuffle_2.jsonl')
	prompts, ids = generate_prompts(
		'data/proofwriter/owa-baseline-test-80.jsonl',
		#'data/proofwriter/test-80.jsonl',
		#'data/proofwriter/OWA/depth-5/meta-test.jsonl',
		#'data/reveal/eval/musique_test.csv',
		return_ids=True,
		baseline=True,
	)
	prompts = prompts[0:120]
	#asyncio.run(batch_request_async(
	#	prompts,
	#	'claude-3-5-sonnet-20240620',
	#	#'data/anthropic_response/baseline-reveal-strategyqa-test-claude35sonnet-0000-0120.jsonl',
	#	#'data/anthropic_response/z3py-3-shot-v24-reveal-musique-test-claude35sonnet-0000-0120.jsonl',
	#	'data/anthropic_response/z3py-3-shot-v24-folio-val-claude35sonnet-0120-0220.jsonl',
	#	#demos_path='demos/baselines/reveal.txt',
	#	#additional_path='demos/folio.py',
	#	prefill='def',
	#	max_tokens=4096,
	#	max_concurrency=2,
	#))

	#return
	requests = generate_batch(
		prompts,
		0, 80,
		#'baseline-proofwriter-test-80-cot-35sonnet',
		#'baseline-folio-test-all-cot-35sonnet',
		#'z3py-3-shot-v24-proofwriter-test-80-35sonnet',
		'z3py-3-shot-v24-proofwriter-test-single-80-35sonnet',
		#'z3py-3-shot-v24-folio-v14-val-35sonnet',
		#'z3py-3-shot-v24-reveal-musique-test-35sonnet',
		'claude-3-5-sonnet-20240620',
		#demos_path='demos/baselines/ProofWriter_CoT.txt',
		#additional_path='demos/folio.py',
		#custom_ids=ids,
		prefill='def',
		max_tokens=4096,
	)
	input('Press Enter to submit batch.')
	b = submit_batch(requests)
	print(b.id)

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

def _folio(
	data_path: str = 'data/FOLIO/folio_v2_train.jsonl',
	s: Optional[slice] = None,
):
	from dataset_utils.folio import check_result, get_data
	source = get_data(data_path)
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
	#from dataset_utils.folio import check_result, get_data
	#from dataset_utils.proofwriter import check_result, get_data
	from dataset_utils.reveal import check_result, get_data

	#source = get_data('data/FOLIO/folio_v2_validation.jsonl')
	#source = get_data('data/FOLIO/folio_v2_validation_reshuffle_2.jsonl')
	#source = get_data('data/proofwriter/OWA/depth-5/meta-test.jsonl')
	#source = get_data('data/proofwriter/owa-baseline-test.jsonl')
	#source = get_data('data/proofwriter/test-80.jsonl')
	source = get_data('data/reveal/eval/strategyqa_test.csv')
	#source = source[0:120]

	correct, wrong, llm_failed, z3_failed, total = check_batch_response(
		#'data/batch_response/z3py-3-shot-v24-folio-val-gpt4o0806-0000-0203.jsonl',
		#'data/batch_response/z3py-3-shot-v24-folio-val-rr-gpt4o0806-0000-0107.jsonl',
		#'data/batch_response/z3py-3-shot-v24-folio-v14-val-all-gpt4o0806-0000-0203.jsonl',
		#'data/batch_response/z3py-3-shot-v24-proofwriter-owa5-test-gpt4o0806-0000-0120.jsonl',
		#'data/batch_response/z3py-3-shot-v24-proofwriter-test-single-gpt4o0806-0000-0120.jsonl',
		'data/batch_response/z3py-3-shot-v24-reveal-strategyqa-test-gpt4o0806-0000-0120.jsonl',
		lambda i, results: check_result(results, source[i]),
		#lambda i, results: check_result(results, source[i], allow_unknown=True),
		#use_definitions=False,
		#use_common_knowledge=False,
		sync=True,
	)
	#print([
	#	data['label']
	#	for data in source
	#])
	print(f'Correct: {correct}, Wrong: {wrong}, LLM failed: {llm_failed}, Z3 failed: {z3_failed}, Total: {total}')

def langchain_check():
	from llm_utils.langchain_response import check_langchain_response
	from dataset_utils.folio import check_result, get_data
	# from dataset_utils.proofwriter import check_result, parse_record
	#from dataset_utils.reveal import check_result, get_data

	source = get_data('data/FOLIO/folio_v2_train.jsonl')
	#source = get_data(filter = lambda record: record['dataset'] == 'strategy_qa')
	source = source[0:20]

	correct, wrong, llm_failed, z3_failed, total = check_langchain_response(
		'data/langchain_response/z3py-3-shot-v24-folio-v1-train-claude35sonnet-0000-0020.json',
		#'data/langchain_response/z3py-3-shot-v21-reveal-strategyqa-claude35sonnet-0000-0020.json',
		lambda i, results: check_result(results, source[i]),
		prefill='def',
		use_common_knowledge=False,
		#sync=True,
	)
	print(f'Correct: {correct}, Wrong: {wrong}, LLM failed: {llm_failed}, Z3 failed: {z3_failed}, Total: {total}')

def anthropic_check():
	from llm_utils.anthropic_response import check_batch_response
	#from dataset_utils.folio import check_result, get_data
	#from dataset_utils.proofwriter import check_result, get_data
	from dataset_utils.reveal import check_result, get_data

	#source = get_data('data/FOLIO/folio_v2_validation.jsonl')
	#source = get_data('data/FOLIO/folio_v2_validation_reshuffle_2.jsonl')
	#source = get_data('data/proofwriter/OWA/depth-5/meta-test.jsonl')
	#source = get_data('data/proofwriter/owa-baseline-test-80.jsonl')
	#source = get_data('data/proofwriter/test-80.jsonl')
	source = get_data('data/reveal/eval/musique_test.csv')
	#source = source[0:120]

	correct, wrong, llm_failed, z3_failed, total = check_batch_response(
		#'data/anthropic_response/z3py-3-shot-v24-folio-val-claude35sonnet-0000-0120.jsonl',
		#'data/anthropic_response/z3py-3-shot-v24-folio-val-rr-claude35sonnet-0000-0107.jsonl',
		#'data/anthropic_batch_response/z3py-3-shot-v24-folio-v14-val-35sonnet-0000-0203.jsonl',
		#'data/anthropic_response/z3py-3-shot-v24-proofwriter-owa5-test-claude35sonnet-0000-0120.jsonl',
		#'data/anthropic_batch_response/z3py-3-shot-v24-proofwriter-test-80-single-35sonnet-0000-0080.jsonl',
		#'data/anthropic_batch_response/z3py-3-shot-v24-proofwriter-test-80-35sonnet-0000-0080.jsonl',
		'data/anthropic_response/z3py-3-shot-v24-reveal-musique-test-claude35sonnet-0000-0120.jsonl',
		lambda i, results: check_result(results, source[i]),
		#lambda i, results: check_result(results, source[i], allow_unknown=True),
		#batch=True,
		prefill='def',
		#use_definitions=False,
		#use_common_knowledge=False,
		sync=True,
	)
	print(f'Correct: {correct}, Wrong: {wrong}, LLM failed: {llm_failed}, Z3 failed: {z3_failed}, Total: {total}')

def _prompt_dataset(
	dataset: Literal['folio', 'proofwriter', 'reveal'],
	data_path: str,
	split: Optional[str] = None,
) -> list[str]:
	module_name = f'dataset_utils.{dataset}'
	module = importlib.import_module(module_name)

	generate_prompts = getattr(module, 'generate_prompts')
	if dataset == 'reveal' and split:
		prompts = generate_prompts(data_path, filter = lambda record: record['dataset'] == split)
	else:
		prompts = generate_prompts(data_path)
	return prompts

if __name__ == '__main__':
	from argparse import ArgumentParser
	import logging

	parser = ArgumentParser()
	parser.add_argument('method',
		choices=[
			method.__name__
			for method in [openai_request, langchain_request, anthropic_request, openai_check, langchain_check, anthropic_check]
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

	exit(0)

if False:
	def _get_keys(parser: ArgumentParser):
		return {action.dest for action in parser._actions if action.dest != 'help'}

	parser = ArgumentParser()

	parser.add_argument('provider',
		choices=['openai', 'langchain', 'anthropic'],
		help='provider to use',
	)
	parser.add_argument('dataset',
		choices=['folio', 'proofwriter', 'reveal'],
		type=str.lower,
		help='dataset to use',
	)
	parser.add_argument('--split',
		help='split to use for reveal dataset',
		nargs=1,
	)
	parser.add_argument('slice',
		type = lambda s: tuple(map(int, s.split(','))),
		help = 'start,end',
	)
	parser.add_argument('-l', '--log-level',
		choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
		type=str.upper,
		help='set log level', default='INFO',
	)

	subparsers = parser.add_subparsers(
		dest='method',
		help='method to run',
	)
	request_parser = subparsers.add_parser('request', help='run request')
	check_parser = subparsers.add_parser('check', help='run check', prefix_chars='+-')

	request_parser.add_argument('model_name',
		help='model to use',
	)
	request_parser.add_argument('data_path',
		help='data path',
	)
	request_parser.add_argument('-M', '--max-tokens',
		type=int,
		default=2048,
		help='max tokens',
	)
	request_parser.add_argument('args', nargs='*', help='method arguments')

	check_parser.add_argument('-s', '--sync',
		action='store_true',
		help='check synchronously',
	)
	check_parser.add_argument('-D',
		dest='use_definitions',
		action='store_false',
		help='disable definitions',
	)
	check_parser.add_argument('-C',
		dest = 'use_common_knowledge',
		action = 'store_false',
		help = 'disable common knowledge',
	)
	check_parser.add_argument('+U',
		dest='allow_unknown',
		action='store_true',
		help='allow unknown',
	)
	args = parser.parse_args()
	print(args)
	k_main = _get_keys(parser)
	k_request = _get_keys(request_parser)
	k_check = _get_keys(check_parser)
	print(k_main, k_request, k_check)
	exit()

	if args.log_level:
		logging.basicConfig(level=args.log_level.upper())

	assert args.method and args.provider and args.dataset, 'method, provider, and dataset are required'

	method = f'{args.provider}_{args.method}'

	match args.method:
		case 'request':
			assert args.model_name, 'model_name is required'
			

	def _convert_value(value: str):
		if value.lower() in {'true', 'false'}:
			return value.lower() == 'true'
		try:
			return int(value)
		except ValueError:
			return value

	pargs: list = []
	kwargs: dict[str, Any] = {}
	for arg in args.args:
		if '=' in arg:
			key, value = arg.split('=', 1)
			kwargs[key] = _convert_value(value)
		else:
			pargs.append(_convert_value(arg))
	globals()[method](*pargs, **kwargs)
