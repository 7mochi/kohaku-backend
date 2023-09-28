shell:
	pipenv shell

install:
	PIPENV_VENV_IN_PROJECT=1 pipenv install

install-dev:
	PIPENV_VENV_IN_PROJECT=1 pipenv install --dev
	pipenv run pre-commit install

uninstall:
	pipenv --rm

lint:
	pipenv run pre-commit run --all-files

type-check:
	pipenv run mypy .

update:
	pipenv update --dev

clean:
	pipenv clean

run:
	pipenv run scripts/run_api.sh
