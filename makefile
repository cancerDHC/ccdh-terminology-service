.PHONY: deploy-local deploy-local-prod deploy-local-test run run-outside-docker \
run-outside-docker-test delete-db delete-db-test

# Deploy
deploy-local: deploy-local-prod

deploy-local-prod:
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
