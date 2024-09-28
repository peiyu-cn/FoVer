# %% imports
from z3.z3 import * # type: ignore

from z3_utils import Logic

# %% [markdown] demos
# ## Demo checklist:
# 1. User message is in format: "Question: <question> Answer: <answer>". # TODO
# 2. Function name.
# 3. kwargs.
# 4. Target description.
# 5. Logic initialization.
# 6. Function signatures.
# 7. Function descriptions.
# 8. Target function.
# 9. Targets.
# 10. Relation implementations.
# 11. Relation implementation descriptions.
# 12. Claims.
# 13. Claim descriptions.
# 14. Common knowledge.
# %% System:
"""Extract logic to Z3 Python API from the given text, faithfully, without judgment, following these steps:
1. Identify the conclusion of the text (target).
2. Collect all predicates from the text.
3. Determine their parameters and return types (sorts). (Whether they are predicative or relational, if relational, what is the kind of relation (1-to-1, *-to-1, *-to-*).)
4. Sum up all sorts that is used by predicates.
5. Collect all concepts from the text, determine their types (sorts).
6. Pick sorts that are not types of collected concepts.
7. For each sorts left, review the text to find out their instances, and identify the implicit predicates (what constitutes that sorts).
8. Check whether the sorts need additional supplemental relations (predicates), determine their parameters (sorts), if any, and re-run step 6-8. A supplemental relation is an extra relation you need to support rest sorts in step 6, about what them could be related to according to the text.
9. Review all predicates to see if some of them can be removed or merged.
10. Sum up all sorts.

You need to define a python function to store `definitions`, `claims`, `common_knowledge`, and the main target `assertions`, with their descriptions. `definitions` are relations among predicates, about what a predicate means. `common_knowledge` are unmentioned common sense without which the conclusion cannot be drawn, but are not restatement of the conclusion; the author misses them, but it can be inferred that the author assumes everyone know them, and they are indeed true.
`Logic` is a pre-defined wrapper class. `definitions`, `claims`, `common_knowledge`, and `assertions` are `list[tuple[str, Expr]]`.

NOTICE:
- A concept belongs to ONLY ONE sort. If you find multiple, you find implicit or supplemental predicates.
- `common_knowledge` MUST be COMMON and objectively TRUE.
- Elements of `definitions`, `claims`, `common_knowledge`, and `assertions` are `tuple[str, Expr]`. The first element is the description of the second element, MAKE SURE they match.
- Be faithful to claims and targets. Do not move some part of the text to `definitions` or `common_knowledge`; `definitions` and `common_knowledge` should NOT include any of claims and targets.
- Pay special attention to the usage of implication and equivalence, distinguish between one-way and two-way relations (p if q, p only if q, p if and only if q).
- When using quantifiers, ensure they are declared in parent Forall or Exists. And remember to define placeholders for them.
- Be extremely careful when using defined Z3 functions. Review their signatures and meanings, and review the definitions of parameters you want to use. MAKE SURE types of parameters & returns of functions correspond to their signatures.
Also, make sure types on both sides of equations are the same."""

# %% [markdown] Bamboogle demos
# ## Bamboogle demos
# 2-hop QA

