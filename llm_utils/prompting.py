from typing import Sequence, Any

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from anthropic.types.message_param import MessageParam
	from openai.types.chat import ChatCompletionMessageParam

quote = '"""'
assis = '## Assistant:'
retur = 'return l'

def _parse_demo(
	demo: str,
) -> "Sequence[MessageParam]":
	user_idx = demo.find('## User:')
	assistant_idx = demo.find(assis)
	user_text = demo[user_idx:assistant_idx]
	assistant_text = demo[assistant_idx:]

	quote_idx1 = user_text.find(quote)
	quote_idx2 = user_text.find(quote, quote_idx1 + len(quote))
	user = user_text[quote_idx1 + len(quote) : quote_idx2].strip()

	rest = assistant_text[len(assis):]
	return_idx = rest.find(retur)
	assistant = rest[:return_idx + len(retur) + 2].lstrip()

	return [
		{
			"role": "user",
			"content": user
		},
		{
			"role": "assistant",
			"content": assistant
		}
	]

def get_demos(
	file_path = 'demos.py',
):
	# Read the file
	with open(file_path, 'r', encoding='utf-8') as file:
		content = file.read()

	# Get system
	system_idx = content.find('# %% System:')
	rest = content[system_idx:]
	quote_idx1 = rest.find(quote)
	quote_idx2 = rest.find(quote, quote_idx1 + len(quote))
	system = rest[quote_idx1 + len(quote) : quote_idx2]

	# Get prompts
	demos = rest.split('# %% demo')
	demos_message_pairs = [_parse_demo(demo) for demo in demos[1:]]

	return system, demos_message_pairs

def get_messages(
	msgs: "Sequence[Sequence[MessageParam]]",
	user: str,
) -> "Sequence[MessageParam]":
	messages: "Sequence[MessageParam]" = []

	for message_pair in msgs:
		for message in message_pair:
			messages.append(message)

	messages.append(
		{
			"role": "user",
			"content": user
		}
	)

	return messages
