# Quick start

Clone this repo, and pull the submodules. 

```shell
git clone 
git submodule update --init --recursive
```

Because the PDC json files are under Git LFS (Large File Storage), it must be installed in the repository. Follow [these instrucions](https://git-lfs.github.com/) for installling Git LFS on your machine. Then, install it in the repo via `git lfs install`. Then, pull the content with git lfs.

```shell
cd crdc-nodes/PDC-Public/documentation/prod/json
git lfs pull --include ./*.json
```

## Using Docker

This is the prefered approach to set up the service. You need to have
docker and docker-compose installed on your system before the set up. 

First copy the TCCM NCIT Turtle RDF to the docker import directory for neo4j. 

```shell
cp data/tccm/ncit-termci.ttl docker/neo4j/import
```

In the `docker/` folder, Create a `.env` file with required environment variables.

The `.env` file should contain the following:

```
NEO4J_BOLT_URI=bolt://ccdh-neo4j:7687
NEO4J_USERNAME=<username>
NEO4J_PASSWORD=<password>
NEO4J_HOST=ccdh-neo4j
NEO4J_BOLT_PORT=7687
USER_ACCESS_TOKEN=token
```

Choose a <username> and <password>. As for `USER_ACCESS_TOKEN`, this is used for [GitHub workflow integration](https://docs.github.com/en/actions/reference/authentication-in-a-workflow) with the [CCDH Model repository](https://github.com/cancerDHC/ccdhmodel). If you have access to that repository, you should use a [GitHub personal access token](https://docs.github.com/en/github/authenticating-to-github/keeping-your-account-and-data-secure/creating-a-personal-access-token) and set `USER_ACCESS_TOKEN` to that. The port, host, and 'bolt uri' have been auto-filled for you, but these are configurable if you want to change them.

By default, the importer will pull the CRDC-H YAML from the main branch of the ccdhmodel GitHub repo. 
If another branch is preferred, you can add this line in the .env file.

```shell
CCDHMODEL_BRANCH=ccdhmodel_branch_name_or_full_sha_commit_id
```

Then run the docker-compose build to build the images

```shell
cd docker
docker-compose build
```

If everything works, spin up the containers

```shell
docker-compose up
```

After the docker containers are up, log onto the ccdh-api container and
load data. 

```shell
docker exec -it ccdh-api /bin/bash
python -m ccdh.importers.importer
```

After data is loaded, the server will be running on a local port at 7070. You can visit
http://localhost:7070. 
