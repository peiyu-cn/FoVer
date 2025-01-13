from typing import Any, Coroutine, Iterable, Literal, Sequence, Optional, Unpack, overload

import anthropic
import asyncio
import json
from logging import Logger, getLogger
from tqdm.auto import tqdm

from file_utils import set_file_read_only
from .prompting import get_demos

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from typing import NotRequired

	from anthropic.types.beta.beta_message import BetaMessage
	from anthropic.types.beta.beta_message_param import BetaMessageParam
	from anthropic.types.beta.beta_text_block_param import BetaTextBlockParam
	from anthropic.types.beta.messages.batch_create_params import Request
	from anthropic.types.beta.messages.beta_message_batch_individual_response import BetaMessageBatchIndividualResponse
	from anthropic.types.beta.message_create_params import MessageCreateParamsNonStreaming

	from .prompting import Message

	class MessageCreateParameters(MessageCreateParamsNonStreaming, total=False):
		messages: NotRequired[Iterable[BetaMessageParam]] # type: ignore
		max_tokens: NotRequired[int] # type: ignore
		model: NotRequired[str] # type: ignore

def _get_anthropic_messages(
	demos: "Sequence[Sequence[Message]]",
) -> "list[BetaMessageParam]":
	messages: "Sequence[Message]" = []

	for message_pair in demos:
		for message in message_pair:
			messages.append(message)

	if len(messages) == 0:
		return []

	last = messages[-1]

	assert last["role"] == 'assistant'
	_content = last["content"]
	assert isinstance(_content, str)
	content: "BetaTextBlockParam" = {
		"type": 'text',
		"text": _content,
		"cache_control": {
			"type": 'ephemeral'
		}
	}

	return [
		*messages[:-1], # type: ignore
		{
			"role": 'assistant',
			"content": [content]
		}
	]

@overload
def _get_anthropic_client(
	use_cache: bool = True,
	max_retries: int = 3,
) -> anthropic.Anthropic:
	...

@overload
def _get_anthropic_client(
	use_cache: bool = True,
	max_retries: int = 3,
	*,
	asynchronous: Literal[True],
) -> anthropic.AsyncAnthropic:
	...

def _get_anthropic_client(
	use_cache=True,
	max_retries=3,
	*,
	asynchronous=False,
):
	from private.apikey import anthropic_key, anthropic_base_url, anthropic_base_url_nocache
	base_url = anthropic_base_url if use_cache else anthropic_base_url_nocache
	Ant = anthropic.Anthropic if not asynchronous else anthropic.AsyncAnthropic
	return Ant(
		api_key=anthropic_key.get_secret_value(),
		base_url=base_url,
		max_retries=max_retries,
	)

def get_requests(
	job_prefix: str,
	params: "list[MessageCreateParamsNonStreaming]",
	custom_ids: Optional[Sequence[str]] = None,
	base_id = 0,
) -> "list[Request]":
	l = len(params)
	if custom_ids:
		assert len(custom_ids) == l
		prefixes = [
			f"{job_prefix}-{i + base_id :04}({custom_id})"
			for i, custom_id in enumerate(custom_ids)
		]
	else:
		prefixes = [f"{job_prefix}-{i + base_id :04}" for i in range(l)]
	return [
		{
			"custom_id": prefixes[i],
			"params": params[i],
		} for i in range(l)
	]

def get_prompts(
	user_prompts: "Sequence[str]",
	msgs: "Sequence[BetaMessageParam]",
	prefill: Optional[str] = None,
):
	prompts: "list[list[BetaMessageParam]]" = []
	for user in user_prompts:
		prompt: "list[BetaMessageParam]" = [
			*msgs,
			{
				"role": 'user',
				"content": user
			}
		]
		if prefill:
			prompt.append({
				"role": 'assistant',
				"content": prefill
			})
		prompts.append(prompt)

	return prompts

