# Setup

From the root directory of the repository, follow the subsequent steps to set everything up.

Create and enter a virtual environment:
```
make .venv
source .venv/bin/activate
```

Install the dependencies:
```
make install
```

Install a solver (e.g. Z3):
```
pysmt-install --z3
```
*Make sure to accept the licenses by entering 'y'.*

Now you should be able to run the package:
```
python -m chvatal_smt opt 3
```

# Development

Remember to develop in the virtual environment, and please record and commit any dependencies you add:
```
pip install foo
make freeze
```

Also, please format code with Ruff (included as a dependency):
```
ruff format
```

