.PHONY: format lint lint-fix

format:
	uv run ruff format taiyo tests

lint:
	uv run ruff check taiyo tests

.PHONY: test test-unit solr-up solr-down solr-logs test-integration

solr-up:
	docker-compose up -d
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
	docker-compose down

solr-logs:
	docker-compose logs -f solr

solr-clean:
	docker-compose down -v

test-integration: solr-up
	uv run pytest --cov=taiyo tests/integration || (docker-compose down && exit 1)
	docker-compose down

test-unit:
	uv run pytest --cov=taiyo tests/unit

test:
	test-unit test-integration


.PHONY: build publish

build:
	uv build

publish:
	uv publish --repository pypi
