from itertools import chain, combinations
from collections.abc import Iterable
from dataclasses import dataclass


# From https://docs.python.org/3/library/itertools.html
def powerset(iterable: Iterable) -> Iterable:
    """Subsequences of the iterable from shortest to longest."""
    # powerset([1,2,3]) → () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


def subsets(iterable: Iterable, n, m) -> Iterable:
    """Subsequences of the iterable from shortest to longest, with lengths in [n, m]"""
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(n, m + 1))


@dataclass
class FormulationResult:
    name: str
    n: int
    does_conjecture_hold: int
    constraint_count: int
    runtime: float

    def __str__(self):
        return f"name={self.name},n={self.n},does_conjecture_hold={self.does_conjecture_hold},constraint_count={self.constraint_count},runtime={self.runtime}"
