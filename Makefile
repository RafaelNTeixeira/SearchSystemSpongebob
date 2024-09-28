# This is simply for easier process execs
.PHONY: all crawl clean
crawl:
	cd spongebobCrawler; \
	scrapy crawl season_spider

crawl-print:
	cd spongebobCrawler; \
	scrapy crawl season_spider -a enable_print=True
 

clean:
	rm data/raw/* -f