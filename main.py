from dataset_utils.proofwriter import generate_prompts
from llm_utils.openai_request import generate_batch, submit_batch

prompts = generate_prompts('data/proofwriter/OWA/NatLang/meta-dev.jsonl')
outfile = generate_batch(
	prompts,
	0, 10,
	'z3py-5-shot-v3-proofwriter',
	'gpt-4o-2024-08-06',
)
input('Press Enter to submit batch.')
submit_batch(outfile)
