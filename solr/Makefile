# This is simply for easier process execs
.PHONY: prepare_study_subset generate_synonyms solr down up schema populate index evaluate api semantic_search

solr:
	make prepare_study_subset
	make generate_synonyms
	make up
	sleep 3
	make create_cores
	make schema
	sleep 2
	make populate
	sleep 2
	make api
	make semantic_search

down:
	docker compose -f docker/docker-compose.yml down --remove-orphans -v

up:
	docker compose -f docker/docker-compose.yml up -d

create_cores: 
	docker exec -it spongebob_solr solr create_core -c episodes
	docker exec -it spongebob_solr solr create_core -c schemaless_subset

schema:
	curl -X POST -H 'Content-type:application/json' \
    --data-binary "@./docker/data/schema.json" \
    http://localhost:8983/solr/episodes/schema
	curl -X POST -H 'Content-type:application/json' \
	--data-binary "@./docker/data/simple_schema.json" \
	http://localhost:8983/solr/schemaless_subset/schema

populate:
	docker exec -it spongebob_solr bin/post -c episodes /data/spongebob.json
	docker exec -it spongebob_solr bin/post -c schemaless_subset /data/spongebob.json

api:
	uvicorn api:app --host 0.0.0.0 --port 8000 --reload

semantic_search:
	python semantic_search/get_embeddings.py

prepare_study_subset: 
	python create_study_subset.py

generate_synonyms: 
	python generate_synonyms.py

# To run the evaluation, you can use the following command:
# make evaluate queries_folder=queries collection=study_subset qN=1,
# where collection is the collection to be evaluated and  qN is the query number.
qN=1

# QUERIES := 1 2 3 4
# evaluate_all:
# 	# evaluate and evaluate_simple for 1 to 4


# evaluate:
# 	python scripts/query_solr.py --query queries/q$(qN).json --uri http://localhost:8983/solr --collection episodes | \
#     python scripts/solr2trec.py > evaluation/results_q$(qN)_trec.txt && \
#     cat qrels/qrels$(qN).txt | python scripts/qrels2trec.py > evaluation/qrels_trec_q$(qN).txt && \
#     trec_eval evaluation/qrels_trec_q$(qN).txt evaluation/results_q$(qN)_trec.txt && \
#     cat evaluation/results_q$(qN)_trec.txt | python scripts/plot_pr.py --qrels evaluation/qrels_trec_q$(qN).txt --output evaluation/prec_rec_q$(qN).png

# evaluate_simple:
# 	python scripts/query_solr.py --query queries/q$(qN)_simple.json --uri http://localhost:8983/solr --collection schemaless_subset | \
#     python scripts/solr2trec.py > evaluation/results_q$(qN)_simple_trec.txt && \
#     cat qrels/qrels$(qN).txt | python scripts/qrels2trec.py > evaluation/qrels_trec_q$(qN)_simple.txt && \
#     trec_eval evaluation/qrels_trec_q$(qN)_simple.txt evaluation/results_q$(qN)_simple_trec.txt && \
#     cat evaluation/results_q$(qN)_simple_trec.txt | python scripts/plot_pr.py --qrels evaluation/qrels_trec_q$(qN)_simple.txt --output evaluation/prec_rec_q$(qN)_simple.png


QUERIES := 1 2 3 4

evaluate_all: $(foreach qN,$(QUERIES),evaluate_$(qN) evaluate_simple_$(qN))

define EVALUATE_RULE
evaluate_$(1):
	python scripts/query_solr.py --query queries/q$(1).json --uri http://localhost:8983/solr --collection episodes | \
	python scripts/solr2trec.py > evaluation/results_q$(1)_trec.txt && \
	cat qrels/qrels$(1).txt | python scripts/qrels2trec.py > evaluation/qrels_trec_q$(1).txt && \
	trec_eval evaluation/qrels_trec_q$(1).txt evaluation/results_q$(1)_trec.txt && \
	cat evaluation/results_q$(1)_trec.txt | python scripts/plot_pr.py --qrels evaluation/qrels_trec_q$(1).txt --output evaluation/prec_rec_q$(1).png
endef
$(foreach qN,$(QUERIES),$(eval $(call EVALUATE_RULE,$(qN))))

define EVALUATE_SIMPLE_RULE
evaluate_simple_$(1):
	python scripts/query_solr.py --query queries/q$(1)_simple.json --uri http://localhost:8983/solr --collection schemaless_subset | \
	python scripts/solr2trec.py > evaluation/results_q$(1)_simple_trec.txt && \
	cat qrels/qrels$(1).txt | python scripts/qrels2trec.py > evaluation/qrels_trec_q$(1)_simple.txt && \
	trec_eval evaluation/qrels_trec_q$(1)_simple.txt evaluation/results_q$(1)_simple_trec.txt && \
	cat evaluation/results_q$(1)_simple_trec.txt | python scripts/plot_pr.py --qrels evaluation/qrels_trec_q$(1)_simple.txt --output evaluation/prec_rec_q$(1)_simple.png
endef
$(foreach qN,$(QUERIES),$(eval $(call EVALUATE_SIMPLE_RULE,$(qN))))
