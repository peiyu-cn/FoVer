from typing import Any, Callable, Tuple

from z3 import * # type: ignore

def verify(s: Solver, expr):
	assert s.check() == sat # sanity check

	r1 = s.check(expr)
	r2 = s.check(Not(expr))

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
	def __init__(self, use_common_knowledge=False, **kwargs):
		self.s = Solver(**kwargs)
		self.use_common_knowledge = use_common_knowledge
		self._added = False

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
	def claims(self) -> list[Tuple[Any, str]]:
		"""
		Claims included in the text.
		"""
		return self._claims

	@claims.setter
	def claims(self, value: list[Tuple[Any, str]]):
		self._claims = value

	@property
	def common_knowledge(self) -> list[Tuple[Any, str]]:
		"""
		World knowledge that are assumed to be true and that support the assertion.
		"""
		return self._common_knowledge

	@common_knowledge.setter
	def common_knowledge(self, value: list[Tuple[Any, str]]):
		self._common_knowledge = value

	@property
	def assertions(self) -> list[Tuple[BoolRef, str]]:
		"""
		Target conclusions to be verified.
		"""
		raise NotImplementedError

	def _add(self) -> None:
		"""
		Add the premises to the solver.
		"""
		if not self._added:
			self._add2(self.definations)
			self._add2(self.claims)
			if self.use_common_knowledge:
				self._add2(self.common_knowledge)
			self._added = True

	def _add2(self, exprs: list[Tuple[Any, str]]) -> None:
		self.s.add([expr for expr, _ in exprs])

	def verify(self):
		"""
		Verify the assertion.
		"""
		self._add()
		return [
			verify(self.s, expr)
			for expr, _ in self.assertions
		]

	def judge(self):
		"""
		Judge the assertion.
		"""
		return [
			judge(r1, r2)
			for r1, r2 in self.verify()
		]

	def to_conjuction(self):
		"""
		Get all added expressions in the solver as a conjunction.
		"""
		self._add()
		return And(*self.s.assertions())

	def simplify(self):
		"""
		Simplify the premises.
		"""
		return simplify(self.to_conjuction())

	def solve(self):
		"""
		Solve the premises.
		"""
		return solve(self.to_conjuction())

class Logic(LogicBase):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

	@property
	def assertions(self) -> list[Tuple[BoolRef, str]]:
		return self._assertions

	@assertions.setter
	def assertions(self, value: list[Tuple[Any, str]]):
		self._assertions = value

class QALogic(LogicBase):
	def __init__(self, use_common_knowledge=False, **kwargs):
		super().__init__(use_common_knowledge, **kwargs)

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
	
	#@property
	#def assertion(self): # TODO
	#	return self.question(self.answer)
