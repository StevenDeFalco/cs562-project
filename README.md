# ExtendedSQL

## Description

ExntededSQL is an interface designed for the utilization of a new query language of the same name, or ESQL for short.

The new query language solves the biggest issue with SQL -- the inibility to compute aggregate functions outside of the grouping varaibles. ESQL is designed to be able to include mutiple aggregate queries for the five main aggregate functions (sum,avg,min,max,count), without the need of nested subqueries and repetitive selection, grouping, and aggregation.

This query language was based off of the SQL entention proposed in the two papers that can be found in `/assets/docs`, namely [MFQueries](/assets/docs/MFQueries.pdf) and [Ad-Hoc OLAP Query Processing](/assets/docs/Ad-Hoc_OLAP_Query_Processing.pdf). They propose a concept of the Phi Operator in relational agebra and the basic syntax of the language, as well as the algorithm used to compute the resulting relation. Read the article to learn more about the theory behind the query language.

This query language is utilized best when being used for OLAP (Online Analytical Processing) purposes and should be avoided if transactions are needed.


## Installation

Follow these steps to set up the project on your local machine.


### Prerequisites

Make sure that the following are installed on your local machine:

- [Python 3.6 or higher](https://www.python.org/downloads/)
- [PostgreSQL](https://www.postgresql.org/download/)
- [Git](https://git-scm.com/downloads)

### 1. Clone the repository
```sh
git clone https://github.com/lucasfhope/ExtendedSQL.git
cd ExtendedSQL
```

### 2. Set up a virtual envirnomnet

#### On macOS and Linux
```sh
python3 -m venv venv
source venv/bin/activate
```

#### On Windows
```sh
python -m venv venv
venv\Scripts\activate
```

### 3. Install the project and the dependencies
```sh
pip install .
```

### 4. Run the project
```sh
extendedsql
```

## Interface

## Syntax


