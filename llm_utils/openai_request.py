from typing import Any, Callable, Dict, Iterable, List, Literal, Optional, Sequence, Tuple, TypedDict, Union, Unpack
from typing import TypeVar

import json
from openai import OpenAI

from .prompting import get_demos, get_messages

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from typing_extensions import NotRequired
	import httpx
	from openai._types import NOT_GIVEN, Body, Query, Headers, NotGiven
	from openai.types.chat import completion_create_params
	from openai.types.chat_model import ChatModel
	from openai.types.chat.chat_completion_tool_param import ChatCompletionToolParam
	from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
	from openai.types.chat.chat_completion_stream_options_param import ChatCompletionStreamOptionsParam
	from openai.types.chat.chat_completion_tool_choice_option_param import ChatCompletionToolChoiceOptionParam

	class OpenAIRequestBody(TypedDict):
		messages: Iterable[ChatCompletionMessageParam]
		model: Union[str, ChatModel]
		frequency_penalty: NotRequired[float]
		function_call: NotRequired[completion_create_params.FunctionCall]
		functions: NotRequired[Iterable[completion_create_params.Function]]
		logit_bias: NotRequired[Dict[str, int]]
		logprobs: NotRequired[bool]
		max_tokens: NotRequired[int]
		n: NotRequired[int]
		presence_penalty: NotRequired[float]
		response_format: NotRequired[completion_create_params.ResponseFormat]
		seed: NotRequired[int]
		stop: NotRequired[Union[Optional[str], List[str]]]
		stream: NotRequired[Literal[False]]
		stream_options: NotRequired[ChatCompletionStreamOptionsParam]
		temperature: NotRequired[float]
		tool_choice: NotRequired[ChatCompletionToolChoiceOptionParam]
		tools: NotRequired[Iterable[ChatCompletionToolParam]]
		top_logprobs: NotRequired[int]
		top_p: NotRequired[float]
		user: NotRequired[str]
		# Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs
		# The extra values given here take precedence over values defined on the client or passed to this method
		extra_headers: NotRequired[Optional[Headers]]
		extra_query: NotRequired[Optional[Query]]
		extra_body: NotRequired[Optional[Body]]
		timeout: NotRequired[Optional[float | httpx.Timeout]]

	class OpenAIRequest(TypedDict):
		custom_id: str
		method: Literal['POST']
		url: str
		body: OpenAIRequestBody

def _get_openai_messages(
	system: str,
	msgs: "Sequence[ChatCompletionMessageParam]",
) -> "Iterable[ChatCompletionMessageParam]":
	return [
		{
			"role": "system",
			"content": system
		},
		*msgs
	]

def get_openai_request_body(
	messages: "Iterable[ChatCompletionMessageParam]",
	model: str = 'gpt-4o-2024-08-06',
	**kwargs: "Unpack[OpenAIRequestBody]", # type: ignore
) -> "OpenAIRequestBody":
	return {
		"model": model,
		"messages": messages,
		**kwargs,
	}

def get_requests(
	job_prefix: str,
	bodies: "list[OpenAIRequestBody]",
	custom_ids: Optional[Sequence[str]] = None,
	base_id = 0,
	endpoint = '/v1/chat/completions',
) -> "list[OpenAIRequest]":
	if custom_ids:
		assert len(custom_ids) == len(bodies)
		prefixes = [
			f"{job_prefix}-{i + base_id :04}({custom_id})"
			for i, custom_id in enumerate(custom_ids)
		]
	else:
		prefixes = [f"{job_prefix}-{i + base_id :04}" for i in range(len(bodies))]
	return [
		{
			"custom_id": prefixes[i],
			"method": "POST",
			"url": endpoint,
			"body": bodies[i],
		} for i in range(len(bodies))
	]

def generate_batch(
	user_prompts: list[str],
	base_id: int,
	size: int,
	job_prefix: str,
	model_name = 'gpt-4o-2024-08-06',
	demos_path = 'demos/common.py',
	additional_path: Optional[str] = None,
	custom_ids: Optional[Sequence[str]] = None,
	endpoint = '/v1/chat/completions',
	max_tokens = 2048,
	temperature = 0,
	top_p = 1,
):
	demos = get_demos(demos_path, additional_path)
	system, _demos = demos

	bodies: "list[OpenAIRequestBody]" = []

	for user in user_prompts:
		messages: "Sequence[ChatCompletionMessageParam]" = get_messages(_demos, user) # type: ignore
		openai_messages = _get_openai_messages(system, messages)
		request_body = get_openai_request_body(
			openai_messages,
			model_name,
			max_tokens=max_tokens,
			temperature=temperature,
			top_p=top_p,
		)
		bodies.append(request_body)

	top = base_id + size
	requests = get_requests(job_prefix, bodies[base_id:top], custom_ids[base_id:top] if custom_ids else None, base_id, endpoint)

	outfile = f'data/batch_request/{job_prefix}-{base_id:04}-{top:04}.jsonl'
	with open(outfile, 'w', encoding='utf-8') as file:
		for request in requests:
			print(json.dumps(request), file=file)

	return outfile

def submit_batch(
	outfile: str,
	endpoint: "Literal['/v1/chat/completions', '/v1/embeddings', '/v1/completions']" = '/v1/chat/completions',
):
	from private.apikey import openai_base_url, openai_key

	client = OpenAI(
		api_key=openai_key.get_secret_value(),
		base_url=openai_base_url,
	)

	batch_file = client.files.create(
		purpose='batch',
		file=open(outfile, 'rb'),
	)

	return client.batches.create(
		endpoint=endpoint,
		input_file_id=batch_file.id,
		completion_window='24h',
	)
