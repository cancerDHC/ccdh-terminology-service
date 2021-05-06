CALL n10s.graphconfig.init();

DROP CONSTRAINT n10s_unique_uri IF EXISTS;
CREATE CONSTRAINT n10s_unique_uri ON (r:Resource) ASSERT r.uri IS UNIQUE;

CALL n10s.graphconfig.init({
  handleVocabUris: 'MAP'
});

CALL n10s.nsprefixes.add('neo4voc', 'http://neo4j.org/vocab/sw#');
