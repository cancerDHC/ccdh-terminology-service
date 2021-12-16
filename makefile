.PHONY: deploy-local deploy-local-test run run-outside-docker \
run-outside-docker-test delete-db delete-db-test teardown teardown-test connect \
connect-test import destroy-and-deploy-local destroy-and-deploy-local-test

# Deploy
# destroy-and-deploy-local-local-force: After this, still need to run `make import`
destroy-and-deploy-local: delete-db teardown deploy-local connect
destroy-and-deploy-local-test: delete-db-test teardown-test deploy-local-test connect-test

deploy-local:
	@cp .env.prod .env; \
	docker-compose build; \
	docker-compose up -d

deploy-local-test:
	@cp .env.test .env; \
	docker-compose -f docker-compose-test.yml -p ccdh-test build; \
	docker-compose -f docker-compose-test.yml -p ccdh-test up -d

run: run-outside-docker

run-outside-docker:
	@cp .env.dev .env; \
	uvicorn ccdh.api.app:app $$ROOT_PATH --host 0.0.0.0 --port 8000

run-outside-docker-test:
	@cp .env.dev.test .env; \
	uvicorn ccdh.api.app:app $$ROOT_PATH --host 0.0.0.0 --port 8000

# Database management
delete-db:
	@echo Running script. If permission denied, use sudo.; \
	python3 scripts/delete_db.py --backup --env-name production

delete-db-test:
	@echo Running script. If permission denied, use sudo.; \
	python3 scripts/delete_db.py --backup --env-name test

# Container management
teardown:
	docker stop ccdh-api; docker rm ccdh-api; \
	docker stop ccdh-neo4j; docker rm ccdh-neo4j; \
	docker stop ccdh-redis; docker rm ccdh-redis

teardown-test:
	docker stop ccdh-api-test; docker rm ccdh-api-test; \
	docker stop ccdh-neo4j-test; docker rm ccdh-neo4j-test; \
	docker stop ccdh-redis-test; docker rm ccdh-redis-test

connect:
	docker exec -it ccdh-api /bin/bash

connect-test:
	docker exec -it ccdh-api-test /bin/bash

import:
	python -m ccdh.importers.importer
