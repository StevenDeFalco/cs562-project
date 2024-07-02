from src.parser.parser import Parser
import src.execution.execution_algorithms as algorithms

import csv
from tabulate import tabulate


def main():
    
    # Gets the file path for the query input
    file_path = 'query.txt'

    # Connects to the database
    datatable, columns, column_datatypes = get_database()
    #datatable = repr(datatable)

    # Get translation dictionary for database  columns (attribute name --> index)
    column_indexes = {}
    for i, attribute in enumerate(columns):
        column_indexes[attribute] = i
    algorithms.set_datatable_information(datatable, column_indexes)

    # get the parsed query struct
    process_query = Parser(file_path,columns,column_datatypes)
    query_struct = process_query.query_struct

    select_attributes = query_struct['select_clause']
    select_grouping_attributes = query_struct['select_grouping_attributes']
    aggregate_groups = query_struct['aggregate_groups']
    conditions = query_struct['conditions']
    having_clause = query_struct['having_clause']
    aggregates = query_struct['aggregates']
    order_by = query_struct['order_by']


    table = algorithms.build_resulting_table(select_attributes,select_grouping_attributes,aggregates,aggregate_groups,conditions,having_clause,order_by)
   
    # Write data to a csv file
    headers = table[0].keys()
    with open("table.csv", "w", newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(table)

    # Read the CSV file into a list of dictionaries
    table = []
    with open('table.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        table = [row for row in reader]

    # Print the data as a table
    print(tabulate(table, headers="keys", tablefmt="grid"))



if "__main__" == __name__:
    main()
