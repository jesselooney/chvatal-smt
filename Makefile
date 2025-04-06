nothing:
	@echo -n ""

.venv:
	python3 -m venv .venv

freeze:
	pip freeze > requirements.txt

install:
	pip install -r requirements.txt	

.PHONY: nothing freeze install
