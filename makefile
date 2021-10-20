# Deploy
deploy-local: deploy-local-prod

deploy-local-prod:
	cd docker; \
	docker-compose build; \
	docker-compose up -d

deploy-local-test:
	cd docker; \
	docker-compose -f docker-compose-test.yml -p ccdh-test build; \
	docker-compose -f docker-compose-test.yml -p ccdh-test up -d

run:
	uvicorn ccdh.api.app:app $$ROOT_PATH --host 0.0.0.0 --port 8000
