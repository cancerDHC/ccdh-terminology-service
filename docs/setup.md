# Set Up CCDH Terminology Service

## Using Docker

This is the prefered approach to set up the service. You need to have
docker and docker-compose installed on your system before the set up. 

First copy the TCCM NCIT Turtle RDF to the docker import directory for neo4j. 

```shell
cp data/tccm/ncit-termci.ttl docker/neo4j/import
```

Create a .env file with required environment variables. 

The .env file should contain the following:

```
NEO4J_BOLT_URI=bolt://host:port
NEO4J_USERNAME=username
NEO4J_PASSWORD=password
NEO4J_HOST=ccdh-neo4j
NEO4J_BOLT_PORT=port

CDM_GOOGLE_SHEET_ID=google_sheet_id_to_the_CDM_definitions
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

## Rebuilding the docker image

If you use docker-compose to rebuild the ccdh-api image, you may see this error: 

```
error checking context: 'can't stat '/your/path/to/ccdh-terminology-service/docker/neo4j/conf''. 
```

You can reset the permission for that folder to the current user and rerun the build. 