deploy-local: deploy-local-prod

deploy-local-prod:
	cd docker; \
	docker-compose build; \
	docker-compose up -d

deploy-local-test:
	cd docker; \
	docker-compose -f docker-compose-test.yml -p ccdh-test build; \
	docker-compose -f docker-compose-test.yml -p ccdh-test up -d
