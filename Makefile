# Linting and formatting
.PHONY: format lint lint-fix

format:
	uv run ruff format taiyo tests

lint:
	uv run ruff check taiyo tests

# Testing
.PHONY: test test-unit solr-up solr-down solr-logs test-integration

solr-up:
	docker compose up -d
	@echo "Waiting for Solr to be ready..."
	@i=0; while [ $$i -lt 30 ]; do \
		if curl -sf http://localhost:8983/solr/admin/info/system > /dev/null 2>&1; then \
			echo "Solr is ready!"; \
			exit 0; \
		fi; \
		echo "Waiting... ($$i/30)"; \
		sleep 2; \
		i=$$((i + 1)); \
	done; \
	echo "Solr failed to start"; \
	exit 1

solr-down:
	docker compose down

solr-logs:
	docker compose logs -f solr

solr-clean:
	docker compose down -v

test-integration: solr-up
	uv run pytest --cov=taiyo tests/integration || (docker compose down && exit 1)
	docker compose down

test-unit:
	uv run pytest --cov=taiyo tests/unit

test: test-unit test-integration

.PHONY: dev-setup

dev-setup:
	@echo "Setting up development environment using uv..."
	# Upgrade pip/setuptools in uv's environment then install editable package with dev extras
	uv run python -m pip install --upgrade pip setuptools wheel
	uv run pip install -e ".[dev]"

# Build and publish
.PHONY: build publish-dry-run publish-test publish

build:
	rm -rf dist
	uv build

publish-dry-run:
	uv publish --dry-run

publish-test:
	uv publish --publish-url https://test.pypi.org/legacy/

publish:
	uv publish

# Documentation
.PHONY: docs docs-serve docs-clean
docs:
	uv run zensical build

docs-serve:
	uv run zensical serve

docs-clean:
	uv run zensical clean
