# This is simply for easier process execs
.PHONY: clean requirements all crawl clean analyze

all: clean requirements crawl process analyze

requirements:
	pip install -r requirements.txt

crawl:
	cd spongebobCrawler; \
	scrapy crawl season_spider

crawl-print:
	cd spongebobCrawler; \
	scrapy crawl season_spider -a enable_print=True

process:
	python data/src/clean.py

analyze:
	python data/src/analyze.py

clean:
	rm -f data/raw/*
	rm -f data/clean/*
	rm -f data/documents/*