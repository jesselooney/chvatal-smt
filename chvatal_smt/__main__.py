import argparse
from .formulations import formulations
import sys

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
    parser.add_argument(
        "-d",
        "--dimacs-file",
        help="Output SAT constraints to a DIMACS file",
    )
    parser.add_argument(
        "-n",
        "--no-solve",
        action="store_true",
        help="Construct but do not solve the formulation",
    )

    args = parser.parse_args()

    formulation = formulation_dict.get(args.formulation_name)
    assert formulation is not None

    if not args.quiet:
        print(
            f"Checking the Conjecture for {args.n=} using formulation {args.formulation_name}"
        )

    if args.dimacs_file is not None:
        try:
            result = formulation(
                args.n, should_solve=not args.no_solve, dimacs_file=args.dimacs_file
            )
            sys.exit(0)
        except TypeError:
            raise Exception(
                f"Formulation {args.formulation_name} does not support DIMACS output"
            )
    else:
        result = formulation(args.n, should_solve=not args.no_solve)

    if not args.no_solve and not args.quiet:
        print(f"Finished in {result.runtime:.3f} s")

        if result.does_conjecture_hold:
            print("Conjecture holds")
        else:
            print("Conjecture fails")

    print(result)
