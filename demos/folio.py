# %% imports
from z3.z3 import * # type: ignore

from z3_utils import Logic

# %% [markdown] FOLIO Demos
# ## FOLIO Demos

# %% demo 1
## User:
"""Premises:
William Dickinson was a British politician who sat in the House of Commons
William Dickinson attended Westminster school for high school and then the University of Edinburgh.
The University of Edinburgh is a university located in the United Kingdom.
William Dickinson supported the Portland Whigs.
William Thornton Dickinson is another name for William Dickinson.
People who supported the Portland Whigs did not get a seat in the Parliament.

Conclusion: William Dickinson did not get a seat in Parliament.
(Simple case does not need complex predicates and common knowledge apart from distinction and equivalence.)"""
## Assistant:
def william_dickinson_did_not_get_seat_in_parliament(**kwargs) -> Logic:
	"""
	Claims:
	William Dickinson was a British politician who sat in the House of Commons
	William Dickinson attended Westminster school for high school and then the University of Edinburgh.
	The University of Edinburgh is a university located in the United Kingdom.
	William Dickinson supported the Portland Whigs.
	William Thornton Dickinson is another name for William Dickinson.
	People who supported the Portland Whigs did not get a seat in the Parliament.

	Target: William Dickinson did not get a seat in Parliament.
	Predicates: be politician, sit in, attend school, attend university, be located in, support, get seat in.
	Parameters of predicates:
		is a: Entity is Entity, *-bool, (Entity, Entity) -> Bool. # Simple case
			- Entity
		sit in: Entity sit in Entity, *-bool, (Entity, Entity) -> Bool.
		attend: Entity attend Entity, *-bool, (Entity, Entity) -> Bool.
		locate in: Entity locate in Entity, *-bool, (Entity, Entity) -> Bool.
		support: Entity support Entity, *-bool, (Entity, Entity) -> Bool.
		get seat in: Entity get seat in Entity, *-bool, (Entity, Entity) -> Bool.
	All sorts by now: Entity
	Concepts: William Dickinson, British politician, House of Commons, Westminster school, University of Edinburgh, university, United Kingdom, Portland Whigs, Parliament.
		- William Dickinson, British politician, House of Commons, Westminster school, University of Edinburgh, university, United Kingdom, Portland Whigs, William Thornton Dickinson, Parliament: Entity
	Rest sorts: .
	Supplemental predicates: .
	Removed & merged predicates: .
	All sorts: Entity; Bool.
	"""
	# Initialize an instance of Logic with given arguments.
	l = Logic(**kwargs)

	# Define types.
	Entity = DeclareSort('Entity')
	# I shall use these identifiers for placeholders: Entity: e*; Bool: b*.

	# Define functions with usage comments.
	e_a_is_a_e_b = Function('is-a', Entity, Entity, BoolSort()) # (Entity, Entity) -> Bool, Entity a is an Entity b, usage: e_a_is_a_e_b(Entity, Entity).
	e_a_sit_in_e_b = Function('sit-in', Entity, Entity, BoolSort()) # (Entity, Entity) -> Bool, Entity a sit in Entity b, usage: e_a_sit_in_e_b(Entity, Entity).
	e_a_attend_e_b = Function('attend', Entity, Entity, BoolSort()) # (Entity, Entity) -> Bool, Entity a attend Entity b, usage: e_a_attend_e_b(Entity, Entity).
	e_a_locate_in_e_b = Function('locate-in', Entity, Entity, BoolSort()) # (Entity, Entity) -> Bool, Entity a locate in Entity b, usage: e_a_locate_in_e_b(Entity, Entity).
	e_a_support_e_b = Function('support', Entity, Entity, BoolSort()) # (Entity, Entity) -> Bool, Entity a support Entity b, usage: e_a_support_e_b(Entity, Entity).
	e_a_get_seat_in_e_b = Function('get-seat-in', Entity, Entity, BoolSort()) # (Entity, Entity) -> Bool, Entity a get seat in Entity b, usage: e_a_get_seat_in_e_b(Entity, Entity).

	# Arrange instances.
	williamdickinson = Const('William Dickinson', Entity)
	britishpolitician = Const('British politician', Entity)
	houseofcommons = Const('House of Commons', Entity)
	westminsterschool = Const('Westminster school', Entity)
	universityofedinburgh = Const('University of Edinburgh', Entity)
	university = Const('university', Entity)
	unitedkingdom = Const('United Kingdom', Entity)
	portlandwhigs = Const('Portland Whigs', Entity)
	williamthorntondickinson = Const('William Thornton Dickinson', Entity)
	parliament = Const('Parliament', Entity)

	# I'm not sure what quantifiers will be used, so I shall define them later.
	def _store():
		# Relation Definitions
		l.definitions = []
		# Claims from text
		l.claims = [
			(
				"William Dickinson was a British politician who sat in the House of Commons",
				And(
					e_a_is_a_e_b(williamdickinson, britishpolitician),
					e_a_sit_in_e_b(williamdickinson, houseofcommons)
				)
			),
			(
				"William Dickinson attended Westminster school for high school and then the University of Edinburgh.",
				And(
					e_a_attend_e_b(williamdickinson, westminsterschool),
					e_a_attend_e_b(williamdickinson, universityofedinburgh)
				)
			),
			(
				"The University of Edinburgh is a university located in the United Kingdom.",
				And(
					e_a_is_a_e_b(universityofedinburgh, university),
					e_a_locate_in_e_b(universityofedinburgh, unitedkingdom)
				)
			),
			(
				"William Dickinson supported the Portland Whigs.",
				e_a_support_e_b(williamdickinson, portlandwhigs)
			),
			(
				"William Thornton Dickinson is another name for William Dickinson.",
				williamthorntondickinson == williamdickinson
			),
			(
				"People who supported the Portland Whigs did not get a seat in the Parliament.",
				ForAll([e1], Implies(e_a_support_e_b(e1, portlandwhigs), Not(e_a_get_seat_in_e_b(e1, parliament))))
			),
		]
		# Common sense
		l.common_knowledge = []
		# Target.
		l.assertions = [(
			"William Dickinson did not get a seat in Parliament.",
			Not(e_a_get_seat_in_e_b(williamdickinson, parliament))
		)]

	# All placeholders used: e1: Entity
	e1, = Consts('e1', Entity)

	_store()

	return l
