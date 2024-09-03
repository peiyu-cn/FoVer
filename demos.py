# %% imports
from z3 import *

from z3_utils import LogicBase, Logic, QALogic

# %% [markdown] demos
# ## Demo checklist:
# 1. User message is in format: "Question: <question> Answer: <answer>".
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
"""Extract logic to Z3 Python API from the given question-answer pair.
You need to define a python function to store `definations`, `claims`, `common_knowledge`, and the main target `assertion`.
`Logic` is a pre-defined wrapper class."""

# %% [markdown] Bamboogle demos
# ## Bamboogle demos
# 2-hop QA

# %% demo 1
## User:
"""Question: Who was president of the U.S. when superconductivity was discovered?
Answer:
Superconductivity was discovered in 1911 .  
The President of the United States was William Howard Taft from 1909 to 1913.  
So William Howard Taft was president of the U.S. when superconductivity was discovered"""
## Assistant:
def williamhowardtaft_was_president_of_us_when_superconductivity_was_discovered(**kwargs):
	"""
	Superconductivity was discovered in 1911.
	The President of the United States was William Howard Taft from 1909 to 1913.
	So William Howard Taft was president of the U.S. when superconductivity was discovered.
	
	Target: William Howard Taft was president of the U.S. when superconductivity was discovered.
	"""
	# Initialize an instance of Logic with given arguments.
	l = Logic(**kwargs)

	# Define types.
	Name = DeclareSort('Name')
	Event = DeclareSort('Event')
	Region = DeclareSort('Region')
	# Define functions.
	president_of_when = Function('is-president-of-when', Name, Region, IntSort(), BoolSort()) # (Name, Region, Int) -> Bool Name is president of Region when Int. # Using int as input and bool as output because this is not *-to-1 relation.
	happen_in = Function('happen-in', Event, IntSort()) # (Event) -> Int, Event happen in Int. # Using int as output because event time is *-to-1 relation.
	#  Target function:
	president_of_when_event = Function('is-president-of-when-event', Name, Region, Event, BoolSort()) # (Name, Region, Event) -> Bool, Name is president of Region when Event.

	# Arrange instances.
	discover_superconductivity = Const('discover-superconductivity', Event)
	williamhowardtaft = Const('William Howard Taft', Name)
	us = Const('U.S.', Region)
	unitedstates = Const('United States', Region)

	# Implementations.
	#  Local placeholders that will be used by quantifiers.
	i = Int('i')
	n = Const('n', Name)
	e = Const('e', Event)
	r = Const('r', Region)

	#  Relation Definitions
	l.definations = [
		(
			ForAll([n, e, r], president_of_when_event(n, r, e) == Exists([i], And(happen_in(e) == i, president_of_when(n, r, i)))),
			"A person was president when an event happened if and only if the event happened in the year that person was president."
		),
	]
	#  Claims from text
	l.claims = [
		(happen_in(discover_superconductivity) == 1911, "Superconductivity was discovered in 1911."),
		(
			ForAll([i], Implies(And(i >= 1909, i <= 1913), (president_of_when(williamhowardtaft, unitedstates, i)))),
			"William Howard Taft was president from 1909 to 1913.",
		),
	]
	#  Common knowledge that I know to be true and that support the reasoning process.
	l.common_knowledge = [
		(us == unitedstates, "U.S. is United States."),
	]

	# Target.
	l.assertion = president_of_when_event(williamhowardtaft, us, discover_superconductivity)

	return l

