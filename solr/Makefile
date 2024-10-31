# This is simply for easier process execs
.PHONY: all solr_start solr_schema solr_populate

all:
	make solr_start
	sleep 3
	make solr_schema
	sleep 2
	make solr_populate
	sleep 2
	make index

solr_start:
	docker run -p 8983:8983 --name spongebob_solr -v ${PWD}:/data -d solr:9 solr-precreate episodes

solr_schema:
	curl -X POST -H 'Content-type:application/json' \
    --data-binary "@./schema.json" \
    http://localhost:8983/solr/episodes/schema

solr_populate:
	docker exec -it spongebob_solr bin/post -c episodes /data/spongebob.json

index:
	python indexTranscript.py