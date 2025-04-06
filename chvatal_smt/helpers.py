from itertools import chain, combinations
from collections.abc import Iterable


# From https://docs.python.org/3/library/itertools.html
def powerset(iterable: Iterable) -> Iterable:
    """Subsequences of the iterable from shortest to longest."""
    # powerset([1,2,3]) → () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))
