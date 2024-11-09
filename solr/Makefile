# This is simply for easier process execs
.PHONY: prepare_study_subset solr down up schema populate index evaluate

solr:
	make prepare_study_subset
	make up
	make testData
	sleep 3
	make schema
	sleep 2
	make populate
	# sleep 2
	# make index

down:
	docker compose -f docker/docker-compose.yml down --remove-orphans -v

up:
	docker compose -f docker/docker-compose.yml up -d

schema:
	curl -X POST -H 'Content-type:application/json' \
    --data-binary "@./docker/data/schema.json" \
    http://localhost:8983/solr/episodes/schema
	curl -X POST -H 'Content-type:application/json' \
    --data-binary "@./docker/data/schema.json" \
    http://localhost:8983/solr/test/schema
	curl -X POST -H 'Content-type:application/json' \
    --data-binary "@./docker/data/schema.json" \
    http://localhost:8983/solr/study_subset/schema

populate:
	docker exec -it spongebob_solr bin/post -c episodes /data/spongebob.json
	docker exec -it spongebob_solr bin/post -c test /data/test.json

	docker exec -it spongebob_solr bin/post -c study_subset /data/study_subset.json

index:
	python indexTranscript.py

prepare_study_subset: 
	python create_study_subset.py

# To run the evaluation, you can use the following command:
# make evaluate qN=1
qN=1 # default query number

evaluate:
	python scripts/query_solr.py --query queries/q$(qN).json --uri http://localhost:8983/solr --collection episodes | \
    python scripts/solr2trec.py > evaluation/results_q$(qN)_trec.txt && \
    cat qrels/qrels$(qN).txt | python scripts/qrels2trec.py > evaluation/qrels_trec_q$(qN).txt && \
    trec_eval evaluation/qrels_trec_q$(qN).txt evaluation/results_q$(qN)_trec.txt && \
    cat evaluation/results_q$(qN)_trec.txt | python scripts/plot_pr.py --qrels evaluation/qrels_trec_q$(qN).txt --output evaluation/prec_rec_q$(qN).png

testData:
	python makeTestData.py
