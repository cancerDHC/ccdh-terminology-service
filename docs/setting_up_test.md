# Setting up a testing server with dockers
First, you will want to have 2 clones of this repository. One should be for production ('prod'), and the other for test.

To set up a testing server with docker containers, use `docker/docker-compose-test.yml`. 

Create a file `.env.test` in the `docker` directory. It should have similar content as `.env`. Then, you should back up
the prod `.env` file; e.g. you can copy it and can call it `.env.prod`.

The variable `NEO4J_BOLT_PORT` and `NEO4J_HOST` for `.env.test` need to be different than what is in `.env.prod` 

When you've finished your `.env.test` file, overwrite `.env` with those same exact contents. This is because `config.py`
will always look for `.env`, regardless of the environment. We plan to fix this in a future update.

Run the following to start up the containers.

```
cd docker
docker-compose -f docker-compose-test.yml build
docker-compose -f docker-compose-test.yml -p ccdh-test up -d
```

In the [`docker-compose`](https://docs.docker.com/compose/) command above, `-f` stands for `--file`, `-p` is 
for `--project-name`. We use this to avoid name collisions between the test/production containers. Running 
[with `up`](https://docs.docker.com/compose/reference/up/) builds, (re)creates, starts, and attaches to containers for 
a service. Finally, `-d` is for `--detach`, which runs the process in the background so that you can continue doing 
other things in your shell session.
