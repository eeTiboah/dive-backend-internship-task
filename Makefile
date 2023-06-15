
SHELL := /bin/bash

define setup
	python3 -m venv venv \
	&& source ./venv/bin/activate \
	&& pip install poetry \
	&& poetry install \
	&& source venv/bin/activate
endef

define activate_venv
	source ./venv/bin/activate
endef

t.setup_venv:
	$(call setup)

t.activate:
	$(call activate_venv)

t.start:
	uvicorn src.main:app --reload

t.clean:
	rm -rf venv