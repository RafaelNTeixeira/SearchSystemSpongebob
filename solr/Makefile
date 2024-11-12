# This is simply for easier process execs
.PHONY: prepare_study_subset generate_synonyms solr down up schema populate index evaluate

solr:
	make prepare_study_subset
	make generate_synonyms
	make up
	sleep 3
	make create_cores
	make schema
	sleep 2
	make populate

down:
	docker compose -f docker/docker-compose.yml down --remove-orphans -v

up:
	docker compose -f docker/docker-compose.yml up -d

create_cores: 
	docker exec -it spongebob_solr solr create_core -c episodes
	docker exec -it spongebob_solr solr create_core -c schemaless_subset
	docker exec -it spongebob_solr solr create_core -c study_subset

schema:
	curl -X POST -H 'Content-type:application/json' \
    --data-binary "@./docker/data/schema.json" \
    http://localhost:8983/solr/episodes/schema
	curl -X POST -H 'Content-type:application/json' \
    --data-binary "@./docker/data/schema.json" \
    http://localhost:8983/solr/study_subset/schema

populate:
	docker exec -it spongebob_solr bin/post -c episodes /data/spongebob.json
	docker exec -it spongebob_solr bin/post -c schemaless_subset /data/study_subset.json
	docker exec -it spongebob_solr bin/post -c study_subset /data/study_subset.json

prepare_study_subset: 
	python create_study_subset.py

generate_synonyms: 
	python generate_synonyms.py

# To run the evaluation, you can use the following command:
# make evaluate queries_folder=queries collection=study_subset qN=1,
# where collection is the collection to be evaluated and  qN is the query number.
queries_folder=queries
collection=study_subset
qN=1

evaluate:
	python scripts/query_solr.py --query $(queries_folder)/q$(qN).json --uri http://localhost:8983/solr --collection $(collection) | \
    python scripts/solr2trec.py > evaluation/results_q$(qN)_trec.txt && \
    cat qrels/qrels$(qN).txt | python scripts/qrels2trec.py > evaluation/qrels_trec_q$(qN).txt && \
    trec_eval evaluation/qrels_trec_q$(qN).txt evaluation/results_q$(qN)_trec.txt && \
    cat evaluation/results_q$(qN)_trec.txt | python scripts/plot_pr.py --qrels evaluation/qrels_trec_q$(qN).txt --output evaluation/prec_rec_q$(qN).png

