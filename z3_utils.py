from typing import Any, Callable, Tuple

from z3 import *
#from enum import Enum
#
#class JudgeResult(Enum):
#	FALSE = 0,
#	TRUE = 1,
#	SATISFIABLE = 2,
#	CONTRADICT = 3,
#	EXCEPTION = 4,

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

#def judge(r1: CheckSatResult, r2: CheckSatResult) -> JudgeResult:
#	if r1 == sat:
#		if r2 == sat:
#			return JudgeResult.SATISFIABLE
#		elif r2 == unsat:
#			return JudgeResult.TRUE
#		else:
#			return JudgeResult.EXCEPTION
#	elif r1 == unsat:
#		if r2 == sat:
#			return JudgeResult.CONTRADICT
#		elif r2 == unsat:
#			return JudgeResult.FALSE
#		else:
#			return JudgeResult.EXCEPTION
#	else:
#		return JudgeResult.EXCEPTION

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

class Logic:
	def __init__(self, use_world_knowledge=True):
		self.s = Solver()
		self.use_world_knowledge = use_world_knowledge
		self._added = False

	@property
	def definations(self):
		return self._definations

	@definations.setter
	def definations(self, value: list):
		self._definations = value

	@property
	def facts(self):
		return self._facts

	@facts.setter
	def facts(self, value: list):
		self._facts = value

	@property
	def world_knowledge(self):
		return self._world_knowledge

	@world_knowledge.setter
	def world_knowledge(self, value: list):
		self._world_knowledge = value

	@property
	def answer(self):
		return self._answer

	@answer.setter
	def answer(self, value):
		self._answer = value

	@property
	def answer_type(self):
		return self._answer_type

	@answer_type.setter
	def answer_type(self, value: SortRef):
		self._answer_type = value

	@property
	def question(self):
		return self._question

	@question.setter
	def question(self, value: Callable[[Any], BoolRef]):
		self._question = value
	
	@property
	def assertion(self):
		#return self._assertion
		return self.question(self.answer)

	#@assertion.setter
	#def assertion(self, value):
	#	self._assertion = value

	def _add(self):
		if not self._added:
			self.s.add(self.definations)
			self.s.add(self.facts)
			if self.use_world_knowledge:
				self.s.add(self.world_knowledge)
			self._added = True

	def verify(self):
		self._add()
		return verify(self.s, self.assertion)

	def judge(self):
		return judge(*self.verify())
