import os
import shutil
import csv
import psycopg2
import psycopg2.extras
from src.connect.postgres_oids import NUMERICAL_OIDs, STRING_OIDs, DATE_OID, BOOLEAN_OID

TABLES_DIRECTORY_PATH = '.tables'

def import_table(table, username,password,host,port):
    
    try:
        conn = psycopg2.connect(
            host=host,
            dbname='postgres',
            user=username,
            password=password, 
            port=port,
            cursor_factory=psycopg2.extras.DictCursor)
    except Exception:
        raise Exception("Unable to import table from PostgreSQL. Ensure that PostgreSQL is currently running and the table name, Username, Password, Host, and Port inputs are correct")
    
    cur = conn.cursor()
    cur.execute("SELECT * FROM " + table)

    columns = [desc[0] for desc in cur.description]
    datatypes = [desc[1] for desc in cur.description]

    column_datatypes = {}
    for i in range(len(columns)):
        # Map OIDs to human-readable data types
        if datatypes[i] in NUMERICAL_OIDs:
            column_datatypes[columns[i]] = 'numeric'
        elif datatypes[i] in STRING_OIDs:
            column_datatypes[columns[i]] = 'string'
        elif datatypes[i] == DATE_OID:
            column_datatypes[columns[i]] = 'date'
        elif datatypes[i] == BOOLEAN_OID:
            column_datatypes[columns[i]] = 'boolean'
        else:
            column_datatypes[columns[i]] = 'unknown'  # Handle unknown types

    if not os.path.isdir(TABLES_DIRECTORY_PATH):
        os.mkdir(TABLES_DIRECTORY_PATH)

    new_table_dir = os.path.join(TABLES_DIRECTORY_PATH,table.lower())
    if os.path.isdir(new_table_dir):
        raise Exception("Table with the name " + table.lower() + " already exists. Delete the current " + table.lower() + " table or change the name in PostgreSQL.")
    
    os.mkdir(new_table_dir)

    datatable_path = os.path.join(new_table_dir,"table")
    columns_path = os.path.join(new_table_dir,"columns")

    try:
        with open(datatable_path, 'w') as file:
            writer = csv.writer(file)
            writer.writerows(cur.fetchall())

        with open(columns_path, 'w') as file:
            writer = csv.writer(file)
            for key, value in column_datatypes.items():
                writer.writerow([key, value])

    except Exception as e:
        shutil.rmtree(new_table_dir)
        raise Exception("Could not write data to file.")



        


    
    

