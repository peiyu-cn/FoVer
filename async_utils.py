from typing import Awaitable, Callable, Generic, ParamSpec, TypeVar

T = TypeVar('T')
P = ParamSpec('P')

class SyncAwaitable(Awaitable[T], Generic[P, T]):
	"""
	An awaitable object that runs a synchronous task.
	"""
	def __init__(self, task: Callable[P, T], *args: P.args, **kwargs: P.kwargs):
		self._task = task
		self._args = args
		self._kwargs = kwargs

	def __await__(self):
		yield
		return self._task(*self._args, **self._kwargs)
