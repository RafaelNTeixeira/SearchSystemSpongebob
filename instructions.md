The crawler for the project can be run by executing the following commands:

```cd spongebobCrawler/```
```scrapy crawl season_spider -a enable_print=True```

Or simply: 

```make crawl```
```make crawl-print```

To run the project's analysis run the following command:

```python data/src/analyze.py```

Or simply: 

```make analyze```