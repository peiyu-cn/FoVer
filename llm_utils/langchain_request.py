from typing import Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.language_models import BaseChatModel

from .prompting import get_demos, get_langchain_template
from .langchain_utils import BatchCallback

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from pydantic.v1.types import SecretStr

def batch_request(
	user_prompts: list[str],
	model: BaseChatModel,
	max_concurrency: int = 8,
	**retry_kwargs,
):
	system, messages = get_demos()
	msgs = get_langchain_template(system, messages)

	chain = ChatPromptTemplate.from_messages(msgs) | model | StrOutputParser()
	chain = chain.with_retry(**retry_kwargs)

	with BatchCallback(len(user_prompts)) as callback:
		return chain.batch([
			{ "user": user }
			for user in user_prompts
		], config={
			"max_concurrency": max_concurrency,
			"callbacks": [callback],
		})

def request_and_save(
	custom_ids: list[str],
	user_prompts: list[str],
	model: BaseChatModel,
	output_file: str,
	max_concurrency: int = 8,
	**retry_kwargs,
):
	import json

	assert len(custom_ids) == len(user_prompts)
	responses = batch_request(user_prompts, model, max_concurrency, **retry_kwargs)
	with open(output_file, 'w', encoding='utf-8') as file:
		json.dump([
			{
				"id": custom_id,
				"response": response if isinstance(response, str) else {
					"type": response.__class__.__name__,
					"fields": vars(response),
				}
			}
			for custom_id, response in zip(custom_ids, responses)
		], file, ensure_ascii=False, indent=0)

def get_anthropic(
	task_id: str,
	model_name: str,
	api_key: "SecretStr",
	base_url: Optional[str] = None,
	streaming: bool = False,
	temperature: float = 0,
	top_p: float = 1,
	**kwargs,
):
	from langchain_anthropic import ChatAnthropic
	from langchain_community.cache import SQLiteCache

	return ChatAnthropic(
		model_name=model_name,
		api_key=api_key,
		base_url=base_url,
		streaming=streaming,
		temperature=temperature,
		top_p=top_p,
		cache=SQLiteCache(f'cache/{model_name}-{task_id}.db'),
		**kwargs,
	)