# %% demo 1
## User:
"""Question: Who was president of the U.S. when superconductivity was discovered?
Answer:
Superconductivity was discovered in 1911 by Heike Kamerlingh Onnes. Woodrow Wilson was president of the United States from 1913 to 1921. So the final answer (the name of the president) is: Woodrow Wilson."""
## Assistant:
def president_of_us_when_superconductivity_was_discovered_was_woodrowwilson(**kwargs) -> Logic: # This function name exactly matches the target.
	"""
	Claims:
	Superconductivity was discovered in 1911 by Heike Kamerlingh Onnes.
	Woodrow Wilson was president of the United States from 1913 to 1921.
	
	Target: President of the U.S. when superconductivity was discovered was Woodrow Wilson.
	Predicates: discover in, discover by, be president of from to, be president of when.
	Parameters of predicates:
		discover in: New thing discover in Int, *-to-1, (New thing) -> Int.
			- New thing
		discover by: New thing discover by Person, *-to-1, (New thing) -> Person.
			- Person
		be president of from to: Person be president of Region from Int to Int, *-to-*, (Person, Region, Int) -> Bool. # [Preson] be president of [Region] from [Int a] to [Int b] == [Person] be president of [Region] in [Int x] (a <= x <= b), I will use this pattern for all range relations.
			- Region
		president of when: president of Region when Event happen is Person, *-to-1, (Region, Event) -> Person.
			- Event
	All sorts by now: New thing, Person, Region, Event.
	Concepts: Superconductivity, 1911, Heike Kamerlingh Onnes, Woodrow Wilson, United States, 1913, 1921, U.S.
		- Superconductivity: New thing
		- 1911: Int
		- Heike Kamerlingh Onnes: Person
		- Woodrow Wilson: Person
		- United States: Region
		- 1913: Int
		- 1921: Int
		- U.S.: Region
	Rest sorts: Event. # Sorts to which no concept above belongs.
		- Event:
			Concepts: # What constitutes an Event.
				- discover superconductivity
			Implicit predicates:
				- discover: discover New thing is Event, 1-to-1, (New thing) -> Event.
	Supplemental predicates:
		- happen in: Event happen in Int, *-to-1, (Event) -> Int.
	Removed & merged predicates:
		- discover in: [New thing] discover in [Int] ==
			discover [New thing] is [Event e], [Event e] happen in [Int].
	All sorts: New thing, Person, Region, Event; Int, Bool.
	"""
	# Initialize an instance of Logic with given arguments.
	l = Logic(**kwargs)

	# Define types.
	Newthing = DeclareSort('Newthing')
	Person = DeclareSort('Person')
	Region = DeclareSort('Region')
	Event = DeclareSort('Event')
	# I shall use thease identifiers for placeholders: Newthing: n*, Person: p*, Region: r*, Event: e*; Int: i*, Bool: b*.

	# Define functions with usage comments.
	n_discoverer__person = Function('discoverer', Newthing, Person) # (Newthing) -> Person, usage: n_discoverer__person(Newthing) = Person.
	p_is_president_of_r_in_i = Function('is-president-of-in', Person, Region, IntSort(), BoolSort()) # (Person, Region, Int) -> Bool, usage: p_is_president_of_r_in_i(Preson, Region, Int). # Person is president of Region from Int a to Int b means Person is president of Region in Int x (a <= x <= b).
	president_of_r_when_e_happen__person = Function('president-of-when', Person, Region, Event, BoolSort()) # (Region, Event) -> Person, usage: president_of_r_when_e_happen__person(Region, Event) = Person.
	discover_n_as__event = Function('discover', Newthing, Event) # (Newthing) -> Event, usage: discover_n_as__event(Newthing) = Event.
	e_happentime__int = Function('happentime', Event, IntSort()) # (Event) -> Int, usage: e_happentime__int(Event) = Int.

	# Arrange instances.
	superconductivity = Const('superconductivity', Newthing)
	heikekamerlinghonnes = Const('Heike Kamerlingh Onnes', Person)
	woodrowwilson = Const('Woodrow Wilson', Person)
	unitedstates = Const('United States', Region)
	us = Const('U.S.', Region)

	# I'm not sure what quantifiers will be used, so I shall define them later.
	def _store():
		# Relation Definitions
		l.definitions = [
			# What does president of Region when Event happen is Person mean.
			(
				"President of Region when an Event happened was Person if and only if the Event happened in the year that Person was president of that Region.",
				ForAll([p1, e1, r1], (president_of_r_when_e_happen__person(r1, e1) == p1) == Exists([i1], And(e_happentime__int(e1) == i1, p_is_president_of_r_in_i(p1, r1, i1))))
			),
			# Necessary constraints for 1-to-1 relations.
			(
				"'discover New thing is Event' is an injective relation between New thing and Event.",
				ForAll([n1, n2, e1], Implies(And(discover_n_as__event(n1) == e1, discover_n_as__event(n2) == e1), n1 == n2))
			)
		]
		# Claims from text
		l.claims = [
			("Superconductivity was discovered in 1911.", e_happentime__int(discover_n_as__event(superconductivity)) == 1911),
			(
				"Superconductivity was discovered by Heike Kamerlingh Onnes.",
				n_discoverer__person(superconductivity) == heikekamerlinghonnes
			),
			(
				"Woodrow Wilson was president from 1913 to 1921.",
				ForAll([i1], Implies(And(i1 >= 1913, i1 <= 1921), (p_is_president_of_r_in_i(woodrowwilson, unitedstates, i1))))
			),
		]
		# Common sense
		l.common_knowledge = [
			("U.S. is United States.", us == unitedstates),
		]
		# Target.
		l.assertions = [(
			"President of the U.S. when superconductivity was discovered was Woodrow Wilson.",
			president_of_r_when_e_happen__person(us, discover_n_as__event(superconductivity)) == woodrowwilson
		)]

	# All placeholders used: p1: Person, e1: Event, r1: Region, i1: Int
	n1, n2 = Consts('n1 n2', Newthing)
	p1, = Consts('p1', Person)
	e1, = Consts('e1', Event)
	r1, = Consts('r1', Region)
	i1, = Ints('i1')

	_store()

	return l

