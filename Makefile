# This is simply for easier process execs
.PHONY: clean requirements all crawl clean analyze solr

all: clean requirements process analyze

requirements:
	pip install -r requirements.txt
	python -m spacy download en_core_web_sm

crawl:
	cd spongebobCrawler; \
	scrapy crawl season_spider

crawl-print:
	cd spongebobCrawler; \
	scrapy crawl season_spider -a enable_print=True

process:
	python data/src/process.py

analyze:
	python data/src/analyze.py

cleanRaw:
	rm -f data/raw/*

clean:
	rm -f data/clean/*
	rm -f data/documents/*

solr:
	cd solr; \
	make solr

solr-down:
	cd solr; \
	make down	