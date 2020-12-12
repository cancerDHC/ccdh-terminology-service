#!/bin/bash

set -m # exit at the first error

# Start the primary process and put it in the background
/docker-entrypoint.sh neo4j &

/opt/initialize_neo4j.sh

fg %1