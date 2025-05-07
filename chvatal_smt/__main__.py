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

    result = formulation(n)

    if not quiet:
        print(f"Finished in {result.runtime:.3f} s")

        if result.does_conjecture_hold:
            print("Conjecture holds")
        else:
            print("Conjecture fails")

    print(result)
