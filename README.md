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

Before running the project please install the contents of the "requirments.txt" file. You can do so by running: 

```make requirements```

The crawler for the project can be run by executing the following commands:

```make crawl```

To run the project's analysis run the following command:

```make process```
```make analyze```

To access the Apache Solr's dash board run the following command: 

```make solr```

You can access the dash board on: 

```http://localhost:8983/solr/#```