# %% [markdown] LogiQA 2.0 domos
# ## LogiQA 2.0 demos
# From LogiQA 2.0 (demo in the paper) (original multiple choice)
# 
# Last night, Mark either went to play in the gym or visited his teacher Tony. If Mark drove last night, he didn't go to play in the gym. Mark would go visit his teacher Tony only if he and his teacher had an appointment. In fact, Mark had no appointment with his teacher Tony in advance.
# Q: Which is true based on the above statement?
# A. Mark went to the gym with his teacher Tony last night.
# B. Mark visited his teacher Tony last night.
# C. Mark didn't drive last night.
# D. Mark didn't go to the gym last night.

# %% demo 2
# multiple choices
## User:
"""Last night, Mark either went to play in the gym or visited his teacher Tony. If Mark drove last night, he didn't go to play in the gym. Mark would go visit his teacher Tony only if he and his teacher had an appointment. In fact, Mark had no appointment with his teacher Tony in advance.
Q: Which is true based on the above statement?
A. Mark went to the gym with his teacher Tony last night.
B. Mark visited his teacher Tony last night.
C. Mark didn't drive last night.
D. Mark didn't go to the gym last night."""
## Assistant:
def multiple_targets_mark_either(**kwargs) -> Logic: # The function name does not matter in cases with multiple targets.
	"""
	Claims:
	Last night, Mark either went to play in the gym or visited his teacher Tony.
	If Mark drove last night, he didn't go to play in the gym.
	Mark would go visit his teacher Tony only if he and his teacher had an appointment.
	In fact, Mark had no appointment with his teacher Tony in advance.
	
	Targets:
	A. Mark went to the gym with his teacher Tony last night.
	B. Mark visited his teacher Tony last night.
	C. Mark didn't drive last night.
	D. Mark didn't go to the gym last night.
	Predicates: play in, visit, drive, have appointment, go to with, go to.
	Parameters of predicates:
		play in: Person play in Place when Time, *-bool, (Person, Place, Time) -> Bool. # This is more predicative than relational, so I use *-bool instead.
			- Person
			- Place
			- Time
		visit: Person visit Person when Time, *-bool, (Person, Person, Time) -> Bool.
		drive: Person drive when Time, *-bool, (Person, Time) -> Bool.
		have appointment: Person have appointment with Person before Time, *-bool, (Person, Person, Time) -> Bool.
		go to with: Person go to Place with Person when Time, *-bool, (Person, Place, Person, Time) -> Bool.
		go to: Person go to Place when Time, *-bool, (Person, Place, Time) -> Bool.
	All sorts by now: Person, Place, Time.
	Concepts: last night, Mark, gym, Tony.
		- last night: Time
		- Mark: Person
		- gym: Place
		- Tony: Person
	Rest sorts: .
	Supplemental predicates: .
	All sorts: Person, Place, Time; Bool.
	"""
	# Initialize an instance of Logic with given arguments.
	l = Logic(**kwargs)

	# Define types.
	Person = DeclareSort('Person')
	Place = DeclareSort('Place')
	Time = DeclareSort('Time')
	# I shall use thease identifiers for placeholders: Person: p*, Place: pl*, Time: t*; Bool: b*.

	# Define functions with usage comments.
	p_play_in_pl_when_t = Function('play-in-when', Person, Place, Time, BoolSort()) # (Person, Place, Time) -> Bool, usage: p_play_in_pl_when_t(Person, Place, Time).
	p_a_visit_p_b_when_t = Function('visit-when', Person, Person, Time, BoolSort()) # (Person, Person, Time) -> Bool, usage: p_a_visit_p_b_when_t(Person [a], Person [b], Time), Person a visit Person b when Time.
	p_drive_when_t = Function('drive-when', Person, Time, BoolSort()) # (Person, Time) -> Bool, usage: p_drive_when_t(Person, Time).
	p_a_have_appointment_with_p_b_before_t = Function('have-appointment-before', Person, Person, Time, BoolSort()) # (Person, Person, Time) -> Bool, usage: p_a_have_appointment_with_p_b_before_t(Person [a], Person [b], Time), Person a and Person b have appointment before Time.
	p_a_go_to_pl_with_p_b_when_t = Function('go-to-with-when', Person, Place, Person, Time, BoolSort()) # (Person, Place, Person, Time) -> Bool, usage: p_a_go_to_pl_with_p_b_when_t(Person [a], Place, Person [b], Time), Person a go to Place with Person b when Time.
	p_go_to_pl_when_t = Function('go-to-when', Person, Place, Time, BoolSort()) # (Person, Place, Time) -> Bool, usage: p_go_to_pl_when_t(Person, Place, Time).

	# Arrange instances.
	lastnight = Const('last night', Time)
	mark = Const('Mark', Person)
	gym = Const('gym', Place)
	tony = Const('Tony', Person)

	# I'm not sure what quantifiers will be used, so I shall define them later.
	def _store():
		# Relation Definitions
		l.definitions = [
			# What constitutes Person go to Place when Time.
			# What does Person play in Place when Time mean.
			(
				"If a Person plays in a Place at a Time, then the Person goes to the Place at that Time.",
				ForAll([p1, pl1, t1], Implies(p_play_in_pl_when_t(p1, pl1, t1), p_go_to_pl_when_t(p1, pl1, t1)))
			),
			# What does Person [a] go to Place with Person [b] when Time mean.
			(
				"If a Person A goes to a Place with Person B at a Time, then both Persons go to the Place at that Time.",
				ForAll([p1, p2, pl1, t1], Implies(p_a_go_to_pl_with_p_b_when_t(p1, pl1, p2, t1), And(p_go_to_pl_when_t(p1, pl1, t1), p_go_to_pl_when_t(p2, pl1, t1))))
			),
		]
		# Claims from text
		l.claims = [
			(
				"Last night, Mark either went to play in the gym or visited his teacher Tony.",
				# either-or in this text indicates that two sides cannot be true at the same time.
				Xor(
					p_play_in_pl_when_t(mark, gym, lastnight),
					p_a_visit_p_b_when_t(mark, tony, lastnight)
				)
			),
			(
				"If Mark drove last night, he didn't go to play in the gym.",
				Implies(p_drive_when_t(mark, lastnight), Not(p_play_in_pl_when_t(mark, gym, lastnight)))
			),
			(
				"Mark would go visit his teacher Tony only if he and his teacher had an appointment.",
				Implies(p_a_visit_p_b_when_t(mark, tony, lastnight), p_a_have_appointment_with_p_b_before_t(mark, tony, lastnight))
			),
			(
				"Mark had no appointment with his teacher Tony in advance.",
				Not(p_a_have_appointment_with_p_b_before_t(mark, tony, lastnight))
			),
		]
		# Common sense
		l.common_knowledge = [
			("Mark, Tony are different persons.", Distinct(mark, tony)),
		]
		# Targets that should be checked one by one.
		l.assertions = [
			(
				"Mark went to the gym with his teacher Tony last night.",
				p_a_go_to_pl_with_p_b_when_t(mark, gym, tony, lastnight)
			),
			("Mark visited his teacher Tony last night.", p_a_visit_p_b_when_t(mark, tony, lastnight)),
			("Mark didn't drive last night.", Not(p_drive_when_t(mark, lastnight))),
			("Mark didn't go to the gym last night.", Not(p_go_to_pl_when_t(mark, gym, lastnight))),
		]

	# All placeholders used: p1, p2: Person, pl1: Place, t1: Time
	p1, p2 = Consts('p1 p2', Person)
	pl1, = Consts('pl1', Place)
	t1, = Consts('t1', Time)

	_store()

	return l

