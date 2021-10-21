# Deploy
deploy-local: deploy-local-prod

deploy-local-prod:
	@cp .env.prod .env; \
	docker-compose build; \
	docker-compose up -d' \
	rm .env

deploy-local-test:
	@cp .env.test .env; \
	docker-compose -f docker-compose-test.yml -p ccdh-test build; \
	docker-compose -f docker-compose-test.yml -p ccdh-test up -d; \
	rm .env

run:
	uvicorn ccdh.api.app:app $$ROOT_PATH --host 0.0.0.0 --port 8000
