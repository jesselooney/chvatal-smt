import time
from pysmt.shortcuts import Solver
from typing import Callable
from pysmt.solvers.solver import Model


def solve_with_encoding(
    encoding: Callable[[Solver, int], None], n: int
) -> (Model, float):
    # TODO: instantiate solver with explicit configuration for reproducability?
    with Solver() as solver:
        encoding(solver, n)

        start_time = time.perf_counter()
        solver.solve()
        end_time = time.perf_counter()

        runtime = end_time - start_time

        model = solver.get_model()

    return model, runtime

