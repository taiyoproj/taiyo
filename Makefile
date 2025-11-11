.PHONY: format lint lint-fix
format:
	uv run ruff format taiyo tests

lint:
	uv run ruff check taiyo tests

lint-fix:
	ruff check --fix taiyo tests

.PHONY: test
test:
	uv run pytest tests/

.PHONY: build publish
build:
	uv build

publish:
	uv publish --repository pypi