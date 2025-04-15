import time
from pysmt.shortcuts import Solver
from typing import Callable
from pysmt.solvers.solver import Model
from .formulations import inf


def solve_with_encoding(
    encoding: Callable[[Solver, int], None], n: int
) -> (Model, float):
    # TODO: instantiate solver with explicit configuration for reproducability?
    with Solver() as solver:
        encoding(solver, n)

        start_time = time.perf_counter()
        is_satisfiable = solver.solve()
        end_time = time.perf_counter()

        runtime = end_time - start_time

        model = solver.get_model() if is_satisfiable else None

    return model, runtime


if __name__ == "__main__":
    model, runtime = solve_with_encoding(inf, 3)
    print(model)
    print(runtime)
