# This is simply for easier process execs
.PHONY: all crawl clean analyze

all: crawl analyze

crawl:
	cd spongebobCrawler; \
	scrapy crawl season_spider

crawl-print:
	cd spongebobCrawler; \
	scrapy crawl season_spider -a enable_print=True
 
analyze:
	python data/src/analyze.py
clean:
	rm data/raw/* -f
	rm data/clean/* -f
	rm data/documents/* -f