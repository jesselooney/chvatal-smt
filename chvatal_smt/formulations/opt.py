"""This file implements an SMT encoding of Eifler et al.'s optimality-based
formulation, following the formulae in the paper as closely as possible. Where
applicable, this file follows the conventions in chvatal_optprob.zpl in Eifler
et al.'s MILP implementation.
"""

import time
import sys
from ..helpers import powerset
from collections.abc import Iterable, Set
from pysmt.typing import INT
from pysmt.shortcuts import Symbol, Plus, And, get_model, Solver, Int, Equals


def opt(n: int, solver: Solver):
    """Returns True iff downsets $D$ such that $|U(D)| \le n$ satisfy Chvatal's conjecture.
    """

    """Setup"""
    # N is $[n] = {1, 2, ..., n}$.
    N = list(range(1, n+1))
    # P is $2^[n]$.
    P = list(map(set, powerset(N)))
    # I is an index set for P, so that each element of P corresponds to an integer.
    I = range(0, len(P))

    """Variables and domain constraints"""
    x = [Symbol(f"x{i}", INT) for i in I]
    y = [Symbol(f"y{i}", INT) for i in I]
    z = Symbol("z", INT)
    for i in I:
        solver.add_assertion(And(
            0 <= x[i], x[i] <= 1,
            0 <= y[i], y[i] <= 1,
        ))
    solver.add_assertion(z >= 0)

    """Objective function"""
    # TODO: I still have concerns about the validity of the proof if $z$ is
    # included in the summation.
    # The cost function to be maximized (3a).
    cost = Plus(y[s] - z for s in I if len(P[s]) != 0)

    """Model constraints"""
    # $S(y)$ is an intersecting family (3b).
    for t in I:
        for s in I:
            if len(P[t]) != 0 and len(P[s]) != 0 and len(P[t] & P[s]) == 0:
                solver.add_assertion(y[t] + y[s] <= 1)

    # $z$ is at least the cardinality of the largest star in $S(x)$ (3c).
    for i in N:
        # The cardinality of the largest star on $i$ in $S(x)$
        star_cardinality = Plus(x[s] for s in I if i in P[s])
        solver.add_assertion(star_cardinality <= z)

    # $S(x)$ contains the powerset of $S(y)$ (3d).
    for t in I:
        for s in I:
            if P[s] <= P[t]:
                solver.add_assertion(y[t] <= x[s])

    """Checking the Conjecture"""
    # Since this is a maximization problem, the cost of an optimal solution is
    # zero iff there exists a feasible solution with zero cost, and no solution
    # with positive cost is feasible.
    is_zero_feasible = solver.solve([Equals(cost, Int(0))])
    is_positive_feasible = solver.solve([cost > 0])

    return is_zero_feasible and not is_positive_feasible


with Solver() as solver:
    n = 6
    if len(sys.argv) >= 2:
        n = sys.argv[1]

    print(f"Checking the Conjecture for {n=}")

    if opt(n, solver):
        print("Conjecture holds")
    else:
        print("Conjecture fails")

