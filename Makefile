.PHONY: format lint lint-fix

format:
	uv run ruff format taiyo tests

lint:
	uv run ruff check taiyo tests

lint-fix:
	uv run ruff check --fix taiyo tests

.PHONY: test test-unit test-integration

test-unit:
	uv run pytest --cov=taiyo tests/unit

test-integration:
	uv run pytest --cov=taiyo tests/integration

test:
	test-unit test-integration

.PHONY: build publish

build:
	uv build

publish:
	uv publish --repository pypi
