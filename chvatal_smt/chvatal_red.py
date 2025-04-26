"""This file implements an SMT encoding of Eifler et al.'s reduction-based
formulation, following the formulae in the paper as closely as possible. Where
applicable, this file follows the conventions in chvatal_infprob_red.zpl and
chvatal_optprob_red.zpl in Eifler et al.'s MILP implementation.
"""

from helpers import powerset

from pysmt.typing import INT
from pysmt.shortcuts import Symbol, Plus, And, get_model, Equals, Int, GT

# The fixed $n$ the Conjecture is defined around.
n = 3

# N is $[n]$
N = range(0, n)

# P is $2^[n]$
P = list(map(set, powerset(N)))

# I is an index set for P, so that each element of P corresponds to an integer.
I = range(0, len(P))

x = [Symbol(f"x{i}", INT) for i in I]
y = [Symbol(f"y{i}", INT) for i in I]
z = Symbol("z", INT)

zero = Int(0)

# all constraints will become arrays of formula that we will And() together at the end

# constraining variables to certain domains
# Constrain x's and y's to [0, 1]
domain_ineq = []
for s in I:
    domain_ineq.append(0 <= x[s])
    domain_ineq.append(x[s] <= 1)
    domain_ineq.append(0 <= y[s])
    domain_ineq.append(y[s] <= 1)
# constrain z to positive integers
domain_ineq.append(0 <= z)

# constant to represent the powerset of 4
P4 = set(powerset([0, 1, 2, 3]))

# (7a) maximize the sum of y_s - z
# this reduction-based solver only works if the objective function value of an optimal solution is 0
# ie, sum of y_s - z = 0
# ie, UNSAT for f > 0 and SAT for f == 0
optimal_ineq = []
optimal_eq = []
objective_fnct = Plus([(y[s] - z) for s in I if len(P[s]) != 0])
optimal_ineq.append(GT(objective_fnct, zero))
optimal_eq.append(Equals(objective_fnct, zero))

# (7b) intersecting families
intersecting_ineq = []
for t in I:
    for s in I:
        # The requirements that P[t] and P[s] are nonempty may be able to be
        # omitted? This is what the authors do in their implementation.
        if len(P[t]) != 0 and len(P[s]) != 0 and len(P[t] & P[s]) == 0:
            intersecting_ineq.append(y[t] + y[s] <= 1)

# (7c) star property
star_ineq = []
# we need the "for i in N" here
for i in N:
    star_cardinality = Plus(x[s] for s in I if i in P[s])
    star_ineq.append(star_cardinality <= z)

# (7d) downset
downset_ineq = []
for t in I:
    for s in I:
        # if S is a subset of T, y_t =< x_s
        if P[s] <= P[t]:
            downset_ineq.append(y[t] <= x[s])

# (7e) corollary 2
corollary_ineq = []
y_sum = Plus([(2 * y[s]) for s in I if len(P[s]) != 0])
x_sum = Plus([x[s] for s in I])
corollary_ineq.append(y_sum <= x_sum)

# (7f-7h) other constraints introduced by conjecture
constraints = []
for s in I:
    # y_s = 0 for all S s.t. 1 <= |S| <= 2
    if len(P[s]) <= 2 and len(P[s]) >= 1:
        # NOTE: we are using <= + => to imply equality as we are restricted to inequalities
        constraints.append(y[s] <= 0)
        constraints.append(y[s] >= 0)
    # x_s = 1 for all |S| = 1
    if len(P[s]) == 1:
        constraints.append(x[s] <= 1)
        constraints.append(x[s] >= 1)
    # x_s = 1 for all subsets of [4] (powerset of 4)
    if P[s] <= P4:
        constraints.append(x[s] <= 1)
        constraints.append(x[s] >= 1)
    # NOTE: some duplicate constraints may be created here


formula = And(
    domain_ineq
    + intersecting_ineq
    + star_ineq
    + downset_ineq
    + corollary_ineq
    + constraints
    + optimal_ineq
)

formula2 = And(
    domain_ineq
    + intersecting_ineq
    + star_ineq
    + downset_ineq
    + corollary_ineq
    + constraints
    + optimal_eq
)

# run the solver
# GOAL: f > 0 is UNSAT and f == 0 is SAT
print("f > 0: ")
model = get_model(formula)
if model is not None:
    print(model)
else:
    print("UNSAT")

print("f == 0: ")
model2 = get_model(formula2)
if model2 is not None:
    print(model2)
else:
    print("UNSAT")
