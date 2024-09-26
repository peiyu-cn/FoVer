from typing import Any, Callable, Literal, Tuple
from typing_extensions import deprecated

from logging import Logger, getLogger
from z3.z3 import * # type: ignore

from typing import TYPE_CHECKING

def verify(s: Solver, expr):
	assert s.check() == sat, 'Paradox premises.' # sanity check

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

Expr = (
	PatternRef | QuantifierRef | BoolRef | IntNumRef | ArithRef | RatNumRef |
	AlgebraicNumRef | BitVecNumRef | BitVecRef | ArrayRef | DatatypeRef |
	FPNumRef | FPRef | FiniteDomainNumRef | FiniteDomainRef | FPRMRef | SeqRef | CharRef | ReRef | ExprRef
)

class LogicBase:
	def __init__(self,
		use_common_knowledge = True,
		translate = False,
		logger: Logger = getLogger(__name__),
		**kwargs
	):
		self.context = kwargs.get("context", None)# or Context()
		# kwargs["ctx"] = self.context
		self.s = Solver(**kwargs)
		self.use_common_knowledge = use_common_knowledge
		if not translate:
			self._switch_context = lambda exprs: exprs
		self._logger = logger
		self._added = False

	def _preprocess(self,
		property_name: Literal['definitions', 'claims', 'common_knowledge', 'assertions'],
		exprs: list[Tuple[Expr, str]]
	):
		assert isinstance(exprs, list), f'Expected {property_name} to be list, but got {type(exprs)}'
		if len(exprs) == 2 and isinstance(exprs[0], Expr) and isinstance(exprs[1], str):
			self._logger.warning('Unwrapped tuple in %s: %s', property_name, exprs[1])
			exprs = [(exprs[0], exprs[1])] # idiot Pylance
			return self._switch_context(exprs)

		for i, t in enumerate(exprs):
			if not isinstance(t, tuple):
				self._logger.warning('Expected %s[%d] to be tuple, but got %s', property_name, i, type(t))
				self._logger.debug('Assuming %s to be [Expr]', property_name)
				all_expr = True
				for e in exprs:
					if not isinstance(e, Expr):
						all_expr = False
						break
				assert all_expr, 'All elements should be Expr if not (Expr, str).'
				exprs = [(e, '') for e in exprs] # type: ignore # idiot Pylance
				break
			assert len(t) == 2, f'Expected tuple {property_name}[{i}] to have length 2, but got {len(t)}'
			a, b = t
			assert isinstance(b, str), f'Expected {property_name}[{i}][1] to be str, but got {type(b)}'
			if not isinstance(a, Expr):
				self._logger.warning('Unexpected type %s of %s[%d][0]', type(a), property_name, i)

		return self._switch_context(exprs)

	def _switch_context(self, exprs: list[Tuple[Expr, str]]) -> list[Tuple[Expr, str]]:
		return [ # type: ignore
			(expr.translate(self.context) if expr.ctx != self.context else expr, desc)
			for expr, desc in exprs
		]

	@property
	def definitions(self):
		"""
		Definitions of defined relations.
		"""
		return self._definitions

	@definitions.setter
	def definitions(self, value: list[Tuple[Any, str]]):
		self._definitions = self._preprocess('definitions', value)

	@property
	def claims(self) -> list[Tuple[Any, str]]:
		"""
		Claims included in the text.
		"""
		return self._claims

	@claims.setter
	def claims(self, value: list[Tuple[Any, str]]):
		self._claims = self._preprocess('claims', value)

	@property
	def common_knowledge(self) -> list[Tuple[Any, str]]:
		"""
		World knowledge that are assumed to be true and that support the assertion.
		"""
		return self._common_knowledge

	@common_knowledge.setter
	def common_knowledge(self, value: list[Tuple[Any, str]]):
		self._common_knowledge = self._preprocess('common_knowledge', value)

	@property
	def assertions(self) -> list[Tuple[BoolRef | QuantifierRef, str]]:
		"""
		Target conclusions to be verified.
		"""
		raise NotImplementedError

	def _add(self) -> None:
		"""
		Add the premises to the solver.
		"""
		if not self._added:
			self._add2(self.definitions)
			self._add2(self.claims)
			if self.use_common_knowledge:
				self._add2(self.common_knowledge)
			self._added = True

	def _get_expr(self, exprs: list[Tuple[Any, str]]):
		return [expr for expr, _ in exprs]

	def _add2(self, exprs: list[Tuple[Any, str]]) -> None:
		self.s.add(self._get_expr(exprs))

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

	def to_conjunction(self):
		"""
		Get all added expressions in the solver as a conjunction.
		"""
		self._add()
		return And(*self.s.assertions())

	def simplify(self):
		"""
		Simplify the premises.
		"""
		return simplify(self.to_conjunction())

	def solve(self):
		"""
		Solve the premises.
		"""
		return solve(self.to_conjunction())

class Logic(LogicBase):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

	@property
	def assertions(self) -> list[Tuple[BoolRef | QuantifierRef, str]]:
		return self._assertions # type: ignore

	@assertions.setter
	def assertions(self, value: list[Tuple[Any, str]]):
		self._assertions = self._preprocess('assertions', value)
		for i, (assertion, _) in enumerate(self._assertions):
			if assertion in self._get_expr(self.definitions):
				self._logger.error('Assertion #%d (%s) is inluded in definitions.', i, assertion)
				assert False, 'Definitions should not include assertions.'
			elif assertion in self._get_expr(self.common_knowledge):
				self._logger.error('Assertion #%d (%s) is inluded in common knowledge.', i, assertion)
				assert not self.use_common_knowledge, 'Common knowledge should not include assertions.'
			elif assertion in self._get_expr(self.claims):
				self._logger.warning('Assertion #%d (%s) is inluded in claims.', i, assertion)

@deprecated('Use Logic instead.')
class QALogic(LogicBase):
	def __init__(self, **kwargs):
		raise NotImplementedError
		super().__init__(**kwargs)

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
