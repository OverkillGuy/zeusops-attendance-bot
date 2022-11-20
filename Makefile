DOCKER_IMAGE_NAME=zeusops-attendance-bot
APP_VERSION=$(shell poetry version --short)

.PHONY: all
all: install lint docs build install-hooks # test
# No tests yet, experimental

.PHONY: install
install:
	poetry install

# Enforce the pre-commit hooks
.PHONY: install-hooks
install-hooks:
	pre-commit install

.PHONY: lint
lint:  # Use all linters on all files (not just staged for commit)
	pre-commit run --all --all-files

# DEBUG="--debug"
DEBUG=""
.PHONY: run
run:
	sh -c "DISCORD_API_TOKEN=$(shell pass zeusops/attendance_bot_token) poetry run zeusops-attendance-bot ${DEBUG}"

# Not phony because real file
# Clean up the raw discord messages into ready to parse attendance file
processed_attendance.json: attendance.json
	poetry run python -c 'from zeusops_attendance_bot.preprocess import main; main()'

.PHONY: parse
parse: processed_attendance.json
	poetry run python -c 'from zeusops_attendance_bot.parsing import main; main()'

.PHONY: test
test:
	poetry run pytest

.PHONY: docs
docs:
	cd docs && make html

.PHONY: docs-serve
docs-serve:
	cd docs/build/html && python3 -m http.server

.PHONY: build
build:
	poetry build -f wheel

.PHONY: docker-build-release
docker-build-release:
	docker build \
		-t "${DOCKER_IMAGE_NAME}:${APP_VERSION}" \
		-f Dockerfile.release \
		.

.PHONY: docker-build-dev
docker-build-dev:
	docker build -t ${DOCKER_IMAGE_NAME}-dev .

# Make a release commit + tag, creating Changelog entry
# Set BUMP variable to any of poetry-supported (major, minor, patch)
# or number (1.2.3 etc), see 'poetry version' docs for details
.PHONY: release
# Default the bump to a patch (v1.2.3 -> v1.2.4)
release: BUMP=patch
release:
# Set the new version Makefile variable after the version bump
	$(eval NEW_VERSION := $(shell poetry version --short ${BUMP}))
	sed -i \
		"s/\(## \[Unreleased\]\)/\1\n\n\n## v${NEW_VERSION} - $(shell date -I)/" \
		CHANGELOG.md
	git add -A
	git commit -m "Bump to version v${NEW_VERSION}"
	git tag -a v${NEW_VERSION} \
		-m "Release v${NEW_VERSION}"

# Less commonly used commands

# Generate/update the poetry.lock file
.PHONY: lock
lock:
	poetry lock

# Update dependencies (within pyproject.toml specs)
# Update the lock-file at the same time
.PHONY: update
update:
	poetry update --lock

# Generate a pip-compatible requirements.txt
# From the poetry.lock. Mostly for CI use.
.PHONY: export-requirements
export-requirements:
	poetry run pip freeze > requirements.txt

# Install poetry from pip
# IMPORTANT: Make sure "pip" resolves to a virtualenv
# Or that you are happy with poetry installed system-wide
.PHONY: install-poetry
install-poetry:
	pip install poetry

# Ensure Poetry will generate virtualenv inside the git repo /.venv/
# rather than in a centralized location. This makes it possible to
# manipulate venv more simply
.PHONY: poetry-venv-local
poetry-venv-local:
	poetry config virtualenvs.in-project true

# Delete the virtualenv to clean dependencies
# Useful when switching to a branch with less dependencies
# Requires the virtualenv to be local (see "poetry-venv-local")
.PHONY: poetry-venv-nuke
poetry-venv-nuke:
	find .venv -delete