# %% demo 3
# converted NLI
# from `QA2NLI/train.txt` line 4. label: not entailed
## User:
"""Premises: A, B, and C are three balls, one is red, one is blue, and the other is yellow. C is bigger than the yellow ball, A and the blue ball are not the same size, and the blue ball is smaller than C.
Conslusion: A is red, B is blue, C is yellow"""
## Assistant:
def a_red_b_blue_c_yellow(**kwargs) -> Logic: # This function name exactly matches the target.
	"""
	Claims:
	A, B, and C are three balls, one is red, one is blue, and the other is yellow.
	C is bigger than the yellow ball,
	A and the blue ball are not the same size,
	the blue ball is smaller than C.

	Target: A is red, B is blue, C is yellow.
	Predicates: is (color), is (size). # is bigger, are not the same size, is smaller can be unified under is (size).
	Parameters of predicates:
		is (color): Ball is Color, 1-to-1, (Ball) -> Color. # "are three balls, one is ..." and "'the' yellow ball, ..." indicate that Ball-Color relation in this text is 1-to-1.
			- Ball
			- Color
		is (size): Ball has size Int, *-to-1, (Ball) -> Int. # Any comparable type can be used for size. I just use Int for simplicity.
	All sorts by now: Ball, Color.
	Concepts: A, B, C, red, blue, yellow.
		- A, B, C: Ball
		- red, blue, yellow: Color
	Rest sorts: .
	Supplemental predicates: .
	All sorts: Ball, Color; Int.
	"""
	# Initialize an instance of Logic with given arguments.
	l = Logic(**kwargs)

	# Define types.
	Ball, (a, b, c) = EnumSort('Ball', ['A', 'B', 'C']) # We must be very careful when using EnumSort. I can use here and I shall use here because all claims in text about balls are about A, B, C, i.e., placeholders b* that will be used below will refer only to A, B, C (Exists b1 means one of A, B, C; ForAll b1 means all A, B, C).
	Color = DeclareSort('Color')
	# I shall use thease identifiers for placeholders: Ball: b*, Color: c*; Int: i*.

	# Define functions with usage comments.
	b__color = Function('ball-color', Ball, Color) # (Ball) -> Color, usage: b__color(Ball) = Color.
	b_size__int = Function('ball-size', Ball, IntSort()) # (Ball) -> Int, usage: b_size__int(Ball) = Int.

	# Arrange instances.
	red = Const('red', Color)
	blue = Const('blue', Color)
	yellow = Const('yellow', Color)

	# I'm not sure what quantifiers will be used, so I shall define them later.
	def _store():
		# Relation Definitions
		l.definitions = [
			# Necessary constraints for 1-to-1 relations.
			(
				"'Ball is Color' is an injective relation between Ball and Color.",
				ForAll([b1, b2], (b__color(b1) == b__color(b2)) == (b1 == b2)) # We must add brackets to sides of `==` to avoid ambiguity.
			),
		]
		# Claims from text
		l.claims = [
			("One ball is red.", Exists([b1], b__color(b1) == red)),
			("One ball is blue.", Exists([b1], b__color(b1) == blue)),
			("One ball is yellow.", Exists([b1], b__color(b1) == yellow)),
			("C is bigger than the yellow ball.", ForAll([b1], Implies(b__color(b1) == yellow, b_size__int(c) > b_size__int(b1)))),
			("A and the blue ball are not the same size.", ForAll([b1], Implies(b__color(b1) == blue, b_size__int(a) != b_size__int(b1)))),
			("The blue ball is smaller than C.", ForAll([b1], Implies(b__color(b1) == blue, b_size__int(b1) < b_size__int(c)))),
		]
		# Common sense
		l.common_knowledge = [
			("Red, blue, yellow are different colors.", Distinct(red, blue, yellow)),
		]
		# Target.
		l.assertions = [("A is red, B is blue, C is yellow.", And(b__color(a) == red, b__color(b) == blue, b__color(c) == yellow))]

	# All placeholders used: b1: Ball
	b1, b2 = Consts('b1 b2', Ball)

	_store()

	return l
