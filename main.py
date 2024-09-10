from typing import TYPE_CHECKING

def request():
	# from dataset_utils.proofwriter import generate_prompts
	from llm_utils.openai_request import generate_batch, submit_batch
	from dataset_utils.reveal import generate_prompts

	prompts, ids = generate_prompts(
		filter=lambda record: record['dataset'] == 'strategy_qa',
		return_ids=True,
	)
	if TYPE_CHECKING:
		assert isinstance(prompts, list) # idiot pylance
		assert isinstance(ids, list) # even more idiot
	outfile = generate_batch(
		prompts,
		0, 10,
		'z3py-5-shot-v3-reveal-strategyqa-gpt4o0806',
		'gpt-4o-2024-08-06',
		custom_ids=ids,
	)
	input('Press Enter to submit batch.')
	submit_batch(outfile)

def langchain_request():
	from llm_utils.langchain_request import request_and_save, get_anthropic
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
		ids[0:10],
		prompts[0:10],
		model,
		'data/langchain_response/z3py-5-shot-v3-reveal-strategyqa-claude35sonnet-0000-0010.json',
		max_concurrency=3,
	)

def check():
	# from dataset_utils.proofwriter import check_result, parse_record
	from llm_utils.openai_response import check_batch_response
	from dataset_utils.reveal import check_result, get_reveal_data

	source = get_reveal_data(filter = lambda record: record['dataset'] == 'strategy_qa')
	source = source[0:10]

	correct, wrong, llm_failed, z3_failed, total = check_batch_response(
		'data/batch_response/z3py-5-shot-v3-reveal-strategyqa-gpt4o0806-0000-0010.jsonl',
		lambda i, results: check_result(results, source[i]),
	)
	print(f'Correct: {correct}, Wrong: {wrong}, LLM failed: {llm_failed}, Z3 failed: {z3_failed}, Total: {total}')

import logging
logging.basicConfig(level=logging.INFO)

langchain_request()
# check()
