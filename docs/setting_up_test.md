# Setting up a testing server with dockers

To set up a testing server with docker containers, use `docker/docker-compose-test.yml`. 

Create a file `.env.test` in the `docker` directory. It should have similar content as `.env`. 

The variable 'NEO4J_HOST' needs to be `ccdh-neo4j-test`. 

```
NEO4J_HOST=ccdh-neo4j-test
```

If the testing server and the "prod" server is on the same machine, make sure the NEO4J_BOLT_PORT is not using the same port as what's in `.env`. 


```
cd docker
docker-compose -f docker-compose-test.yml -p ccdh-test
docker-compose -f docker-compose-test.yml -p ccdh-test up
```