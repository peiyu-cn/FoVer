from typing import Any, Coroutine, Optional

import anthropic
import asyncio
from tqdm.auto import tqdm

from file_utils import set_file_read_only
from .prompting import get_demos

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from typing import Sequence, Iterable

	from anthropic.types.beta.prompt_caching import PromptCachingBetaMessage, PromptCachingBetaMessageParam, PromptCachingBetaTextBlockParam

	from .prompting import Message

def _get_anthropic_messages(
	demos: "Sequence[Sequence[Message]]",
) -> "list[PromptCachingBetaMessageParam]":
	messages: "Sequence[Message]" = []

	for message_pair in demos:
		for message in message_pair:
			messages.append(message)

	last = messages[-1]

	assert last["role"] == 'assistant'
	_content = last["content"]
	assert isinstance(_content, str)
	content: "PromptCachingBetaTextBlockParam" = {
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

async def batch_request_async(
	user_prompts: "Sequence[str]",
	model: str,
	output_file: str,
	additional_path: Optional[str] = None,
	max_tokens: int = 2048,
	temperature: float = 0,
	top_p: float = 1,
	prefill: Optional[str] = None,
	max_concurrency: int = 2,
	**kwargs,
):
	from private.apikey import anthropic_key, anthropic_base_url

	system, messages = get_demos(additional_path=additional_path)
	msgs = _get_anthropic_messages(messages)
	prompts: "list[list[PromptCachingBetaMessageParam]]" = []
	for user in user_prompts:
		prompt: "list[PromptCachingBetaMessageParam]" = [
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

	client = anthropic.AsyncAnthropic(
		api_key=anthropic_key.get_secret_value(),
		base_url=anthropic_base_url,
		max_retries=3,
	)

	coros: "list[Coroutine[Any, Any, PromptCachingBetaMessage]]" = [
		client.beta.prompt_caching.messages.create(
			max_tokens=max_tokens,
			messages=message,
			model=model,
			system=system,
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
