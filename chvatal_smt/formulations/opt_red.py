"""This file implements an SMT encoding of Eifler et al.'s optimality-based
formulation, following the formulae in the paper as closely as possible. Where
applicable, this file follows the conventions in chvatal_optprob.zpl in Eifler
et al.'s MILP implementation.
"""

from ..helpers import powerset, FormulationResult
from pysmt.typing import INT
from pysmt.shortcuts import Symbol, Plus, And, Solver, Int, Equals
import time


def opt_red(n: int, *, should_solve=True) -> FormulationResult:
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
    z = Symbol("z", INT)
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

    solver.add_assertion(z >= 0)
    constraints += 1

    """Objective function"""
    # The cost function to be maximized (7a).
    cost = Plus(y[s] for s in I if len(P[s]) != 0) - z

    """Model constraints"""
    # S(y)\{0} is an intersecting family (7b).
    for t in I:
        for s in I:
            if len(P[t]) != 0 and len(P[s]) != 0 and len(P[t] & P[s]) == 0:
                solver.add_assertion(y[t] + y[s] <= 1)
                constraints += 1

    # z is at least the cardinality of the largest star in S(x) (7c).
    for i in N:
        # The cardinality of the largest star on i in S(x)
        star_cardinality = Plus(x[s] for s in I if i in P[s])
        solver.add_assertion(star_cardinality <= z)
        constraints += 1

    # S(x) contains the powerset of S(y) (7d).
    for t in I:
        for s in I:
            if P[s] <= P[t]:
                solver.add_assertion(y[t] <= x[s])
                constraints += 1

    """Additional constraints"""
    # (7e)
    lhs = Plus(2 * y[s] for s in I if len(P[s]) != 0)
    rhs = Plus(x[s] for s in I)
    solver.add_assertion(lhs <= rhs)
    constraints += 1

    # (7f)
    for s in I:
        if 1 <= len(P[s]) <= 2:
            solver.add_assertion(Equals(y[s], Int(0)))
            constraints += 1

    # (7g)
    for s in I:
        if len(P[s]) == 1:
            solver.add_assertion(Equals(x[s], Int(1)))
            constraints += 1

    # (7h)
    for s in I:
        if P[s] <= {1, 2, 3, 4}:
            solver.add_assertion(Equals(x[s], Int(1)))
            constraints += 1

    """Checking the Conjecture"""
    # Since this is a maximization problem, the cost of an optimal solution is
    # zero iff there exists a feasible solution with zero cost, and no solution
    # with positive cost is feasible.
    if should_solve:
        start_time = time.perf_counter()
        is_zero_feasible = solver.solve([Equals(cost, Int(0))])
        is_positive_feasible = solver.solve([cost > 0])
        end_time = time.perf_counter()
        does_conjecture_hold = is_zero_feasible and not is_positive_feasible
        runtime = end_time - start_time
    else:
        does_conjecture_hold = False
        runtime = -1

    solver.exit()

    return FormulationResult(
        name="opt_red",
        n=n,
        does_conjecture_hold=does_conjecture_hold,
        constraint_count=constraints,
        runtime=runtime,
    )
