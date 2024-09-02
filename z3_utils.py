from typing import Any, Callable, Tuple

from z3 import Solver, CheckSatResult, sat, unsat, unknown, Not, BoolRef, SortRef

def verify(s: Solver, expr):
	assert s.check(expr) == sat # sanity check

	s.push()
	s.add(expr)
	r1 = s.check()
	s.pop()

	s.push()
	s.add(Not(expr))
	r2 = s.check()
	s.pop()

	return r1, r2

def judge(r1: CheckSatResult, r2: CheckSatResult) -> bool | CheckSatResult:
	if r1 == sat:
		if r2 == sat:
			return sat
		elif r2 == unsat:
			return True
		else:
			return unknown
	elif r1 == unsat:
		if r2 == sat:
			return False
		elif r2 == unsat:
			return unsat
		else:
			return unknown
	else:
		return unknown

class LogicBase:
	def __init__(self, context=None):
		self.s = Solver(ctx=context)
		self._added = False

	@property
	def claims(self) -> list[Tuple[Any, str]]:
		"""
		Claims included in the text.
		"""
		return self._claims

	@claims.setter
	def claims(self, value: list[Tuple[Any, str]]):
		self._claims = value

	@property
	def assumptions(self) -> list[Tuple[Any, str]]:
		"""
		Unstated assumptions that are necessary to the assertion.
		"""
		return self._assumptions

	@assumptions.setter
	def assumptions(self, value: list[Tuple[Any, str]]):
		self._assumptions = value

	@property
	def assertion(self) -> BoolRef:
		"""
		Target conclusion to be verified.
		"""
		raise NotImplementedError

	def _add(self) -> None:
		"""
		Add the premises to the solver.
		"""
		if not self._added:
			self.__add(self.claims)
			self.__add(self.assumptions)
			self._added = True

	def __add(self, exprs: list[Tuple[Any, str]]) -> None:
		self.s.add([expr for expr, _ in exprs])

	def verify(self):
		"""
		Verify the assertion.
		"""
		self._add()
		return verify(self.s, self.assertion)

	def judge(self):
		"""
		Judge the assertion.
		"""
		return judge(*self.verify())

class Logic(LogicBase):
	def __init__(self, context=None):
		super().__init__(context)

	@property
	def assertion(self):
		return self._assertion

	@assertion.setter
	def assertion(self, value: BoolRef):
		self._assertion = value

class QALogic(LogicBase):
	def __init__(self, context=None):
		super().__init__(context)

	@property
	def definations(self):
		"""
		Definations of defined relations.
		"""
		return self._definations

	@definations.setter
	def definations(self, value: list[Tuple[Any, str]]):
		self._definations = value

	@property
	def answer(self):
		"""
		Answer term of the question.
		"""
		return self._answer

	@answer.setter
	def answer(self, value):
		self._answer = value

	@property
	def answer_type(self) -> SortRef:
		"""
		Type of the answer term.
		"""
		return self._answer_type

	@answer_type.setter
	def answer_type(self, value: SortRef):
		self._answer_type = value

	@property
	def question(self) -> Callable[[Any], BoolRef]:
		"""
		Target question.
		"""
		return self._question

	@question.setter
	def question(self, value):
		self._question = value
	
	@property
	def assertion(self):
		return self.question(self.answer)

	def _add(self):
		if not self._added:
			self.__add(self.definations)
			self.__add(self.claims)
			self.__add(self.assumptions)
			self._added = True
