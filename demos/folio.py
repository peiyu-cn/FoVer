# %% imports
from z3.z3 import * # type: ignore

from z3_utils import Logic

# %% [markdown] FOLIO Demos
# ## FOLIO Demos

# %% demo 1
## User:
"""Premises:
All customers in James' family who subscribe to AMC A-List are eligible to watch three movies every week without any additional fees. 
Some of the customers in James' family go to the cinema every week.
Customers in James' family subscribe to either AMC A-List or HBO service. 
Some of the customers in James' family are familiar with HBO service.
Some of the customers in James' family are unfamiliar with AMC A-List.
Customers in James' family who prefer TV series will not watch TV series in cinemas.
All customers in James' family who subscribe to HBO services prefer TV series to movies. 
No one who goes to the cinema every week does not prefer movies.
Lily is a customer in James' family; she watches TV series in cinemas. 
Li is another name for Lily.

Conclusion: Lily goes to cinemas every week.
(Simple case, treat all concepts as single sort Entity, do not need complex predicates and common knowledge apart from distinction and equivalence.)"""
## Assistant:
def lily_goes_to_cinemas_every_week(**kwargs) -> Logic:
	"""
	Claims:
	All customers in James' family who subscribe to AMC A-List are eligible to watch three movies every week without any additional fees.
	Some of the customers in James' family go to the cinema every week.
	Customers in James' family subscribe to either AMC A-List or HBO service.
	Some of the customers in James' family are familiar with HBO service.
	Some of the customers in James' family are unfamiliar with AMC A-List.
	Customers in James' family who prefer TV series will not watch TV series in cinemas.
	All customers in James' family who subscribe to HBO services prefer TV series to movies.
	No one who goes to the cinema every week does not prefer movies.
	Lily is a customer in James' family; she watches TV series in cinemas.
	Li is another name for Lily.

	Target: Lily goes to cinemas every week.
	Predicates: is customer, is in, subscribe, eligible to watch three movies every week without any additional fees, go to every week, is familiar with, prefer, watch in.
	Parameters of predicates:
		is customer: Entity is Customer, *-bool, (Entity) -> Bool.
			- Entity
		is in: Entity is in Entity, *-bool, (Entity, Entity) -> Bool.
		subscribe: Entity subscribe to Entity, *-bool, (Entity, Entity) -> Bool.
		eligible to watch three movies every week without any additional fees: Entity eligible to watch three movies every week without any additional fees, *-bool, (Entity) -> Bool.
		go to every week: Entity go to Entity every week, *-bool, (Entity, Entity) -> Bool.
		is familiar with: Entity is familiar with Entity, *-bool, (Entity, Entity) -> Bool.
		prefer: Entity prefer Entity, *-bool, (Entity, Entity) -> Bool.
		watch in: Entity watch Entity in Entity, *-bool, (Entity, Entity, Entity) -> Bool.
	All sorts by now: Entity
	Concepts: James' family, AMC A-List, cinema, HBO service, TV series, movie, Lily, Li.
		- James' family, AMC A-List, cinema, HBO service, TV series, movie, Lily, Li: Entity
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
	e_is_customer = Function('is-customer', Entity, BoolSort()) # (Entity) -> Bool, Entity is Customer, usage: e_is_customer(Entity).
	e_a_is_in_e_b = Function('is-in', Entity, Entity, BoolSort()) # (Entity, Entity) -> Bool, Entity a is in Entity b, usage: e_a_is_in_e_b(Entity, Entity).
	e_a_subscribe_to_e_b = Function('subscribe', Entity, Entity, BoolSort()) # (Entity, Entity) -> Bool, Entity a subscribe to Entity b, usage: e_a_subscribe_to_e_b(Entity, Entity).
	e_eligible_watch3movies_everyweek_free = Function('eligible-to-watch', Entity, BoolSort()) # (Entity) -> Bool, Entity eligible to watch Int movies every week, usage: e_eligible_watch3movies_everyweek_free(Entity).
	e_a_go_to_e_b_every_week = Function('go-to-every-week', Entity, Entity, BoolSort()) # (Entity, Entity) -> Bool, Entity a go to Entity b every week, usage: e_a_go_to_e_b_every_week(Entity, Entity).
	e_a_is_familiar_with_e_b = Function('is-familiar-with', Entity, Entity, BoolSort()) # (Entity, Entity) -> Bool, Entity a is familiar with Entity b, usage: e_a_is_familiar_with_e_b(Entity, Entity).
	e_a_prefer_e_b = Function('prefer', Entity, Entity, BoolSort()) # (Entity, Entity) -> Bool, Entity a prefer Entity b, usage: e_a_prefer_e_b(Entity, Entity).
	e_a_watch_e_b_in_e_c = Function('watch-in', Entity, Entity, Entity, BoolSort()) # (Entity, Entity, Entity) -> Bool, Entity watch Entity in Entity, usage: e_a_watch_e_b_in_e_c(Entity, Entity, Entity).

	# Arrange instances.
	jamesfamily = Const("James' family", Entity)
	amcalist = Const('AMC A-List', Entity)
	cinema = Const('cinema', Entity)
	hboservice = Const('HBO service', Entity)
	tvseries = Const('TV series', Entity)
	movie = Const('movie', Entity)
	lily = Const('Lily', Entity)
	li = Const('Li', Entity)

	# I'm not sure what quantifiers will be used, so I shall define them later.
	def _store():
		# Relation Definitions
		l.definitions = []
		# Claims from text
		l.claims = [
			(
				"All customers in James' family who subscribe to AMC A-List are eligible to watch three movies every week without any additional fees.",
				ForAll([e1], Implies(
					And(e_is_customer(e1), e_a_is_in_e_b(e1, jamesfamily), e_a_subscribe_to_e_b(e1, amcalist)),
					e_eligible_watch3movies_everyweek_free(e1)
				))
			),
			(
				"Some of the customers in James' family go to the cinema every week.",
				Exists([e1], And(e_is_customer(e1), e_a_is_in_e_b(e1, jamesfamily), e_a_go_to_e_b_every_week(e1, cinema)))
			),
			(
				"Customers in James' family subscribe to either AMC A-List or HBO service.",
				# Always use Xor for 'either or'.
				ForAll([e1], Implies(
					And(e_is_customer(e1), e_a_is_in_e_b(e1, jamesfamily)),
					Xor(e_a_subscribe_to_e_b(e1, amcalist), e_a_subscribe_to_e_b(e1, hboservice))
				))
			),
			(
				"Some of the customers in James' family are familiar with HBO service.",
				Exists([e1], And(
					e_is_customer(e1), e_a_is_in_e_b(e1, jamesfamily),
					e_a_is_familiar_with_e_b(e1, hboservice)
				))
			),
			(
				"Some of the customers in James' family are unfamiliar with AMC A-List.",
				Exists([e1], And(
					e_is_customer(e1), e_a_is_in_e_b(e1, jamesfamily),
					Not(e_a_is_familiar_with_e_b(e1, amcalist))
				))
			),
			(
				"Customers in James' family who prefer TV series will not watch TV series in cinemas.",
				ForAll([e1], Implies(
					And(e_is_customer(e1), e_a_is_in_e_b(e1, jamesfamily), e_a_prefer_e_b(e1, tvseries)),
					Not(e_a_watch_e_b_in_e_c(e1, tvseries, cinema))
				))
			),
			(
				"All customers in James' family who subscribe to HBO services prefer TV series to movies.",
				ForAll([e1], Implies(
					And(e_is_customer(e1), e_a_is_in_e_b(e1, jamesfamily), e_a_subscribe_to_e_b(e1, hboservice)),
					And(e_a_prefer_e_b(e1, tvseries), Not(e_a_prefer_e_b(e1, movie)))
				))
			),
			(
				"No one who goes to the cinema every week does not prefer movies.",
				Not(Exists([e1],
			   		And(e_a_go_to_e_b_every_week(e1, cinema), Not(e_a_prefer_e_b(e1, movie)))
				))
			),
			(
				"Lily is a customer in James' family; she watches TV series in cinemas.",
				And(
					e_is_customer(lily), e_a_is_in_e_b(lily, jamesfamily),
					e_a_watch_e_b_in_e_c(lily, tvseries, cinema)
				)
			),
			(
				"Li is another name for Lily.",
				# Always use `==` when seeing 'is another name for'.
				li == lily
			)
		]
		# Common sense
		l.common_knowledge = []
		# Target.
		l.assertions = [("Lily goes to cinemas every week.", e_a_go_to_e_b_every_week(lily, cinema))]

	# All placeholders used: e1: Entity
	e1, = Consts('e1', Entity)

	_store()

	return l
