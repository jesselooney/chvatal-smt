"""This file implements an SMT encoding of Eifler et al.'s optimality-based
formulation, following the formulae in the paper as closely as possible. Where
applicable, this file follows the conventions in chvatal_optprob.zpl in Eifler
et al.'s MILP implementation.
"""

import time
from ..helpers import powerset
from collections.abc import Iterable, Set
from pysmt.typing import INT
from pysmt.shortcuts import Symbol, Plus, And, get_model, Solver, Int, Equals

n = 8

# N is $[n]$
N = range(0, n)

# P is $2^[n]$
P = list(map(set, powerset(N)))

# I is an index set for P, so that each element of P corresponds to an integer.
I = range(0, len(P))

x = [Symbol(f"x{i}", INT) for i in I]
y = [Symbol(f"y{i}", INT) for i in I]
z = Symbol("z", INT)

# In the following, I have aimed to match inequalities (1b-1e) in Eifler et al.
# as faithfully as possible. Compare this code to their ZIMPL implementation
# which differs slightly from their writeup.

# Constrain x's and y's to [0, 1]
domain_ineq = []
for s in I:
    domain_ineq.append(0 <= x[s])
    domain_ineq.append(x[s] <= 1)
    domain_ineq.append(0 <= y[s])
    domain_ineq.append(y[s] <= 1)

domain_ineq.append(z >= 0)

# intersecting inequalities (7b)
intersecting_ineq = []
# Because addition is commutative, we currently generate duplicate constraints.
for t in I:
    for s in I:
        # The requirements that P[t] and P[s] are nonempty may be able to be
        # omitted? This is what the authors do in their implementation.
        if len(P[t]) != 0 and len(P[s]) != 0 and len(P[t] & P[s]) == 0:
            intersecting_ineq.append(y[t] + y[s] <= 1)

# star inequalities (7c)
star_ineq = []
for i in N:
    star_cardinality = Plus([x[s] for s in I if i in P[s]])
    star_ineq.append(
        star_cardinality <= z
    )

# generation inequalities (7d)
generation_ineq = []
for t in I:
    for s in I:
        if P[s] <= P[t]:
            generation_ineq.append(y[t] <= x[s])

# Berge's inequality (7e)
berge_ineq = [Plus(Int(2) * y[s] for s in I if len(P[s]) != 0) <= Plus(x[s] for s in I)]

# not powerset
#notps_ineq = []
#for s in I:
#    if len(P[s]) == n:
#        y[s] <= 0

# corollary 3 equalities (7f)
corollary_3_eq = []
for s in I:
    if 1 <= len(P[s]) <= 2:
        corollary_3_eq.append(Equals(y[s], Int(0)))

# proposition 4 equalities (7g)
proposition_4_eq = []
for s in I:
    if len(P[s]) == 1:
        proposition_4_eq.append(Equals(x[s], Int(1)))

# proposition 5 equalities (7h)
proposition_5_eq = []
for s in I:
    if P[s] <= set(range(0, 4)):
        proposition_5_eq.append(Equals(x[s], Int(1)))

# TODO: Include constraint that S(y) is not the whole powerset? This is included
# in the ZIMPL implementation.

# TODO: Note that I have not included propositions 4 or 5 here as they make the
# objective value of 0 infeasible for some reason.
constraints = And(
    domain_ineq + intersecting_ineq + star_ineq + generation_ineq + berge_ineq + corollary_3_eq
)


with Solver() as solver:
    solver.add_assertion(constraints)
   
    # TODO: Is this the correct objective function? Unclear whether the sum is
    # over just the y_S or over (y_S - z). 
    objective_func = Plus(y[s] - z for s in I if len(P[s]) != 0)
    
    #print(constraints)
    #print(objective_func)
   
    startTime = time.perf_counter() 
    is_zero_feasible = solver.solve([Equals(objective_func, Int(0))])
    is_positive_feasible = solver.solve([objective_func > 0])
    stopTime = time.perf_counter()

    runtime = stopTime - startTime
    print(f"{runtime=}")

    # The Conjecture holds for downsets of cardinality at most n iff 0 is the
    # optimal value---that is, if 0 is a feasible objective value and no
    # larger objective value is feasible.
    if is_zero_feasible and not is_positive_feasible:
        print("Conjecture holds")
    else:
        print("Conjecture fails")
    
