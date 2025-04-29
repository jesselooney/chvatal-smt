import time
import sys
from .formulations import formulations


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} formulation n")
        sys.exit(1)
    else:
        n = int(sys.argv[2])
        formulation_name = sys.argv[1]

    formulation_dict = {f.__name__: f for f in formulations}

    formulation = formulation_dict.get(formulation_name)
    if formulation is None:
        print(f"Invalid formulation identifier: {formulation_name}")
        sys.exit(1)

    print(f"Checking the Conjecture for {n=} using formulation {formulation_name}")

    startTime = time.perf_counter()
    does_conjecture_hold = formulation(n)
    stopTime = time.perf_counter()

    runtime = stopTime - startTime
    print(f"Finished in {runtime:.3f} s")

    if does_conjecture_hold:
        print("Conjecture holds")
    else:
        print("Conjecture fails")