# %% demo 1 candidate
## User:
"""Question: Who was president of the U.S. when superconductivity was discovered?
Answer:
Superconductivity was discovered in 1911 by Heike Kamerlingh Onnes. Woodrow Wilson was president of the United States from 1913 to 1921. So the final answer (the name of the president) is: Woodrow Wilson."""
## Assistant:
def woodrowwilson_was_president_of_us_when_superconductivity_was_discovered(**kwargs):
	"""
	Superconductivity was discovered in 1911 by Heike Kamerlingh Onnes.
	Woodrow Wilson was president of the United States from 1913 to 1921.
	
	Target: Woodrow Wilson was president of the U.S. when superconductivity was discovered.
	"""
	# Initialize an instance of Logic with given arguments.
	l = Logic(**kwargs)

	# Define types.
	Name = DeclareSort('Name')
	Event = DeclareSort('Event')
	Region = DeclareSort('Region')
	# Define functions.
	president_of_when = Function('is-president-of-when', Name, Region, IntSort(), BoolSort()) # (Name, Region, Int) -> Bool Name is president of Region when Int. # Using int as input and bool as output because this is not *-to-1 relation.
	happen_in = Function('happen-in', Event, IntSort()) # (Event) -> Int, Event happen in Int. # Using int as output because event time is *-to-1 relation.
	#  Target function:
	president_of_when_event = Function('is-president-of-when-event', Name, Region, Event, BoolSort()) # (Name, Region, Event) -> Bool, Name is president of Region when Event.

	# Arrange instances.
	discover_superconductivity = Const('discover-superconductivity', Event)
	woodrowwilson = Const('Woodrow Wilson', Name)
	us = Const('U.S.', Region)
	unitedstates = Const('United States', Region)

	# Implementations.
	#  Local placeholders that will be used by quantifiers.
	i = Int('i')
	n = Const('n', Name)
	e = Const('e', Event)
	r = Const('r', Region)

	#  Relation Definitions
	l.definations = [
		(
			ForAll([n, e, r], president_of_when_event(n, r, e) == Exists([i], And(happen_in(e) == i, president_of_when(n, r, i)))),
			"A person was president when an event happened if and only if the event happened in the year that person was president."
		),
	]
	#  Claims from text
	l.claims = [
		(happen_in(discover_superconductivity) == 1911, "Superconductivity was discovered in 1911."),
		(
			ForAll([i], Implies(And(i >= 1913, i <= 1921), (president_of_when(woodrowwilson, unitedstates, i)))),
			"Woodrow Wilson was president from 1913 to 1921.",
		),
	]
	#  Common knowledge that I know to be true and that support the reasoning process.
	l.common_knowledge = [
		(us == unitedstates, "U.S. is United States."),
	]

	# Target.
	l.assertion = president_of_when_event(woodrowwilson, us, discover_superconductivity)

	return l

# %% demo 2
## User:
"""Question: When did the war that Neil Armstrong served in end?
Answer:
Neil Armstrong served in the Korean War, which lasted from 1950 to 1953. The war officially ended with an armistice agreement on July 27, 1953. 

So the final answer (the end date of the war) is: July 27, 1953."""
## Assistant:
def the_war_that_neilarmstrong_served_ended_on_july271953(**kwargs):
	"""
	Neil Armstrong served in the Korean War, which lasted from 1950 to 1953.
	The war officially ended with an armistice agreement on July 27, 1953.

	Target: The war that Neil Armstrong served ended on July 27, 1953.
	"""
	# Initialize an instance of Logic with given arguments.
	l = Logic(**kwargs)

	# Define types.
	Name = DeclareSort('Name')
	War = DeclareSort('War')
	Date = DeclareSort('Date')
	# Define functions.
	serve_in = Function('serve-in', Name, War) # (Name) -> War, Name serve in War. # The question implies that Neil Armstrong served in only one war, so this is a *-to-1 relation.
	war_in = Function('war-in', War, IntSort(), BoolSort()) # (War, Int) -> Bool, War in Int. # Using int as input and bool as output because war time is *-to-1 relation.
	war_end_on = Function('war-end-on', War, Date) # (War) -> Date, Event end on Date.
	#  Target function:
	war_served_end_on = Function('war-served-end-on', Name, Date) # (Name) -> Date, The war that Name served end on Date.

	# Arrange instances.
	neilarmstrong = Const('Neil Armstrong', Name)
	koreanwar = Const('Korean War', War)
	july271953 = Const('July 27, 1953', Date)

	# Implementations.
	#  Local placeholders that will be used by quantifiers.
	i = Int('i')
	n = Const('n', Name)
	w = Const('w', War)
	d = Const('d', Date)

	#  Relation Definitions
	l.definations = [
		(
			ForAll([n, d], (war_served_end_on(n) == d) == Exists([w], And(serve_in(n) == w, war_end_on(w) == d))),
			"The war that a person served in ended on a date if and only if the person served in that war and the war ended on that date."
		),
	]
	#  Claims from text
	l.claims = [
		(serve_in(neilarmstrong) == koreanwar, "Neil Armstrong served in the Korean War."),
		(ForAll([i], (war_in(koreanwar, i)) == And(i >= 1950, i <= 1953)), "Korean War lasted from 1950 to 1953."),
		(war_end_on(koreanwar) == july271953, "Korean War ended on July 27, 1953."),
	]
	#  Common knowledge that I know to be true and that support the reasoning process.
	l.common_knowledge = []

	# Target.
	l.assertion = war_served_end_on(neilarmstrong) == july271953

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

