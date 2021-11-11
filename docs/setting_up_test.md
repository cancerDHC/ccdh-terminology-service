# Setting up a testing server with dockers
## Environment files
First, you will want to have 2 clones of this repository. One should be for production ('prod'),
and the other for test.

To set up a testing server with docker containers, use `docker/docker-compose-test.yml`. 

Create a file `.env.test` in the `docker` directory. It should have similar content as `.env`. Then, you should back up
the prod `.env` file; e.g. you can copy it and can call it `.env.prod`.

The variables `NEO4J_HOST`, and `REDIS_URL` for `.env.test` need to be different 
than what is in `.env.prod`. The host names in the `.env.prod` and `.env.test` need 
to match the `container_name` or the
service name in `docker-compose.yml` and `docker-compose-test.yml` respectively.

### Example `.env.prod`
```sh
# .env file for running docker environments: prod
NEO4J_USERNAME=<username>
NEO4J_PASSWORD=<password>
NEO4J_HOST=ccdh-neo4j
NEO4J_BOLT_PORT=7687
REDIS_URL=redis://ccdh-redis:6379
USER_ACCESS_TOKEN=<token>
```

### Example `.env.test`
```sh
# .env file for running in docker environments: test
NEO4J_USERNAME=<username>
NEO4J_PASSWORD=<password>
NEO4J_HOST=ccdh-neo4j-test
NEO4J_BOLT_PORT=7687
REDIS_URL=redis://ccdh-redis-test:6380
USER_ACCESS_TOKEN=<token>

```

## Run the following to start up the containers.

```sh
make deploy-local-test
```

## And run the importer
```shell
docker exec -it ccdh-api-test /bin/bash
python -m ccdh.importers.importer
```

In the [`docker-compose`](https://docs.docker.com/compose/) command above, `-f` stands for `--file`, `-p` is 
for `--project-name`. We use this to avoid name collisions between the test/production containers. Running 
[with `up`](https://docs.docker.com/compose/reference/up/) builds, (re)creates, starts, and attaches to containers for 
a service. Finally, `-d` is for `--detach`, which runs the process in the background so that you can continue doing 
other things in your shell session.