def generate_batch(
	user_prompts: "Sequence[str]",
	base_id: int,
	size: int,
	job_prefix: str,
	model: Literal['claude-3-5-sonnet-20240620'],
	demos_path = 'demos/common.py',
	additional_path: Optional[str] = None,
	replace: bool = False,
	custom_ids: Optional[Sequence[str]] = None,
	prefill: Optional[str] = None,
	max_tokens: int = 2048,
	temperature: float = 0,
	top_p: float = 1,
	**kwargs: "Unpack[MessageCreateParameters]", # type: ignore
):
	system, messages = get_demos(file_path=demos_path, additional_path=additional_path, replace=replace)
	msgs = _get_anthropic_messages(messages)
	prompts = get_prompts(user_prompts, msgs, prefill)

	top = base_id + min(size, len(prompts) - base_id)
	requests = get_requests(
		job_prefix = job_prefix,
		custom_ids = custom_ids[base_id:top] if custom_ids else None,
		base_id = base_id,
		params = [
			{
				"model": model,
				"system": [
					{
						"type": 'text',
						"text": system,
						"cache_control": {
							"type": 'ephemeral'
						},
					}
				],
				"messages": prompt,
				"max_tokens": max_tokens,
				"temperature": temperature,
				"top_p": top_p,
				**kwargs,
			}
			for prompt in prompts[base_id:top]
		],
	)

	outfile = f'data/anthropic_batch_request/{job_prefix}-{base_id:04}-{top:04}.jsonl'
	with open(outfile, 'w', encoding='utf-8') as file:
		for request in requests:
			print(json.dumps(request), file=file)

	set_file_read_only(outfile)
	return requests

def submit_batch(
	requests: "list[Request]",
):
	client = _get_anthropic_client(use_cache=False)

	return client.beta.messages.batches.create(
		requests=requests,
		betas=['prompt-caching-2024-07-31'],
	)

def list_batch():
	client = _get_anthropic_client(use_cache=False)
	return client.beta.messages.batches.list()

def check_batch(
	batch_id: str,
):
	client = _get_anthropic_client(use_cache=False)
	r = client.beta.messages.batches.retrieve(batch_id)
	return r.processing_status

def save_batch_results(
	batch_id: str,
	output_file: str,
):
	client = _get_anthropic_client(use_cache=False)
	r = client.beta.messages.batches.retrieve(batch_id)
	assert r.processing_status == 'ended', f'Status: {r.processing_status}'
	_results = client.beta.messages.batches.results(batch_id)
	results = list(_results)
	results.sort(key = lambda r: r.custom_id)
	with open(output_file, 'w', encoding='utf-8') as file:
		for result in results:
			print(result.to_json(indent=None), file=file)

async def batch_request_async(
	user_prompts: "Sequence[str]",
	model: str,
	output_file: str,
	demos_path = 'demos/common.py',
	additional_path: Optional[str] = None,
	replace: bool = False,
	max_tokens: int = 2048,
	temperature: float = 0,
	top_p: float = 1,
	prefill: Optional[str] = None,
	max_concurrency: int = 2,
	**kwargs,
):
	system, messages = get_demos(file_path=demos_path, additional_path=additional_path, replace=replace)
	msgs = _get_anthropic_messages(messages)
	prompts = get_prompts(user_prompts, msgs, prefill)

	client = _get_anthropic_client(asynchronous=True)

	coros: "list[Coroutine[Any, Any, BetaMessage]]" = [
		client.beta.messages.create(
			max_tokens=max_tokens,
			messages=message,
			model=model,
			system=[{
				"type": 'text',
				"text": system,
				"cache_control": {
					"type": 'ephemeral'
				},
			}],
			temperature=temperature,
			top_p=top_p,
			**kwargs
		)
		for message in prompts
	]

	results = []

	with open(output_file, 'w', encoding='utf-8') as file, tqdm(total=len(prompts)) as pbar:
		r0 = await coros[0]
		pbar.update()
		results.append(r0)
		print(r0.to_json(indent=None), file=file)
		for i in range(1, len(prompts), max_concurrency):
			tasks = [
				asyncio.create_task(coros[j])
				for j in range(i, min(i + max_concurrency, len(prompts)))
			]
			for task in tasks:
				result = await task
				pbar.update()
				results.append(result)
				print(result.to_json(indent=None), file=file)

	set_file_read_only(output_file)
	return results