# %% demo 3
# one choice
## User:
"""Last night, Mark either went to play in the gym or visited his teacher Tony. If Mark drove last night, he didn't go to play in the gym. Mark would go visit his teacher Tony only if he and his teacher had an appointment. In fact, Mark had no appointment with his teacher Tony in advance.
Q: Which is true based on the above statement?
A. Mark went to the gym with his teacher Tony last night."""
## Assistant:
def mark_went_to_gym_with_his_teacher_tony_last_night(**kwargs):
	"""
	Last night, Mark either went to play in the gym or visited his teacher Tony.
	If Mark drove last night, he didn't go to play in the gym.
	Mark would go visit his teacher Tony only if he and his teacher had an appointment.
	In fact, Mark had no appointment with his teacher Tony in advance.
	
	Target: Mark went to the gym with his teacher Tony last night.
	"""
	# Initialize an instance of Logic with given arguments.
	l = Logic(**kwargs)

	# Define types.
	Name = DeclareSort('Name')
	Action = DeclareSort('Action') # Action may contain names, places, and times.
	Place = DeclareSort('Place')
	Time = DeclareSort('Time')
	# Define functions.
	did = Function('did', Name, Action, BoolSort()) # (Name, Action) -> Bool, Name did Action.
	did_with = Function('did-with', Name, Name, Action, BoolSort()) # (Name, Name, Action) -> Bool, Name did Action with Name.
	did_to = Function('did-to', Name, Name, Action, BoolSort()) # (Name, Name, Action) -> Bool, Name did Action to Name.
	did_at = Function('did-at', Name, Action, Place, BoolSort()) # (Name, Action, Place) -> Bool, Name did Action at Place.
	did_when = Function('did-when', Name, Action, Time, BoolSort()) # (Name, Action, Time) -> Bool, Name did Action when Time.
	at_when = Function('at-when', Name, Place, Time, BoolSort()) # (Name, Place, Time) -> Bool, Name at Place when Time.

	# Arrange instances.
	mark = Const('Mark', Name)
	tony = Const('Tony', Name)
	gym = Const('gym', Place)
	playinthegym = Const('play in the gym', Action)
	visittony = Const('visit Tony', Action)
	drive = Const('drive', Action)
	appointment = Const('have appointment', Action)
	lastnight = Const('last night', Time)

	# Implementations.
	#  Local placeholders that will be used by quantifiers.
	n1, n2 = Consts('n1 n2', Name)
	a = Const('a', Action)
	p1, p2 = Consts('p1 p2', Place)
	t = Const('t', Time)

	#  Relation Definitions
	l.definations = [
		# relations of 'did'
		(
			ForAll([n1, n2, a], Implies(did_with(n1, n2, a), did(n1, a))),
			"If a person did an action with another person, then that person did that action."
		),
		(
			ForAll([n1, n2, a], Implies(did_to(n1, n2, a), did(n1, a))),
			"If a person did an action to another person, then that person did that action."
		),
		(
			ForAll([n1, a, p1], Implies(did_at(n1, a, p1), did(n1, a))),
			"If a person did an action at a place, then that person did that action."
		),
		(
			ForAll([n1, a, t], Implies(did_when(n1, a, t), did(n1, a))),
			"If a person did an action when a time, then that person did that action."
		),
		# relations of 'did-with'
		(
			ForAll([n1, n2, a], did_with(n1, n2, a) == did_with(n2, n1, a)),
			"If a person did an action with another person, then the other person did that action with the person."
		),
		# relations of 'at-when'
		(
			ForAll([n1, p1, t], Implies(at_when(n1, p1, t), 
				ForAll([p2], (p2 == p1) == at_when(n1, p2, t)))),
			"If a person was at a place when a time, then the person was at only that place when that time."
		),
		(
			ForAll([n1, a, p1, t], Implies(And(did_at(n1, a, p1), did_when(n1, a, t)), at_when(n1, p1, t))),
		  	"If a person did an action at a place and when a time, then the person was at that place when that time."
		)
	]
	#  Claims from text
	l.claims = [
		(
			Xor(
				And(did_at(mark, playinthegym, gym), did_when(mark, playinthegym, lastnight)),
				And(did_to(mark, tony, visittony), did_when(mark, visittony, lastnight))
			),
			"Last night, Mark either went to play in the gym or visited his teacher Tony."
		),
		(
			Implies(
				did_when(mark, drive, lastnight),
				Not(did(mark, playinthegym))
			),
			"If Mark drove last night, he didn't go to play in the gym."
		),
		(
			Implies(did(mark, visittony), did_with(mark, tony, appointment)),
			"Mark would go visit his teacher Tony only if he and his teacher had an appointment."
		),
		(
			Not(did_with(mark, tony, appointment)),
			"Mark had no appointment with his teacher Tony in advance."
		),
	]
	#  Common knowledge that I know to be true and that support the reasoning process.
	l.common_knowledge = []

	# Target 1.
	l.assertion = And(
		at_when(mark, gym, lastnight),
		at_when(tony, gym, lastnight),
	)

	# Target 2.
	l.assertion = did_to(mark, tony, visittony)

	# Target 3.
	l.assertion = Not(did_when(mark, drive, lastnight))

	# Target 4.
	l.assertion = Not(at_when(mark, gym, lastnight))

	return l
