# ExtendedSQL Syntax

This document contains information about ExtendedSQL queries. 

I will be providing examples as if I was writing a queries for the 'sales' table. If you would like to import the sales table into the application, follow the instructions that can be found in [/assets/load_sales_table.sql](../load_sales_table.sql). At the very least, I recommend familiarizing yourself with the structure of the table to better understand the examples provided.

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

The query language has 6 keywords: SELECT, FROM, OVER, WHERE, HAVING, and ORDER BY. In the following sections, each keyword will be described in detail. Queries do not need all of the keywords to work, but a table must be chosen and varaible selection must be made for the query to produce an output.

Keep in mind that the query language is not case sensitive, including the keywords. Only string comparison in the WHERE clause is case sensitive. 


## SELECT

The SELECT clause determines the output columns of the query. It contains two types of variables: grouping varaibles and aggregates. 

Grouping varaiables are the column names of the table that you want to find and structure the resulting table around. Note that ESQL automatically groups these varaibles, so all rows that contain the same combination of values in the columns of the grouping variables will be apart of the same row in the output.

Aggregates are what will be calculated for each combination of grouping values. Aggregates can either always contain an aggregate function (sum,avg,min,max,count) and a column that contains numerical data (i.e. `quant` from the `sales` table). Aggregates have the option of being apart of a group, which are defined in the OVER clause. Therefore, aggregate functions can come in two forms: `func_var` or `group_func_var`.

If you wanted to write a query to compute the `maximum` value of `quant`, the `sum` of `quant` for group `1`, and the `average` of `quant` for group `2`, for the columns cust and prod, you would write:

`SELECT cust, prod, max_quant, 1_sum_quant, 2_avg_quant`


## FROM

The FROM clause determines which table will be used for the query. To use the `sales` table in your query, you would write:

`FROM sales`

To use a table in your query, it must be imported into the application. Refer to [documentation](interface.md) on the ExtendedSQL interface to learn about how to do this.


## OVER

The OVER clause determines the names of the groups, which are used to compute aggregate functions outside of the grouping variables that were defined in the SELECT clause. These groups can be any name you want, and they are not case sensitive. It is recommended that group names are short and concise. Group names should also not have any special characters, or they could cause problems for the HAVING clause.

If you want to define two groups with the names `1` and `2`, like in the SELECT example above, you would write:

`OVER 1,2`

Remember that the group names are not limited to just numbers. The following is also a valid OVER clause:

`OVER apple, pear, banana, grapes`


## WHERE



## HAVING

The HAVING clause determines which rows are displayed in the output. It contains a conditional statement based on aggregate functions.

Like in the SELECT clause, aggregate functions can come in two forms: `func_var` or `group_func_var`. The HAVING clause is not limited to the aggregate functions found in the select clause. The only limitation is that they must be contain an aggregate function (sum,avg,min,max,count) and a column that contains numerical data (i.e. `quant` from the `sales` table). They can also contain a valid group that was defined in the OVER clause.

If you would like the output to only contain rows where the `average quant` is greater than `3000`: you would write:

`HAVING avg_quant > 3000`

The HAVING clause supports math symbols (+, -, *, /, %) and parenthesis for order of operations. You must use comparison symbols (>, >=, <, <=, ==, !=) and can use logic operators (and, or, not) to connect expressions. The HAVING clause must be able to be evaluated into a boolean value.

The following is a valid HAVING clause, assuming the groups `1` and `2` are defined in the over clause and the `sales` table is being used:

`HAVING 1_sum_quant < 1000 and (2_avg_quant > 500 or 1_max_quant + 2_min_quant >= 2000)`


## ORDER BY

The ORDER BY clause determines the order of the rows in the outputted table. It should be a number from 0 up to the amount of grouping variables (column names) in the SELECT clause.

ORDER BY will order rows alphabetically for every grouping variable included in the ORDER BY value. If value is 1, it will sort the rows by the first column alphabetically. If the value is 2, it will sort the first column first, and then sort the second column alphabetically while maintaining the order or the first column. This can repeat for each possible grouping value (starting with the first selected).

If the value is 0, it would work the same as not including the order by statement. The rows will be outputed in the order they are computed from the original table.

Using the example from the SELECT clause, the following would be a valid ORDER BY clause:

`ORDER BY 2`