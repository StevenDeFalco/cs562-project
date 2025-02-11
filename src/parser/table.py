import os
import pandas as pd

TABLES_DIRECTORY_PATH = '.tables'

def get_table(table_name):

    '''
    If the table information is not found, the first argument of the returned tuple will be None.
    The second argument will be False if the directory is not found.
    The second arguments will be True if the directory is found but the data files are not found.
    '''

    if table_name == '':
        return (None,False,False) 
    
    if not os.path.isdir(TABLES_DIRECTORY_PATH):
        os.mkdir(TABLES_DIRECTORY_PATH)
        return (None,False)
        
    table_dir_path = os.path.join(TABLES_DIRECTORY_PATH,table_name)
    if not os.path.isdir(table_dir_path):
        return (None,False)
        
    try:
        df = pd.read_csv(os.path.join(table_dir_path, 'table'), header=None)
        table = df.values.tolist()

        df = pd.read_csv(os.path.join(table_dir_path, 'columns'), header=None)
        column_datatypes = dict(zip(df[0], df[1]))
        
        return (table, column_datatypes)
    
    except Exception:
        return (None, True)


    
