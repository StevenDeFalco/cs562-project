import subprocess
from connect import get_database
from phi import PhiOperator
import os

def get_file_path():
  """Prompts the user for a query file, checks its existence, and returns the path.

  Returns:
      The path to the valid query file if it exists, or None otherwise.
  """
  while True:
    filename = input("Enter the query file name (in the 'queries' directory): ")
    file_path = os.path.join("queries", filename)  # Construct full path

    if os.path.exists(file_path):
      return file_path
    else:
      print(f"Error: File '{filename}' does not exist in the 'queries' directory.")

def main():
    """
    This is the generator code. It should take in the MF structure and generate the code
    needed to run the query. That generated code should be saved to a 
    file (e.g. _generated.py) and then run.
    """




    body = """


    column_names = {}
    # Get translation dictionary (attribute name --> index)
    for i, attrib in enumerate(columns):
        column_names[attrib] = i


        # h_table.append(H())
        # h_table[i].update_row(aggregate, row)
    
    class H:
        '''Class to define one row in the H table'''
        def __init__(self, groupingAttributes, data, aggregates):
            self.groupingAttributes = groupingAttributes
            self.aggregates = aggregates
            self.data = data
            self.map = self.make_map()

        def make_map(self):
            map = {}
            for att in self.groupingAttributes:
                idx = column_names[att]
                map[att] = self.data[idx]
            for aggre in self.aggregates:
                agg_list = aggre.split('_')
                # get the aggregate function (i.e. sum) and attribute (i.e. quant)
                if len(agg_list) == 2:
                    agg, att = agg_list[0], agg_list[1]    
                    att_idx = column_names[att]
                    att_val = row[att_idx]
                    if agg in ['sum', 'min', 'max']:
                        map[aggre] = att_val
                    elif agg == 'count':
                        map[aggre] = 1
                    elif agg == 'avg':
                        map[aggre] = {'sum': att_val, 'count': 1, 'avg': att_val}
                else:
                    agg, att = agg_list[1], agg_list[2]    
                    if agg in ['sum', 'count']:
                        map[aggre] = 0
                    elif agg == 'min':
                        map[aggre] = sys.maxsize
                    elif agg == 'max':
                        map[aggre] = - sys.maxsize - 1
                    elif agg == 'avg':
                        map[aggre] = {'sum': 0, 'count': 0, 'avg': 0}
            return map 

        def set_attribute_value(self, aggregate, row):
            # e.g. aggregate = '1_sum_quant' or 'sum_quant'
            agg_list = aggregate.split('_')
            # get the aggregate function (i.e. sum) and attribute (i.e. quant)
            if len(agg_list) == 2:
                agg, att = agg_list[0], agg_list[1]    
            else: 
                agg, att = agg_list[1], agg_list[2]
            att_idx = column_names[att]
            att_val = row[att_idx]
            # Perform appropriate update depending on aggregate
            if agg.lower() == 'sum':
                current = self.map[aggregate]
                new = current + att_val
                self.map[aggregate] = new
            elif agg.lower() == 'min':
                current = self.map[aggregate]
                if att_val < current:
                    self.map[aggregate] = att_val
            elif agg.lower() == 'max':
                current = self.map[aggregate]
                if att_val > current:
                    self.map[aggregate] = att_val
            elif agg.lower() == 'count':
                self.map[aggregate] += 1
            elif agg.lower() == 'avg':
                # e.g. self.map['1_avg_quant'] = {'sum': 150, 'count': 10, 'avg': 15}
                prev = self.map[aggregate]
                new_sum = prev['sum'] + att_val
                new_count = prev['count'] + 1
                self.map[aggregate] = {'sum': new_sum, 
                                       'count': new_count, 
                                       'avg': (new_sum/new_count)}
            
        def get_grouping_values(self):
            result_list = []
            for var in self.groupingAttributes:
                result_list.append(self.map[var])
            return set(result_list)


    hTable = []

    # First pass initialzing H table
    # iterate through each row of the sales database
    for row in db:
        groupingValues = []
        for var in groupingVariables:
            groupingValues.append(row[column_names[var]])
        groupingValues = set(groupingValues)
        inHTable= False
        for h_row in hTable:
            # if grouped row already exists in H table, update it
            if groupingValues == h_row.get_grouping_values():
                inHTable = True
                for agg in fVector:
                    agg_list = agg.split('_')
                    if len(agg_list) == 2:
                        h_row.set_attribute_value(agg, row)
                break
        # if not in H table, create new H table row and add to H table
        if not inHTable:
            new_h_row = H(groupingVariables, row, fVector)
            hTable.append(new_h_row)



    # One pass for each grouping variable
    '''for i in range(len(groupingVariables)):
        for row in db:
            '''
    """





    file_path = get_file_path()
    processing = PhiOperator(file_path)
    # TODO user input option instead of file path
    mf_struct = processing.mf_struct

    # Note: The f allows formatting with variables.
    #       Also, note the indentation is preserved.
    tmp = f"""
import os
import sys
import psycopg2
import psycopg2.extras
import tabulate
from dotenv import load_dotenv
from connect import get_database

# DO NOT EDIT THIS FILE, IT IS GENERATED BY generator.py

selectAttributes = {mf_struct["S"]}
numberGrouping = {mf_struct["n"]}
groupingVariables = {mf_struct["V"]}
fVector = {mf_struct["F"]}
conditions = {mf_struct["sigma"]}
havingClause = {mf_struct["G"]}

def main():
    db, columns = get_database()
    {body}
    print(hTable)
    
if "__main__" == __name__:
    main()
    """

    # Write the generated code to a file
    open("_generated.py", "w").write(tmp)
    # Execute the generated code
    subprocess.run(["python", "_generated.py"])


if "__main__" == __name__:
    main()
