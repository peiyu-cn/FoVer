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
You need to define a python function to store `definations`, `facts`, `world_knowledge`, and the main target (`answer`, `answer_type`, and `question`).
`Logic` is a pre-defined wrapper class."""

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
	Answer: William Howard Taft.
	"""
	# Initialize an instance of QALogic with given arguments.
	l = QALogic(**kwargs)

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
	
	# Target.
	l.answer = williamhowardtaft
	l.answer_type = Name
	l.question = lambda n: president_of_when_event(n, us, discover_superconductivity)

	# Implementations.
	#  Local placeholders that will be used by quantifiers.
	i = Int('i')
	n = Const('n', Name)
	e = Const('e', Event)
	r = Const('r', Region)

	#  Relation Definitions
	l.definations = [
		# A person was president when an event happened if and only if the event happened in the year that person was president.
		ForAll([n, e, r], president_of_when_event(n, r, e) == Exists([i], And(happen_in(e) == i, president_of_when(n, r, i)))),
	]
	#  Claims from text
	l.claims = [
		happen_in(discover_superconductivity) == 1911, # Superconductivity was discovered in 1911.
		ForAll([i], (president_of_when(williamhowardtaft, unitedstates, i)) == And(i >= 1909, i <= 1913)), # WHT was president from 1909 to 1913.
	]
	#  Common knowledge that I know to be true and that support the reasoning process leading to the conclusion.
	l.common_knowledge = [
		us == unitedstates, # U.S. is United States.
	]

# %% demo 2
## User:
"""Question: When did the war that Neil Armstrong served in end?
Answer:
Neil Armstrong served in the Korean War, which lasted from 1950 to 1953. The war officially ended with an armistice agreement on July 27, 1953. 

So the final answer (the end date of the war) is: July 27, 1953."""
## Assistant:
def the_war_that_neilarmstrong_served_ended_on_july271953(kwargs):
	"""
	Neil Armstrong served in the Korean War, which lasted from 1950 to 1953.
	The war officially ended with an armistice agreement on July 27, 1953.

	Target: The war that Neil Armstrong served ended on July 27, 1953.
	Answer: July 27, 1953.
	"""
	# Initialize an instance of QALogic with given arguments.
	l = QALogic(**kwargs)

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

	# Target.
	l.answer = july271953
	l.answer_type = Date
	l.question = lambda d: war_served_end_on(neilarmstrong) == d

	# Implementations.
	#  Local placeholders that will be used by quantifiers.
	i = Int('i')
	n = Const('n', Name)
	w = Const('w', War)
	d = Const('d', Date)

	#  Relation Definitions
	l.definations = [
		# The war that a person served in ended on a date if and only if the person served in that war and the war ended on that date.
		ForAll([n, d], (war_served_end_on(n) == d) == Exists([w], And(serve_in(n) == w, war_end_on(w) == d))),
	]
	#  Claims from text
	l.claims = [
		serve_in(neilarmstrong) == koreanwar, # Neil Armstrong served in the Korean War.
		ForAll([i], (war_in(koreanwar, i)) == And(i >= 1950, i <= 1953)), # Korean War lasted from 1950 to 1953.
		war_end_on(koreanwar) == july271953, # Korean War ended on July 27, 1953.
	]
	#  Common knowledge that I know to be true and that support the reasoning process leading to the conclusion.
	l.common_knowledge = []
