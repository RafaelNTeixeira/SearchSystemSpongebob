# This is simply for easier process execs
.PHONY: solr down up schema populate index

solr:
	make up
	sleep 3
	make schema
	sleep 2
	make populate
	sleep 2
	make index

down:
	docker compose -f docker/docker-compose.yml down --remove-orphans -v

up:
	docker compose -f docker/docker-compose.yml up -d

schema:
	curl -X POST -H 'Content-type:application/json' \
    --data-binary "@./docker/data/schema.json" \
    http://localhost:8983/solr/episodes/schema

populate:
	docker exec -it spongebob_solr bin/post -c episodes /data/spongebob.json

index:
	python indexTranscript.py