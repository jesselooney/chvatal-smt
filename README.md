# Info

This project translates the IP encodings of Chvátal's conjecture done by [Eifler et al.](https://arxiv.org/pdf/1809.01572) into SMT and SAT encodings in an effort to compare the strengths of each encoding type in automated theorem-proving.

COSC 345 Final Project. Allison Klingler, Jesse Looney, and Jonah McDonald. Amherst College.

# Setup
*Note: We observed that PBLib causes issues when running the SAT formulations on Windows.*
From the root directory of the repository, follow the subsequent steps to set everything up.

Create and enter a virtual environment:
```
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies:
```
pip install -r requirements.txt
```

Install a solver (e.g. Z3):
```
pysmt-install --z3
```
*Make sure to accept the licenses by entering 'y'.*

Now you should be able to run the package, in the format ```python -m chvatal_smt {encoding} {n}```, e.g.:
```
python -m chvatal_smt inf 3
```

# Development

Remember to develop in the virtual environment, and please record and commit any dependencies you add:
```
pip install foo
pip freeze > requirements.txt
```

Also, please format code with Ruff (included as a dependency):
```
ruff format
```

