format:
	ruff format taiyo tests

lint:
	ruff check taiyo tests

test:
	python -m pytest tests/
