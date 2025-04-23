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

n = 4

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

# intersecting inequalities (3b)
intersecting_ineq = []
# Because addition is commutative, we currently generate duplicate constraints.
for t in I:
    for s in I:
        # The requirements that P[t] and P[s] are nonempty may be able to be
        # omitted? This is what the authors do in their implementation.
        if len(P[t]) != 0 and len(P[s]) != 0 and len(P[t] & P[s]) == 0:
            intersecting_ineq.append(y[t] + y[s] <= 1)

# star inequalities (3c)
star_ineq = []
for i in N:
    star_cardinality = Plus([x[s] for s in I if i in P[s]])
    star_ineq.append(
        star_cardinality <= z
    )

# generation inequalities (3d)
generation_ineq = []
for t in I:
    for s in I:
        if P[s] <= P[t]:
            generation_ineq.append(y[t] <= x[s])

constraints = And(
    domain_ineq + intersecting_ineq + star_ineq + generation_ineq
)

with Solver() as solver:
    solver.add_assertion(constraints)
   
    # TODO: Is this the correct objective function? Unclear whether the sum is
    # over just the y_S or over (y_S - z). 
    objective_func = Plus(y[s] - z for s in I if len(P[s]) != 0)
   
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
    
