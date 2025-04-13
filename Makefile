shell:
	poetry shell

lint:
	poetry run pre-commit run --all-files

type-check:
	poetry run mypy .

install:
	POETRY_VIRTUALENVS_IN_PROJECT=1 poetry install --no-root

install-dev:
	POETRY_VIRTUALENVS_IN_PROJECT=1 poetry install --no-root --with dev
	poetry run pre-commit install

uninstall:
	poetry env remove python

run:
	poetry run scripts/bootstrap.sh
