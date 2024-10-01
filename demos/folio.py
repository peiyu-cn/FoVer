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
People who supported the Portland Whigs did not get a seat in the Parliament.

Conclusion: William Dickinson did not get a seat in Parliament.
(Simple case does not need complex predicates and common knowledge.)"""
## Assistant:
def william_dickinson_did_not_get_seat_in_parliament(**kwargs) -> Logic:
	"""
	Claims:
	William Dickinson was a British politician who sat in the House of Commons
	William Dickinson attended Westminster school for high school and then the University of Edinburgh.
	The University of Edinburgh is a university located in the United Kingdom.
	William Dickinson supported the Portland Whigs.
	People who supported the Portland Whigs did not get a seat in the Parliament.

	Target: William Dickinson did not get a seat in Parliament.
	Predicates: be politician, sit in, attend school, attend university, be located in, support, get seat in.
	Parameters of predicates:
		be British politician: Person be British politician, *-bool, (Person) -> Bool.
			- Person
		sit in: Person sit in Institution, *-to-*, (Person, Institution) -> Bool.
			- Institution
		attend school: Person attend School, *-to-*, (Person, School) -> Bool.
			- School
		locate in: School locate in Country, *-to-1, (Institution) -> Country.
		support: Person support PoliticalGroup, *-to-*, (Person, PoliticalGroup) -> Bool.
			- PoliticalGroup
		get seat in: Person get seat in Institution, *-to-*, (Person, Institution) -> Bool.
	All sorts by now: Person, Institution, School, Country, PoliticalGroup.
	Concepts: William Dickinson, House of Commons, Westminster school, University of Edinburgh, United Kingdom, Portland Whigs, Parliament.
		- William Dickinson: Person
		- House of Commons: Institution
		- Westminster school: School
		- University of Edinburgh: School
		- United Kingdom: Country
		- Portland Whigs: PoliticalGroup
		- Parliament: Institution
	Rest sorts: .
	Supplemental predicates: .
	Removed & merged predicates: .
	All sorts: Person, Institution, School, Country, PoliticalGroup; Bool.
	"""
	# Initialize an instance of Logic with given arguments.
	l = Logic(**kwargs)

	# Define types.
	Person = DeclareSort('Person')
	Institution = DeclareSort('Institution')
	School = DeclareSort('School')
	Country = DeclareSort('Country')
	PoliticalGroup = DeclareSort('PoliticalGroup')
	# I shall use these identifiers for placeholders: Person: p*, Institution: i*, School: s*, Country: c*, PoliticalGroup: pg*; Bool: b*.

	# Define functions with usage comments.
	p_is_british_pilitician = Function('is-British-Politician', Person, BoolSort()) # (Person) -> Bool, usage: p_is_british_pilitician(Person).
	p_sit_in_i = Function('sit-in', Person, Institution, BoolSort()) # (Person, Institution) -> Bool, usage: p_sit_in_i(Person, Institution).
	p_attend_s = Function('attend-school', Person, School, BoolSort()) # (Person, School) -> Bool, usage: p_attend_s(Person, School).
	i_location__country = Function('location', School, Country) # (School) -> Country, usage: i_location__country(School) = Country.
	p_support_pg = Function('support', Person, PoliticalGroup, BoolSort()) # (Person, PoliticalGroup) -> Bool, usage: p_support_pg(Person, PoliticalGroup).
	p_get_seat_in_i = Function('get-seat-in', Person, Institution, BoolSort()) # (Person, Institution) -> Bool, usage: p_get_seat_in_i(Person, Institution).

	# Arrange instances.
	williamdickinson = Const('William Dickinson', Person)
	houseofcommons = Const('House of Commons', Institution)
	westminsterschool = Const('Westminster school', School)
	universityofedinburgh = Const('University of Edinburgh', School)
	unitedkingdom = Const('United Kingdom', Country)
	portlandwhigs = Const('Portland Whigs', PoliticalGroup)
	parliament = Const('Parliament', Institution)

	# I'm not sure what quantifiers will be used, so I shall define them later.
	def _store():
		# Relation Definitions
		l.definitions = []
		# Claims from text
		l.claims = [
			(
				"William Dickinson was a British politician who sat in the House of Commons",
				And(
					p_is_british_pilitician(williamdickinson),
					p_sit_in_i(williamdickinson, houseofcommons)
				)
			),
			(
				"William Dickinson attended Westminster school for high school and then the University of Edinburgh.",
				And(
					p_attend_s(williamdickinson, westminsterschool),
					p_attend_s(williamdickinson, universityofedinburgh)
				)
			),
			(
				"The University of Edinburgh is a university located in the United Kingdom.",
				i_location__country(universityofedinburgh) == unitedkingdom
			),
			(
				"William Dickinson supported the Portland Whigs.",
				p_support_pg(williamdickinson, portlandwhigs)
			),
			(
				"People who supported the Portland Whigs did not get a seat in the Parliament.",
				ForAll([p1], Implies(p_support_pg(p1, portlandwhigs), Not(p_get_seat_in_i(p1, parliament))))
			),
		]
		# Common sense
		l.common_knowledge = []
		# Target.
		l.assertions = [(
			"William Dickinson did not get a seat in Parliament.",
			Not(p_get_seat_in_i(williamdickinson, parliament))
		)]

	# All placeholders used: p1: Person
	p1, = Consts('p1', Person)

	_store()

	return l
