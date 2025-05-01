"""This file implements an SMT encoding of Eifler et al.'s optimality-based
formulation, following the formulae in the paper as closely as possible. Where
applicable, this file follows the conventions in chvatal_optprob.zpl in Eifler
et al.'s MILP implementation.
"""

import sys
import time
from ..helpers import powerset
from pysat.solvers import Cadical195
from pysat.pb import PBEnc
from pysat.formula import IDPool


def inf_sat2(n: int):
    """Returns True iff downsets D such that |U(D)| <= n satisfy Chvatal's conjecture."""

    """Setup"""
    # N is [n] = {1, 2, ..., n}.
    N = list(range(1, n + 1))
    # P is 2^[n].
    P = list(map(set, powerset(N)))
    # I is an index set for P, so that each element of P corresponds to an integer.
    I = range(0, len(P))

    """Variables and domain constraints"""
    vpool = IDPool()
    x = [vpool.id(f"x{i}") for i in I]
    y = [vpool.id(f"y{i}") for i in I]

    clauses = []

    """Model constraints"""
    # The paper notes that we can use (3d) instead of (1b) and (1d).
    # S(x) contains the powerset of S(y) (3d).
    for t in I:
        for s in I:
            if P[s] <= P[t]:
                # y[t] implies x[s]
                clauses.append([x[s], -y[t]])

    # S(y)\{0} is an intersecting family (1c).
    for t in I:
        for s in I:
            if len(P[t]) != 0 and len(P[s]) != 0 and len(P[t] & P[s]) == 0:
                # at most one of y[t] or y[s] is true
                clauses.append([-y[t], -y[s]])

    # S(y)\{0} has greater cardinality than every star in S(x) (1e).
    for i in N:
        # TODO: explain this more clearly
        # We implement constraint (1e) using a pseudo-boolean constraint.
        star = [x[s] for s in I if i in P[s]]
        intersecting_family = [y[s] for s in I if len(P[s]) != 0]

        lits = intersecting_family + star
        # The weights mean that the sum will encode the cardinality of the
        # intersecting family minus the cardinality of the star.
        weights = [1] * len(intersecting_family) + [-1] * len(star)

        # TODO: verify that this is doing what I want it to
        cnfplus = PBEnc.geq(lits=lits, weights=weights, bound=1, vpool=vpool)
        clauses.extend(cnfplus.clauses)
    
    constraints = len(clauses) # don't count what comes after since that is just assigned variables, not really constraints
    # (Should I be counting them??)

    # Encodings of previously proven chvatal results
    for t in I:
        if 0 < len(P[t]) and len(P[t]) < 3:
            clauses.append([-y[t]]) # constraint 7f
        if len(P[t]) == 1:
            clauses.append([x[t]]) # constraint 7g
        elif P[t] <= set([1, 2, 3, 4]):
            clauses.append([x[t]]) # constraint 7h

    """Checking the Conjecture"""
    solver = Cadical195(bootstrap_with=clauses)
    result = solver.solve()
    solver.delete()

    print(f"{constraints} constraints")

    # The Conjecture holds iff these constraints are unsatisfiable.
    return not result


if __name__ == "__main__":
    start = time.perf_counter()
    result = inf_sat2(int(sys.argv[1]))
    end = time.perf_counter()
    print(f"Finished in {end - start} s")
    if result:
        print("Conjecture holds")
    else:
        print("Conjecture fails")
