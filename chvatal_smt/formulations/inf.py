"""This file implements an SMT encoding of Eifler et al.'s infeasability-based
formulation, following the formulae in the paper as closely as possible. Where
applicable, this file follows the conventions in chvatal_infprob.zpl in Eifler
et al.'s MILP implementation.
"""

from ..helpers import powerset
from collections.abc import Iterable, Set
from pysmt.typing import INT
from pysmt.shortcuts import Symbol, Plus, And, get_model, Solver


def inf(solver: Solver, n: int):
    # N is $[n]$
    N = range(0, n)

    # P is $2^[n]$
    P = list(map(set, powerset(N)))

    # I is an index set for P, so that each element of P corresponds to an integer.
    I = range(0, len(P))

    x = [Symbol(f"x{i}", INT) for i in I]
    y = [Symbol(f"y{i}", INT) for i in I]

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

    # downset inequalities (1b)
    downset_ineq = []
    for t in I:
        for s in I:
            if P[s] < P[t]:
                downset_ineq.append(x[t] <= x[s])

    # intersecting inequalities (1c)
    intersecting_ineq = []
    # Because addition is commutative, we currently generate duplicate constraints.
    for t in I:
        for s in I:
            # The requirements that P[t] and P[s] are nonempty may be able to be
            # omitted? This is what the authors do in their implementation.
            if len(P[t]) != 0 and len(P[s]) != 0 and len(P[t] & P[s]) == 0:
                intersecting_ineq.append(y[t] + y[s] <= 1)

    # containment inequalities (1d)
    containment_ineq = []
    for s in I:
        containment_ineq.append(y[s] <= x[s])

    # star inequalities (1e)
    star_ineq = []
    intersecting_family_cardinality = Plus([y[s] for s in I if len(P[s]) != 0])
    for i in N:
        downset_star_cardinality = Plus([x[s] for s in I if i in P[s]])
        star_ineq.append(
            downset_star_cardinality + 1 <= intersecting_family_cardinality
        )

    formula = And(
        domain_ineq + downset_ineq + intersecting_ineq + containment_ineq + star_ineq
    )
    solver.add_assertion(formula)
