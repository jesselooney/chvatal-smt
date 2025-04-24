"""This file implements an SMT encoding of Eifler et al.'s optimality-based
formulation, following the formulae in the paper as closely as possible. Where
applicable, this file follows the conventions in chvatal_optprob.zpl in Eifler
et al.'s MILP implementation.
"""

import time
from ..helpers import subsets
from collections.abc import Iterable, Set
from pysmt.typing import INT
from pysmt.shortcuts import Symbol, Plus, And, get_model, Solver, Int, Equals

n = 7

# N is $[n]$
N = range(1, n + 1)

# P is $2^[n]$
P = list(map(set, subsets(N, 1, n)))

# I is an index set for P, so that each element of P corresponds to an integer.
I = range(0, len(P))

x = [Symbol(f"x{i}", INT) for i in I]
y = [Symbol(f"y{i}", INT) for i in I]
# make x and y "binary" integer variables
domain_ineq = []
for i in I:
    domain_ineq.append(0 <= x[i])
    domain_ineq.append(x[i] <= 1)
    domain_ineq.append(0 <= y[i])
    domain_ineq.append(y[i] <= 1)

z = Symbol("z", INT)

# objective function
cost = Plus(y[i] - z for i in I)

# ideal inequality
ideal_ineq = []
for t in I:
    for s in I:
        if len(P[s] | P[t]) == len(P[t]) and len(P[s]) < len(P[t]):
            ideal_ineq.append(x[t] + x[s] <= 1)

# intersecting family
intersect_ineq = []
for t in I:
    for s in I:
        if len(P[t] & P[s]) == 0:
            intersect_ineq.append(y[t] + y[s] <= 1)

# z has to be greater or equal than the size of every star
smallerstar_ineq = []
for i in N:
    star_size = Plus(x[s] for s in I if i in P[s])
    smallerstar_ineq.append(star_size - z <= 0)

# containment inequality
containment_ineq = []
for t in I:
    containment_ineq.append(y[t] <= x[t])

constraints = And(
    domain_ineq + ideal_ineq + intersect_ineq + smallerstar_ineq + containment_ineq
)

with Solver() as solver:
    solver.add_assertion(constraints) 
   
    startTime = time.perf_counter() 
    is_zero_feasible = solver.solve([Equals(cost, Int(0))])
    stopTime = time.perf_counter()
    print(f"Found {is_zero_feasible=} in {stopTime - startTime} s")

    startTime = time.perf_counter() 
    is_positive_feasible = solver.solve([cost > 0])
    stopTime = time.perf_counter()
    print(f"Found {is_positive_feasible=} in {stopTime - startTime} s")

    # The Conjecture holds for downsets of cardinality at most n iff 0 is the
    # optimal value---that is, if 0 is a feasible objective value and no
    # larger objective value is feasible.
    if is_zero_feasible and not is_positive_feasible:
        print("Conjecture holds")
    else:
        print("Conjecture fails")
    
