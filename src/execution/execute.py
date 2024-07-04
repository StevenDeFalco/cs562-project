import os
import csv
import pandas as pd
import tabulate as tb

import src.parser.parse as parse
import src.execution.algorithms as algorithms


TABLES_DIRECTORY_PATH = '.tables'


def execute(query):


    ###temp###
    df = pd.read_csv(os.path.join(TABLES_DIRECTORY_PATH, 'sales/table'), header=None)
    table = df.values.tolist()

    df = pd.read_csv(os.path.join(TABLES_DIRECTORY_PATH, 'sales/column_datatypes'), header=None)
    column_datatypes = dict(zip(df[0], df[1]))
    
    df = pd.read_csv(os.path.join(TABLES_DIRECTORY_PATH, 'sales/columns'), header=None)
    columns = df[0].tolist()
    ##########
    


    processed_query = parse.get_processed_query(query,columns,column_datatypes)

    select_attributes = processed_query['select_clause']
    select_grouping_attributes = processed_query['select_grouping_attributes']
    aggregate_groups = processed_query['aggregate_groups']
    conditions = processed_query['conditions']
    having_clause = processed_query['having_clause']
    aggregates = processed_query['aggregates']
    order_by = processed_query['order_by']


    hTable = algorithms.build_hTable(select_grouping_attributes,aggregates,aggregate_groups,conditions,having_clause)
    select_table = algorithms.project_select_attributes(hTable,select_attributes)
    table = algorithms.order_by_sort(select_table,order_by,select_grouping_attributes) 

    '''
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
    '''

   

    



