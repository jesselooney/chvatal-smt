import time
import argparse
from .formulations import formulations

formulation_dict = {f.__name__: f for f in formulations}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="chvatal_smt", description="Solve Chvatal's Conjecture using SAT or SMT"
    )
    parser.add_argument("formulation_name", choices=formulation_dict.keys())
    parser.add_argument(
        "n",
        type=int,
        help="The cardinality of the ground set on which to verify Chvatal's Conjecture",
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="Suppress intermediate output"
    )

    args = parser.parse_args()
    formulation_name = args.formulation_name
    n = args.n
    quiet = args.quiet

    formulation = formulation_dict.get(formulation_name)
    assert formulation is not None

    if not quiet:
        print(f"Checking the Conjecture for {n=} using formulation {formulation_name}")

    start_time = time.perf_counter()
    does_conjecture_hold = formulation(n)
    stop_time = time.perf_counter()

    runtime = stop_time - start_time

    if not quiet:
        print(f"Finished in {runtime:.3f} s")

        if does_conjecture_hold:
            print("Conjecture holds")
        else:
            print("Conjecture fails")

    print(
        f"formulation_name={formulation_name},{n=},{runtime=},{does_conjecture_hold=}"
    )
