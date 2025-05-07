"""This file implements an SMT encoding of Eifler et al.'s infeasibility-based
formulation, following the formulae in the paper as closely as possible. Where
applicable, this file follows the conventions in chvatal_optprob.zpl in Eifler
et al.'s MILP implementation.
"""

from ..helpers import powerset, FormulationResult
from pysmt.typing import INT
from pysmt.shortcuts import Symbol, Plus, And, Solver
import time


def inf(n: int, *, should_solve=True) -> FormulationResult:
    """Setup"""
    # N is [n] = {1, 2, ..., n}.
    N = list(range(1, n + 1))
    # P is 2^[n].
    P = list(map(set, powerset(N)))
    # I is an index set for P, so that each element of P corresponds to an integer.
    I = range(0, len(P))

    constraints = 0
    solver = Solver()

    """Variables and domain constraints"""
    x = [Symbol(f"x{i}", INT) for i in I]
    y = [Symbol(f"y{i}", INT) for i in I]
    for i in I:
        solver.add_assertion(
            And(
                0 <= x[i],
                x[i] <= 1,
                0 <= y[i],
                y[i] <= 1,
            )
        )
        constraints += 4

    """Model constraints"""
    # The paper notes that we can use (3d) instead of (1b) and (1d).
    # S(x) contains the powerset of S(y) (3d).
    for t in I:
        for s in I:
            if P[s] <= P[t]:
                solver.add_assertion(y[t] <= x[s])
                constraints += 1

    # S(y)\{0} is an intersecting family (1c).
    for t in I:
        for s in I:
            if len(P[t]) != 0 and len(P[s]) != 0 and len(P[t] & P[s]) == 0:
                solver.add_assertion(y[t] + y[s] <= 1)
                constraints += 1

    # S(y)\{0} has greater cardinality than every star in S(x) (1e).
    for i in N:
        # The cardinality of the largest star on i in S(x)
        star_cardinality = Plus(x[s] for s in I if i in P[s])
        # The cardinality of the intersecting family S(y)\{0}
        intersecting_cardinality = Plus(y[s] for s in I if len(P[s]) != 0)
        solver.add_assertion(star_cardinality + 1 <= intersecting_cardinality)
        constraints += 1

    """Checking the Conjecture"""
    # The Conjecture holds iff these constraints are unsatisfiable.

    if should_solve:
        start_time = time.perf_counter()
        is_satisfiable = solver.solve()
        end_time = time.perf_counter()
        does_conjecture_hold = not is_satisfiable
        runtime = end_time - start_time
    else:
        does_conjecture_hold = False
        runtime = -1

    solver.exit()

    return FormulationResult(
        name="inf",
        n=n,
        does_conjecture_hold=does_conjecture_hold,
        constraint_count=constraints,
        runtime=runtime,
    )
