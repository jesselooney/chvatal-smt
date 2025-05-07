#!/bin/bash

formulations=("inf" "opt" "opt_red" "inf_sat" "inf_sat_red")
ns=(5 6 7)

for formulation in "${formulations[@]}"; do
    for n in "${ns[@]}"; do
        python -m chvatal_smt "$formulation" "$n" --no-solve --quiet
    done
done
