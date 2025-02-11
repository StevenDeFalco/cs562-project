# ExtendedSQL Syntax

This document contains information about ExtendedSQL queries. 

I will be providing examples as if I was writing a queries for the 'sales' table. If you would like to import the sales table into the application, follow the instructions that can be found in [/assets/load_sales_table.sql](../load_sales_table.sql). At the very least, it is recommended that you familiarize yourself with the structure of the table to better understand the examples provided.

## Table of Contents

- [Structure](#structure)
- [SELECT](#select)
- [FROM](#from)
- [OVER](#over)
- [WHERE](#where)
- [HAVING](#having)
- [ORDER BY](#order-by)


## Structure

The basic structure of ExtendedSQL is defined below.

```sh
SELECT [variables]
FROM [table]
OVER [groups]
WHERE [group conditions]
HAVING [aggregate conditions]
ORDER BY [variable order]
```

The query language has 7 keywords: SELECT, FROM, OVER, WHERE, SUCH THAT, HAVING, and ORDER BY. In the following sections, each keyword will be described in detail. Queries do not need all of the keywords to work, but a table must be chosen (in [FROM](#from)) and varaible projection (in [SELECT](#select)) must be performed for the query to produce an output.

Keep in mind that the query language is not case sensitive, including the keywords. Only string comparison in the WHERE and SUCH THAT clauses is case sensitive. 


## SELECT

The SELECT clause determines the output columns of the query. It contains two types of variables: grouping varaibles and aggregates. 

Grouping varaiables are the column names of the table that you want to find and structure the resulting table around. Note that ESQL automatically groups these varaibles, so all rows that contain the same combination of values in the columns of the grouping variables will be apart of the same row in the output.

Aggregates are what will be calculated for each combination of grouping values. Aggregates must always contain an aggregate function `(sum,avg,min,max,count)` and a column that contains numerical data (i.e. `quant` from the `sales` table) unless the aggregate function used is `count`. Aggregates have the ability to be apart of a group, which are defined in the [OVER](#over) clause. ESQL syntax exclusively utilizes dot notation with groups first, then the column, and the aggregate function always last. Therefore, aggregates can come in two forms: `column.function` or `group.column.function`.

If you wanted to write a query to compute the `maximum` value of `quant`, the `sum` of `quant` for group `g1`, and the `average` of `quant` for group `g2`, for the grouping variables cust and prod, you would write:

`SELECT cust, prod, quant.max, g1.quant.sum, g2.quant.avg`


## FROM

The FROM clause determines which table will be used for the query. To use the `sales` table in your query, you would write:

`FROM sales`

To use a table in your query, it must be imported into the application. Refer to [documentation](interface.md) on the ExtendedSQL interface to learn about how to do this.


## OVER

The OVER clause determines the names of the groups that are used to compute aggregates within the constraints set in the [SUCH THAT](#such-that) clause. These groups can be any name you want, and they are not case sensitive. It is recommended that group names are short and concise. It is recommended that group names should not include special characters, since they may cause unintended problems during parsing and execution. 

If you want to define two groups with the names `g1` and `g2`, like in the SELECT example above, you would write:

`OVER g1,g2`

The following is also a valid OVER clause:

`OVER apple, pear, banana, grapes`


## WHERE

The WHERE clause determines which rows in the original table will be used for computing the aggregates before groups are split in the [SUCH THAT](#such-that) clause. The WHERE clause determines all the rows that will be used to compute aggregates for aggregates without groups. These rows will also be filtered out before being filtered further for each group in the [SUCH THAT](#such-that) clause.

Currenly, the WHERE clause is made up conditions combined with `AND` and `OR`. It also supports the `NOT` operator for negation. There should be no varibales with dot notation, as the left side of comparision operators `(>,<,=,>=,<=,!=)` should be column names and the right side should be either a number, boolean, string, or date (which must match the value type of the column).

Below is an example of a valid WHERE clause:

`WHERE NOT (quant >= 500 AND state = 'CT')`


## SUCH THAT

The SUCH THAT clause determines which rows will be apart of calculating aggregates that are apart of different groups. The SUCH THAT clause should contain a section for each defined group in the [OVER](#over) clause. These sections are to be divided by commas. These sections must contain only one group and should not contain a group that is already defined in another section of the SUCH THAT clause.

The SUCH THAT clause must use dot notation to specify groups. For example, one section that defines a group to only contain the state 'NJ' or 'NY, assuming group `g1` is defined in the `OVER` clause:

`SUCH THAT g1.state = 'NJ' or g1.state = 'NY'`

If there were 4 groups named `q1`, `q2`, `q3`, and `q4`, the following would be a valid SUCH THAT clause:

```
SUCH THAT q1.month = 1 or q1.month = 2 or q1.month = 3,
          q2.month = 4 or q2.month = 5 or q2.month = 6,
          q3.month = 7 or q3.month = 8 or q3.month = 9,
          q4.month = 10 or q4.month = 11 or q4.month = 12
```


## HAVING

The HAVING clause determines which rows are displayed in the output. It contains a conditional statement based on aggregates.

Like in the `SELECT` clause, aggregates can come in the form `column.function` or `group.column.function`. The HAVING clause is not limited to the aggregates defined in the `SELECT` clause. The only limitation is that they must be contain an aggregate function `(sum,avg,min,max,count)` and a column that contains numerical data (i.e. `quant` from the `sales` table) unless the aggregate function used is `count`. They can also contain a valid group that was defined in the `OVER` clause.

If you would like the output to only contain rows where the `average quant` is greater than `3000`: you would write:

`HAVING quant.avg > 3000`

The HAVING clause supports parenthesis for order of operations, comparison symbols `(>, >=, <, <=, ==, !=)` and can use logic operators `(AND, OR, NOT)` to connect expressions. The HAVING clause must be able to be evaluated into a boolean value.

The following is a valid HAVING clause, assuming the groups `g1` and `g2` are defined in the `OVER` clause and the `sales` table is being used:

`HAVING g1.quant.sum < 1000 and (g2.quant.avg > 500 or g2.quant.min <= 20)`


## ORDER BY

The ORDER BY clause determines the order of the rows in the outputted table. It should be a number from 0 up to the amount of grouping variables (column names) in the SELECT clause.

ORDER BY will order rows alphabetically for every grouping variable included in the ORDER BY value. If value is 1, it will sort the rows by the first column alphabetically. If the value is 2, it will sort the first column first, and then sort the second column alphabetically while maintaining the order or the first column. This can repeat for each possible grouping value (starting with the first selected).

If the value is 0, it would work the same as not including the order by statement. The rows will be outputed in the order they are computed from the original table.

Using the example from the SELECT clause, the following would be a valid ORDER BY clause:

`ORDER BY 2`