from typing import Optional, Sequence

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from typing import Literal, TypedDict
	from langchain.prompts.chat import MessageLikeRepresentation

	class Message(TypedDict):
		role: Literal['user', 'assistant']
		content: str

quote = '"""'
assis = '## Assistant:'
retur = 'return l'

def _parse_demo(
	demo: str,
) -> "Sequence[Message]":
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
	file_path = 'demos/common.py',
	additional_path: Optional[str] = None,
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

	# Get additional prompts
	if additional_path:
		with open(additional_path, 'r', encoding='utf-8') as file:
			additional_content = file.read()
		additional_demos = additional_content.split('# %% demo')
		demos.extend(additional_demos[1:])

	demos_message_pairs = [_parse_demo(demo) for demo in demos[1:]]

	return system, demos_message_pairs

def get_messages(
	msgs: "Sequence[Sequence[Message]]",
	user: str,
) -> "Sequence[Message]":
	messages: "Sequence[Message]" = []

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

def get_langchain_template(
	system: str,
	msgs: "Sequence[Sequence[Message]]",
	prefill: Optional[str] = None,
) -> "Sequence[MessageLikeRepresentation]":
	messages: "Sequence[MessageLikeRepresentation]" = []
	messages.append(('system', system)) # idiot pylance

	for message_pair in msgs:
		for message in message_pair:
			messages.append((message["role"], message["content"]))
	
	messages.append(('user', '{user}'))
	if prefill:
		messages.append(('assistant', prefill))
	return messages
