shell:
	pipenv shell

lint:
	pipenv run pre-commit run --all-files

install:
	PIPENV_VENV_IN_PROJECT=1 pipenv install

install-dev:
	PIPENV_VENV_IN_PROJECT=1 pipenv install --dev
	pipenv run pre-commit install

uninstall:
	pipenv --rm

update:
	pipenv update --dev

clean:
	pipenv clean

run-app:
	pipenv run scripts/bootstrap.sh

deploy:
	PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy
