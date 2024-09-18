# %% imports
from z3 import * # type: ignore

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
3. Determine their parameters and return types (sorts).
4. Sum up all sorts that is used by predicates.
5. Collect all concepts from the text, determine their types (sorts).
6. Pick sorts that are not types of collected concepts.
7. For each sorts left, review the text to find out their instances, extract common features of these instances, and identify the implicit predicate.
8. Check whether the implicit predicates need additional supplemental relations (predicates), determine their sorts, if any, and re-run step 6 and 7.
9. Review all predicates to see if some of them can be removed or merged.
10. Sum up all sorts.

You need to define a python function to store `definitions`, `claims`, `common_knowledge`, and the main target `assertions`, with their descriptions. `definitions` are relations among predicates, about what a predicate means. `common_knowledge` are unmentioned premises that are true and support the reasoning process, but are not restatement of the conclusion.
`Logic` is a pre-defined wrapper class. `definitions`, `claims`, `common_knowledge`, and `assertions` are `list[tuple[expr, str]]`, where the first element of the tuple is a Z3 expression.

NOTICE:
- A concept belongs to ONLY ONE sort. If you find multiple, you find implicit predicates.
- `common_knowledge` MUST be COMMON and TRUE.
- Pay special attention to the usage of implication and equivalence, distinguish between one-way and two-way relations.
- When using quantifiers, ensure they are declared in parent Forall or Exists. And remember to define placeholders for them at last.
- Be extremely careful when using defined Z3 functions, make sure the parameters and return types correspond to their signatures.
I repeat, MAKE SURE the usage of defined Z3 functions matches their signatures and meanings."""

# %% [markdown] Bamboogle demos
# ## Bamboogle demos
# 2-hop QA

# %% demo 1
## User:
"""Question: Who was president of the U.S. when superconductivity was discovered?
Answer:
Superconductivity was discovered in 1911 by Heike Kamerlingh Onnes. Woodrow Wilson was president of the United States from 1913 to 1921. So the final answer (the name of the president) is: Woodrow Wilson."""
## Assistant:
def woodrowwilson_was_president_of_us_when_superconductivity_was_discovered(**kwargs) -> Logic: # This function name exactly matches the target.
	"""
	Superconductivity was discovered in 1911 by Heike Kamerlingh Onnes.
	Woodrow Wilson was president of the United States from 1913 to 1921.
	
	Target: Woodrow Wilson was president of the U.S. when superconductivity was discovered. # The target is NOT 'Woodrow Wilson was president of the U.S. in 1911.' because the question and answer are not about who was in 1911, but about who was when superconductivity was discovered.
	Predicates: discover in, discover by, be president of from to, be president of when.
	Parameters of predicates:
		discover in: New thing discover in Int, *-to-1, (New thing) -> Int.
			- New thing
		discover by: New thing discover by Person, *-to-1, (New thing) -> Person.
			- Person
		be president of from to: Person be president of Region from Int to Int, *-to-*, (Person, Region, Int) -> Bool. # I will use this pattern for all range relations.
			- Region
		be president of when: Person be president of Region when Event happen, *-to-*, (Person, Region, Event) -> Bool. # There may be many events happen when a person is president of a region.
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
	Rest sorts: Event.
		- Event: # Concepts that form an event.
			- discover superconductivity
	Implicit predicates: discover New thing = Event [(New thing) -> Event].
	Supplemental predicates: Event happen in Int [(Event) -> Int].
	# discover in can be removed, replaced by discover and happen in.
	All sorts: New thing, Person, Region, Event.
	"""
	# Initialize an instance of Logic with given arguments.
	l = Logic(**kwargs)

	# Define types.
	Newthing = DeclareSort('Newthing')
	Person = DeclareSort('Person')
	Region = DeclareSort('Region')
	Event = DeclareSort('Event')
	# Define functions.
	# discover_in has been removed.
	discover_by = Function('discover-by', Newthing, Person) # (Newthing) -> Person, Newthing is discovered by Person.
	president_of_in = Function('is-president-of-in', Person, Region, IntSort(), BoolSort()) # (Person, Region, Int) -> Bool, Person is president of Region from Int a to Int b means Person is president of Region in Int x (a <= x <= b).
	president_of_when = Function('is-president-of-when', Person, Region, Event, BoolSort()) # (Person, Region, Event) -> Bool, Person is president of Region when Event happen.
	discover = Function('discover', Newthing, Event) # (Newthing) -> Event, discover Newthing is Event.
	happen_in = Function('happen-in', Event, IntSort()) # (Event) -> Int, Event happen in Int.

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
			(
				# p1: Person, e1: Event, r1: Region
				ForAll([p1, e1, r1], president_of_when(p1, r1, e1) == Exists([i1], And(happen_in(e1) == i1, president_of_in(p1, r1, i1)))),
				# i1: Int
				"A Person was president of Region when an Event happened if and only if the Event happened in the year that Person was president of that Region."
			),
		]
		# Claims from text
		l.claims = [
			(happen_in(discover(superconductivity)) == 1911, "Superconductivity was discovered in 1911."),
			(discover_by(superconductivity) == heikekamerlinghonnes, "Superconductivity was discovered by Heike Kamerlingh Onnes."),
			(
				ForAll([i1], Implies(And(i1 >= 1913, i1 <= 1921), (president_of_in(woodrowwilson, unitedstates, i1)))),
				"Woodrow Wilson was president from 1913 to 1921.",
			),
		]
		# Common knowledge that I know to be true and that support the reasoning process.
		l.common_knowledge = [
			(us == unitedstates, "U.S. is United States."),
		]

		# Target.
		l.assertions = [(
			president_of_when(woodrowwilson, us, discover(superconductivity)),
			"Woodrow Wilson was president of the U.S. when superconductivity was discovered."
		)]

	# All placeholders used: p1: Person, e1: Event, r1: Region, i1: Int
	p1, = Consts('n1', Person)
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
		play in: Person play in Place when Time, *-to-*, (Person, Place, Time) -> Bool.
			- Person
			- Place
			- Time
		visit: Person visit Person when Time, *-to-*, (Person, Person, Time) -> Bool.
		drive: Person drive when Time, *-to-*, (Person, Time) -> Bool.
		have appointment: Person have appointment with Person before Time, *-to-*, (Person, Person, Time) -> Bool.
		go to with: Person go to Place with Person when Time, *-to-*, (Person, Place, Person, Time) -> Bool.
		go to: Person go to Place when Time, *-to-*, (Person, Place, Time) -> Bool.
	All sorts by now: Person, Place, Time.
	Concepts: last night, Mark, gym, Tony.
		- last night: Time
		- Mark: Person
		- gym: Place
		- Tony: Person
	Rest sorts: .
	Implicit predicates: .
	Supplemental predicates: .
	All sorts: Person, Place, Time.
	"""
	# Initialize an instance of Logic with given arguments.
	l = Logic(**kwargs)

	# Define types.
	Person = DeclareSort('Person')
	Place = DeclareSort('Place')
	Time = DeclareSort('Time')
	# Define functions.
	play_in_when = Function('play-in-when', Person, Place, Time, BoolSort()) # (Person, Place, Time) -> Bool.
	visit_when = Function('visit-when', Person, Person, Time, BoolSort()) # (Person, Person, Time) -> Bool, Person A visit Person B when Time. # When a sort appears twice or more in one function, additional annotation is needed to distinguish them.
	drive_when = Function('drive-when', Person, Time, BoolSort()) # (Person, Time) -> Bool.
	have_appointment_before = Function('have-appointment-before', Person, Person, Time, BoolSort()) # (Person, Person, Time) -> Bool, Person A have appointment with Person B before Time.
	go_to_with_when = Function('go-to-with-when', Person, Place, Person, Time, BoolSort()) # (Person, Place, Person, Time) -> Bool, Person A go to Place with Person B when Time.
	go_to_when = Function('go-to-when', Person, Place, Time, BoolSort()) # (Person, Place, Time) -> Bool.

	# Arrange instances.
	lastnight = Const('last night', Time)
	mark = Const('Mark', Person)
	gym = Const('gym', Place)
	tony = Const('Tony', Person)

	# I'm not sure what quantifiers will be used, so I shall define them later.
	def _store():
		# Relation Definitions
		l.definitions = [
			# go to with when
			(
				# p1, p2: Person, pl1: Place, t1: Time
				ForAll([p1, p2, pl1, t1], Implies(go_to_with_when(p1, pl1, p2, t1), And(go_to_when(p1, pl1, t1), go_to_when(p2, pl1, t1)))),
				"If a Person A goes to a Place with Person B at a Time, then both Persons go to the Place at that Time."
			),
			# go to when
			(
				ForAll([p1, pl1, t1], Implies(play_in_when(p1, pl1, t1), go_to_when(p1, pl1, t1))),
				"If a Person plays in a Place at a Time, then the Person goes to the Place at that Time."
			),
		]
		# Claims from text
		l.claims = [
			(
				# either-or in this text indicates that two sides cannot be true at the same time.
				Xor(
					play_in_when(mark, gym, lastnight),
					visit_when(mark, tony, lastnight)
				),
				"Last night, Mark either went to play in the gym or visited his teacher Tony."
			),
			(
				Implies(drive_when(mark, lastnight), Not(play_in_when(mark, gym, lastnight))),
				"If Mark drove last night, he didn't go to play in the gym."
			),
			(
				Implies(visit_when(mark, tony, lastnight), have_appointment_before(mark, tony, lastnight)),
				"Mark would go visit his teacher Tony only if he and his teacher had an appointment."
			),
			(
				Not(have_appointment_before(mark, tony, lastnight)),
				"Mark had no appointment with his teacher Tony in advance."
			),
		]
		# Common knowledge that I know to be true and that support the reasoning process.
		l.common_knowledge = [
			(mark != tony, "Mark, Tony are different persons."),
		]

		# Targets that should be checked one by one.
		l.assertions = [
			# Target A.
			(
				go_to_with_when(mark, gym, tony, lastnight),
				"Mark went to the gym with his teacher Tony last night."
			),
			# Target B.
			(visit_when(mark, tony, lastnight), "Mark visited his teacher Tony last night."),
			# Target C.
			(Not(drive_when(mark, lastnight)), "Mark didn't drive last night."),
			# Target D.
			(Not(go_to_when(mark, gym, lastnight)), "Mark didn't go to the gym last night."),
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
"""Premises: A, B, and C are three balls, one is red, one is blue, and the other is yellow. C is bigger than the yellow ball, A and the blue ball are not the same size, and the blue ball is smaller than C
Conslusion: A is red, B is blue, C is yellow"""
## Assistant:
def a_red_b_blue_c_yellow(**kwargs) -> Logic: # This function name exactly matches the target.
	"""
	A, B, and C are three balls, one is red, one is blue, and the other is yellow.
	C is bigger than the yellow ball
	A and the blue ball are not the same size
	the blue ball is smaller than C.

	Target: A is red, B is blue, C is yellow.
	Predicates: has color, has size. # is red, is blue, is yellow can be unified under has color; is bigger, are not the same size, is smaller can be unified under has size.
	Parameters of predicates:
		has color: Ball is Color, *-to-1, (Ball) -> Color.
			- Ball
			- Color
		has size: Ball has size Int, *-to-1, (Ball) -> Int. # Any comparable type can be used for size. I just use Int for simplicity.
	All sorts by now: Ball, Color.
	Concepts: A, B, C, red, blue, yellow.
		- A, B, C: Ball
		- red, blue, yellow: Color
	Rest sorts: .
	Implicit predicates: .
	Supplemental predicates: .
	All sorts: Ball, Color.
	"""
	# Initialize an instance of Logic with given arguments.
	l = Logic(**kwargs)

	# Define types.
	Ball, (a, b, c) = EnumSort('Ball', ['A', 'B', 'C']) # A, B, C are three balls. # Use enum to indicate there are and there are only 3 balls, which are different from one another.
	Color, (red, blue, yellow) = EnumSort('Color', ['red', 'blue', 'yellow']) # I use enum so that Z3 knows these 3 colors are different; otherwise, I would have to explicitly state red != blue, red != yellow, blue != yellow.
	# Define functions.
	color = Function('color', Ball, Color) # (Ball) -> Color, Ball is Color.
	size = Function('size', Ball, IntSort()) # (Ball) -> Int, Ball has size Int.

	# Arrange instances.

	# I'm not sure what quantifiers will be used, so I shall define them later.
	def _store():
		# Relation Definitions
		l.definitions = []
		# Claims from text
		l.claims = [
			# b1: Ball
			(Exists([b1], color(b1) == red), "One ball is red."),
			(Exists([b1], color(b1) == blue), "One ball is blue."),
			(Exists([b1], color(b1) == yellow), "One ball is yellow."),
			(ForAll([b1], Implies(color(b1) == yellow, size(c) > size(b1))), "C is bigger than the yellow ball."),
			(ForAll([b1], Implies(color(b1) == blue, size(a) != size(b1))), "A and the blue ball are not the same size."),
			(ForAll([b1], Implies(color(b1) == blue, size(b1) < size(c))), "The blue ball is smaller than C."),
		]
		# Common knowledge that I know to be true and that support the reasoning process.
		l.common_knowledge = []

		# Target.
		l.assertions = [(And(color(a) == red, color(b) == blue, color(c) == yellow), "A is red, B is blue, C is yellow.")]

	# All placeholders used: b1: Ball
	b1, = Consts('b1', Ball)

	_store()

	return l

# %% [markdown] ProofWriter demos
# ## ProofWriter demos
# theory-statements pairs
# 
# Used data:
# - OWA/birds-electricity
# - OWA/NatLang
# 
# Template: "Theory: <theory> Question: Which of the following statements can be inferred from the theory?: <statements>"

#- %% demo 4
# from `meta-train.jsonl` line 1
##- User:
"""Theory:
From a certain angle Dave is blue but he is young so maybe that will go away. My friend Eric is very young. People say he is nice for having a round shape. Harry was in a chemistry lab accident and turned blue and green which is even more obvious due to his round figure. A kind, round person will surely be red as well. I have found that young, blue, and big individuals are also red. If smeone has a blue and green color, then they are young and probably kind. People that are green tend to be young. Somebody fitting a young, blue and round description will also fit a green description. Being cold and blue made them rough to deal with. A person that is known to be big and rough is also green, they will feel blue about it.

Question: Which of the following statements can be inferred from the theory?
Q1. Harry is blue.
Q6. Harry is not kind.
Q11. Dave is not rough.
Q12. Bob is young."""
##- Assistant:
def multiple_targets_dave_blue(**kwargs) -> Logic: # The function name does not matter in cases with multiple targets.
	"""
	From a certain angle Dave is blue but he is young so maybe that will go away.
	My friend Eric is very young.
	People say he is nice for having a round shape.
	Harry was in a chemistry lab accident and turned blue and green which is even more obvious due to his round figure.
	A kind, round person will surely be red as well.
	I have found that young, blue, and big individuals are also red.
	If smeone has a blue and green color, then they are young and probably kind.
	People that are green tend to be young.
	Somebody fitting a young, blue and round description will also fit a green description.
	Being cold and blue made them rough to deal with.
	A person that is known to be big and rough is also green, they will feel blue about it.

	Targets:
	Q1. Harry is blue.
	Q6. Harry is not kind.
	Q11. Dave is not rough.
	Q12. Bob is young.
	Predicates: has feature (is). # All predicates can be unified under has feature (is).
	Parameters of predicates:
		has feature: Person is Feature, *-to-*, (Person, Feature) -> Bool.
			- Person
			- Feature
	All sorts by now: Person, Feature.
	Concepts: Dave, blue, young, Eric, nice, round, Harry, green, kind, red, big, cold, rough, Bob.
		- Dave: Person
		- blue, young: Feature
		- Eric: Person
		- nice, round: Feature
		- Harry: Person
		- green, kind, red, big, cold, rough: Feature
		- Bob: Person
	Rest sorts: .
	Implicit predicates: .
	Supplemental predicates: .
	All sorts: Person, Feature.
	"""
	# Initialize an instance of Logic with given arguments.
	l = Logic(**kwargs)

	# Define types.
	Person = DeclareSort('Person')
	Feature, (blue, young, nice, round, green, kind, red, big, cold, rough) = EnumSort('Feature',
		['blue', 'young', 'nice', 'round', 'green', 'kind', 'red', 'big', 'cold', 'rough']
	) # Features are different from one another, and these are all features that would be used.
	# Define functions.
	has_feature = Function('is', Person, Feature, BoolSort()) # (Person, Feature) -> Bool, Person is Feature.

	# Arrange instances.
	dave = Const('Dave', Person)
	eric = Const('Eric', Person)
	harry = Const('Harry', Person)
	bob = Const('Bob', Person)

	# I'm not sure what quantifiers will be used, so I shall define them later.
	def _store():
		# Relation Definitions
		l.definitions = []
		# Claims from text
		l.claims = [
			(has_feature(dave, blue), "From a certain angle Dave is blue."),
			(has_feature(dave, young), "Dave is young."),
			(has_feature(eric, young), "Eric is very young."),
			(has_feature(eric, nice), "People say Eric is nice."),
			(has_feature(eric, round), "Eric has a round shape."),
			(has_feature(harry, blue), "Harry turned blue."),
			(has_feature(harry, green), "Harry turned green."),
			(has_feature(harry, round), "Harry has a round figure."),
			(
				# p1: Person
				ForAll([p1], Implies(And(has_feature(p1, kind), has_feature(p1, round)), has_feature(p1, red))),
				"A kind, round person will surely be red."
			),
			(
				ForAll([p1], Implies(And(has_feature(p1, young), has_feature(p1, blue), has_feature(p1, big)), has_feature(p1, red))),
				"Young, blue, and big individuals are also red."
			),
			(
				ForAll([p1], Implies(And(has_feature(p1, blue), has_feature(p1, green)), And(has_feature(p1, young), has_feature(p1, kind)))),
				"If someone has a blue and green color, then they are young and probably kind."
			),
			(ForAll([p1], Implies(has_feature(p1, green), has_feature(p1, young))), "People that are green tend to be young."),
			(
				ForAll([p1], Implies(And(has_feature(p1, young), has_feature(p1, blue), has_feature(p1, round)), has_feature(p1, green))),
				"Somebody fitting a young, blue and round description will also fit a green description."
			),
			(
				ForAll([p1], Implies(And(has_feature(p1, cold), has_feature(p1, blue)), has_feature(p1, rough))),
				"Being cold and blue made them rough to deal with."
			),
			(
				ForAll([p1], Implies(And(has_feature(p1, big), has_feature(p1, rough), has_feature(p1, green)), has_feature(p1, blue))),
				"A person that is known to be big and rough is also green, they will feel blue about it."
			),
		]
		# Common knowledge that I know to be true and that support the reasoning process.
		l.common_knowledge = [
			(
				And(eric != dave, eric != harry, eric != bob, dave != harry, dave != bob, harry != bob),
				"Eric, Dave, Harry, Bob are different persons."
			),
		]

		# Targets that should be checked one by one.
		l.assertions = [
			(has_feature(harry, blue), "Harry is blue."),
			(Not(has_feature(harry, kind)), "Harry is not kind."),
			(Not(has_feature(dave, rough)), "Dave is not rough."),
			(has_feature(bob, young), "Bob is young."),
		]

	# All placeholders used: p1: Person
	p1, = Consts('p1', Person)

	_store()

	return l
