# SpongeBob SquarePants Search Engine

## Group T06G01
| Name             | Number    | E-Mail               |
| ---------------- | --------- | -------------------- |
| Carolina Gonçalves | 202108781 | up202108781@up.pt |
| José Isidro | 202006485 | up202006485@up.pt |
| Marco Costa | 202108821 | up202108821@up.pt |
| Rafael Teixeira | 202108831 | up202108831@up.pt |

## Prerequisites

In order to run this project, you need to have the following technologies installed:
- Python (This project was tested with python 3.12.6)
- Make
- Graphviz ([Download](https://graphviz.org/download/))

## How to run

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

To run the complete project run the following command: 

```make all```

To run the solr run the following command: 

```make solr```

You can access the solr dash board on: 

```http://localhost:8983/solr/#```
