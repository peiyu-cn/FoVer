from typing import Any
from uuid import UUID
from tqdm.auto import tqdm

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult

class BatchCallback(BaseCallbackHandler):
	def __init__(self, total: int, minus_on_chain_error=False):
		super().__init__()
		self.progress_bar = tqdm(total=total)
		if minus_on_chain_error:
			self.on_chain_error = self.__on_chain_error

	def on_llm_end(self, response: LLMResult, *, run_id: UUID, parent_run_id: UUID | None = None, **kwargs: Any) -> Any:
		self.progress_bar.update(1)

	def __on_chain_error(self, error: BaseException, *, run_id: UUID, parent_run_id: UUID | None = None, **kwargs: Any) -> Any:
		if parent_run_id is None:
			self.progress_bar.update(-1)

	def __enter__(self):
		self.progress_bar.__enter__()
		return self
	
	def __exit__(self, exc_type, exc_value, exc_traceback):
		self.progress_bar.__exit__(exc_type, exc_value, exc_traceback)

	def __del__(self):
		self.progress_bar.__del__()
