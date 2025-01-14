# This is simply for easier process execs
.PHONY: prepare_study_subset generate_synonyms solr down up schema populate index evaluate api semantic_search

solr:
	make down
	make processTranscript
	make prepare_study_subset
	make generate_synonyms
	make up
	sleep 3
	make create_cores
	make schema
	sleep 2
	make populate
	sleep 2
	make semantic_search
	make api

down:
	docker compose -f docker/docker-compose.yml down --remove-orphans -v

up:
	docker compose -f docker/docker-compose.yml up -d

processTranscript:
	python processTranscript.py

create_cores: 
	docker exec -it spongebob_solr solr create_core -c episodes
	docker exec -it spongebob_solr solr create_core -c schemaless_subset
	docker exec -it spongebob_solr solr create_core -c transcript_processed

schema:
	curl -X POST -H 'Content-type:application/json' \
    --data-binary "@./docker/data/schema.json" \
    http://localhost:8983/solr/episodes/schema
	curl -X POST -H 'Content-type:application/json' \
	--data-binary "@./docker/data/simple_schema.json" \
	http://localhost:8983/solr/schemaless_subset/schema
	curl -X POST -H 'Content-type:application/json' \
	--data-binary "@./docker/data/processedTranscript_schema.json" \
	http://localhost:8983/solr/transcript_processed/schema

populate:
	docker exec -it spongebob_solr bin/post -c episodes /data/spongebob.json
	docker exec -it spongebob_solr bin/post -c schemaless_subset /data/spongebob.json
	docker exec -it spongebob_solr bin/post -c transcript_processed /data/processedTranscript.json

api:
	uvicorn api:app --host 0.0.0.0 --port 8000 --reload

semantic_search:
	python scripts/get_embeddings.py

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

evaluate_all: 
	make evaluate_queries
	rm -f evaluation/map.txt
	make calculate_map_boosted
	make calculate_map_simple
	make calculate_map_semantic
	make calculate_map_transcript

evaluate_queries: $(foreach qN,$(QUERIES),evaluate_$(qN) evaluate_simple_$(qN) evaluate_semantic_$(qN) evaluate_transcript_$(qN))

calculate_map_simple: 
	python scripts/systems_map.py --avp_folder evaluation/avp_simple

calculate_map_boosted: 
	python scripts/systems_map.py --avp_folder evaluation/avp_boosted

calculate_map_semantic:
	python scripts/systems_map.py --avp_folder evaluation/avp_semantic

calculate_map_transcript:
	python scripts/systems_map.py --avp_folder evaluation/avp_transcript

define EVALUATE_RULE
evaluate_$(1):
	python scripts/query_solr.py --query queries/q$(1).json --uri http://localhost:8983/solr --collection episodes | \
	python scripts/solr2trec.py > evaluation/results_q$(1)_trec.txt && \
	cat qrels/qrels$(1).txt | python scripts/qrels2trec.py > evaluation/qrels_trec_q$(1).txt && \
	trec_eval evaluation/qrels_trec_q$(1).txt evaluation/results_q$(1)_trec.txt > evaluation/trec_eval_results/q$(1)_boosted.txt && \
	cat evaluation/results_q$(1)_trec.txt | python scripts/plot_pr.py --qrels evaluation/qrels_trec_q$(1).txt --output evaluation/prec_rec_q$(1).png  --output_avp evaluation/avp_boosted/q$(1).txt
endef
$(foreach qN,$(QUERIES),$(eval $(call EVALUATE_RULE,$(qN))))

define EVALUATE_SIMPLE_RULE
evaluate_simple_$(1):
	python scripts/query_solr.py --query queries/q$(1)_simple.json --uri http://localhost:8983/solr --collection schemaless_subset | \
	python scripts/solr2trec.py > evaluation/results_q$(1)_simple_trec.txt && \
	cat qrels/qrels$(1).txt | python scripts/qrels2trec.py > evaluation/qrels_trec_q$(1)_simple.txt && \
	trec_eval evaluation/qrels_trec_q$(1)_simple.txt evaluation/results_q$(1)_simple_trec.txt > evaluation/trec_eval_results/q$(1)_simple.txt && \
	cat evaluation/results_q$(1)_simple_trec.txt | python scripts/plot_pr.py --qrels evaluation/qrels_trec_q$(1)_simple.txt --output evaluation/prec_rec_q$(1)_simple.png --output_avp evaluation/avp_simple/q$(1).txt
endef
$(foreach qN,$(QUERIES),$(eval $(call EVALUATE_SIMPLE_RULE,$(qN))))

define EVALUATE_SEMANTIC_RULE
evaluate_semantic_$(1):
	python scripts/query_solr.py --query queries/q$(1).json --uri http://localhost:8983/solr --collection episodes --type semantic | \
	python scripts/solr2trec.py > evaluation/results_q$(1)_semantic_trec.txt && \
	cat qrels/qrels$(1).txt | python scripts/qrels2trec.py > evaluation/qrels_trec_q$(1)_semantic.txt && \
	trec_eval evaluation/qrels_trec_q$(1)_semantic.txt evaluation/results_q$(1)_semantic_trec.txt > evaluation/trec_eval_results/q$(1)_semantic.txt && \
	cat evaluation/results_q$(1)_semantic_trec.txt | python scripts/plot_pr.py --qrels evaluation/qrels_trec_q$(1)_semantic.txt --output evaluation/prec_rec_q$(1)_semantic.png --output_avp evaluation/avp_semantic/q$(1).txt
endef
$(foreach qN,$(QUERIES),$(eval $(call EVALUATE_SEMANTIC_RULE,$(qN))))

define EVALUATE_TRANSCRIPT_RULE
evaluate_transcript_$(1):
	python scripts/query_solr.py --query queries/q$(1).json --uri http://localhost:8983/solr --collection episodes --type transcript | \
	python scripts/solr2trec.py > evaluation/results_q$(1)_transcript_trec.txt && \
	cat qrels/qrels$(1).txt | python scripts/qrels2trec.py > evaluation/qrels_trec_q$(1)_transcript.txt && \
	trec_eval evaluation/qrels_trec_q$(1)_transcript.txt evaluation/results_q$(1)_transcript_trec.txt > evaluation/trec_eval_results/q$(1)_transcript.txt && \
	cat evaluation/results_q$(1)_transcript_trec.txt | python scripts/plot_pr.py --qrels evaluation/qrels_trec_q$(1)_transcript.txt --output evaluation/prec_rec_q$(1)_transcript.png --output_avp evaluation/avp_transcript/q$(1).txt
endef
$(foreach qN,$(QUERIES),$(eval $(call EVALUATE_TRANSCRIPT_RULE,$(qN))))
