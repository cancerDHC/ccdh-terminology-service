#!/bin/bash

wget --quiet --tries=30 --waitretry=3 -O /dev/null http://localhost:7474
cypher-shell --file /cyphers/n10s-init.cypher
cypher-shell --file /cyphers/tccm-init.cypher
cypher-shell --file /cyphers/ccdh-init.cypher
cypher-shell --format plain "call n10s.nsprefixes.list()"

