.DEFAULT_GOAL := help

PYTHONPATH=
SHELL=bash
VENV=.venv
DOCKER_CMD=docker
MODULE_NAME=pgcron
PACKAGE_NAME=django-pgcron
EXEC_WRAPPER?=$(DOCKER_CMD) exec -it $(PACKAGE_NAME)
DATABASE_URL?=postgres://postgres:postgres@db:5432/postgres
DOCKER_RUN_ARGS?=-v ~/:/home/circleci -v $(shell pwd):/app -e EXEC_WRAPPER=""
DOCKER_RUN_CMD?=$(DOCKER_CMD) compose run --name $(PACKAGE_NAME) $(DOCKER_RUN_ARGS) -d app

VENV_BIN=$(VENV)/bin


.venv:  ## Activate the virtual environment, creating it if it doesn't exist
	@if [ ! -d "$(VENV)" ]; then \
		uv venv $(VENV); \
		echo "Virtual environment created at $(VENV)"; \
	else \
		echo "Virtual environment already exists at $(VENV)"; \
	fi

	source $(VENV_BIN)/activate

.PHONY: sync
sync:  ## Sync the virtual environment
	$(MAKE) .venv

	uv sync --all-groups

	@echo "Virtual environment setup complete."

.PHONY: lock
lock:  ## Lock the dependencies
	uv lock
	uv export > docs/requirements.txt --no-editable --no-hashes


.PHONY: lint
lint:  ## Run linting checks
	$(EXEC_WRAPPER) uv run ruff check .
	$(EXEC_WRAPPER) uv run ruff format --check
	$(EXEC_WRAPPER) uv run pyright

.PHONY: format
format:  ## Run code formatting
	uv run ruff check . --fix
	uv run ruff format .

.PHONY: test
test:  ## Run tests
	docker-compose run --rm \
		-v $(shell pwd):/app \
		-w /app \
		app uv run pytest

.PHONY: test-cov
test-cov:  ## Run tests and generate coverage report
	uv run pytest --cov --cov-report=html

.PHONY: open-cov
open-cov:  ## Open the coverage report in the browser
	uv run python -m webbrowser "file://$$(pwd)/htmlcov/index.html"

.PHONY: repl
repl:  ## Run a repl
	uv run ipython

.PHONY: help
help:  ## Display this help screen
	@echo -e "\033[1mAvailable commands:\033[0m"
	@grep -E '^[a-z.A-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}' | sort

# Sets up the local database
.PHONY: db-setup
db-setup:
	$(EXEC_WRAPPER) psql postgres -c "CREATE USER postgres;"
	$(EXEC_WRAPPER) psql postgres -c "ALTER USER postgres SUPERUSER;"
	$(EXEC_WRAPPER) psql postgres -c "CREATE DATABASE ${MODULE_NAME}_local OWNER postgres;"
	$(EXEC_WRAPPER) psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE ${MODULE_NAME}_local to postgres;"
	$(EXEC_WRAPPER) python manage.py migrate

# Sets up a conda development environment
.PHONY: conda-create
conda-create:
	-conda env create -f environment.yml -y

# Sets up a Conda development environment
.PHONY: conda-setup
conda-setup: EXEC_WRAPPER=conda run -n ${PACKAGE_NAME} --no-capture-output
conda-setup: conda-create lock sync db-setup

# Pull the latest container and start a detached run
.PHONY: docker-start
docker-start:
	$(DOCKER_CMD) compose pull
	$(DOCKER_RUN_CMD)

# Sets up a Docker development environment
.PHONY: docker-setup
docker-setup: docker-teardown docker-start lock sync

# Spin down docker resources
.PHONY: docker-teardown
docker-teardown:
	$(DOCKER_CMD) compose down --remove-orphans

.PHONY: shell
shell:
	$(EXEC_WRAPPER) /bin/bash

# Run a shell
.PHONY: shell
shell:
	$(EXEC_WRAPPER) /bin/bash

# Build the docs
.PHONY: docs
docs:
	uv run mkdocs build -s

# Serve the docs
.PHONY: docs-serve
docs-serve:
	uv run mkdocs serve
