
SHELL := /bin/bash

define setup
	python3 -m venv venv \
	&& source ./venv/bin/activate \
	&& pip install poetry \
	&& poetry install
endef

define activate_venv
	source ./venv/bin/activate
endef

t.setup_venv:
	$(call setup)

t.activate:
	$(call activate_venv)

t.format:
	$(call activate_venv) && poetry run black .

t.lint:
	$(call activate_venv) && poetry run flake8 .


t.start:
	docker-compose up -d
	sleep 2
	uvicorn src.main:app --reload

t.remove:
	$(call activate_venv) && poetry run autoflake --remove-all-unused-imports --recursive --in-place --exclude=venv,alembic .

t.test:
	$(call activate_venv) && pytest

t.clean:
	rm -rf venv