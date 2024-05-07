import subprocess
from connect import get_database
from phi import PhiOperator
import os

def get_query_file_path():
    """Prompts the user for a query file, checks its existence, and returns the path.

    Returns:
        The path to the valid query file if it exists, or None otherwise.
    """

    # prints all names of queries
    files = os.listdir("./queries")
    print()
    for i in range(0, len(files), 2):
        try:
            print(f"{files[i]:<30}{files[i+1]}")
        except IndexError:
            print(files[i])
    print()

    while True:
        filename = input(f"Enter the query file name (in the 'queries' directory) "
                        "or leave blank to enter query parameters manually: ")
        
        if filename.strip() != "":
            file_path = os.path.join("queries", filename)  # Construct full path
            if os.path.exists(file_path):
                return file_path
            else:
                print(f"Error: File '{filename}' does not exist in the 'queries' directory.")

        else:
            with open('./queries/_tmpQuery.txt', 'w') as f:
                f.write("SELECT ATTRIBUTE(S):\n")
                s = input("Input values for S (comma-separated): ")
                f.write(s + '\n')
                n = input("Input number of grouping variables (integer): ")
                f.write("NUMBER OF GROUPING VARIABLES(n):\n")
                f.write(n + '\n')
                v = input("Input Grouping Attributes (comma-separated): ")
                f.write("GROUPING ATTRIBUTES(V):\n")
                f.write(v + '\n')
                f_vect = input("Input values of F-vector (comma-separated): ")
                f.write("F-VECT([F]):\n")
                if f_vect.strip() != '': 
                    f.write(f_vect + '\n')
                sig = input("Input select conditions (comma-separated): ")
                sigmas = sig.split(',') if len(sig.strip()) != 0 else []
                f.write("SELECT CONDITION-VECT([σ]):\n")
                for cond in sigmas:
                    f.write(cond.strip() + '\n')
                g = input("Input having clause (with spaces between different entities): ")
                f.write("HAVING_CONDITION(G):\n")
                f.write(g)
                print()
            return './queries/_tmpQuery.txt'


def main():
    
    # Gets the file path for the query input
    file_path = get_query_file_path()

    # Connects to the database
    database, columns, column_datatypes = get_database()


    # create the mf_struct
    processing = PhiOperator(file_path)
    processing.process_mf_struct(columns, column_datatypes)
    mf_struct = processing.mf_struct

    # remove the tmp file created for inputted query
    if file_path == './queries/_tmpQuery.txt':
        os.remove(file_path)

    # Get translation dictionary for database  columns (attribute name --> index)
    col_names = {}
    for i, attrib in enumerate(columns):
        col_names[attrib] = i

    # Ask if the user wants the resulting table sorted
    num_group_by = len(mf_struct['V'])
    order_by_ = input(f"\nInput the order by value (0 for none, {num_group_by} for all grouping attributes): ")
    try:
        order_by_ = int(order_by_) 
        order_by_ = num_group_by if order_by_ > num_group_by else order_by_
        order_by_ = 0 if order_by_ < 0 else order_by_
    except Exception:
        order_by_ = 0
    
    """
    This is the generator code. It should take in the MF structure and generate the code
    needed to run the query. That generated code should be saved to a 
    file (e.g. _generated.py) and then run.
    """

    body = """
    
    class H:
        '''Class to define one row in the H table'''
        def __init__(self, groupingAttributes, data, aggregates):
            self.groupingAttributes = groupingAttributes
            self.aggregates = aggregates
            self.data = data
            self.map = self.make_map()

        def __str__(self):
            result = ''
            for key, value in self.map.items():
                result += f"{key}: {value}, "
            return result

        def __repr__(self):
            return self.__str__()

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
    for i in range(1, numberGrouping + 1):
        # e.g. of ith_condition = state='NJ'
        ith_conditions = []
        # get (sigma) conditions for ith group 
        for cond in conditions:
            split_cond = cond.split(".")
            if split_cond[0] == str(i):
                ith_conditions.append(split_cond[1])
        #  e.g. of parsed_condition = (<idx-of-attribute>, <attrib-val>, <operator>)
        parsed_conditions = []
        for cond in ith_conditions:
            if '>' in cond and '=' not in cond:
                cl = cond.split('>')
                parsed_conditions.append(f'{cl[0]} > {cl[1]}')
            elif '<' in cond and '=' not in cond:
                cl = cond.split('<')
                parsed_conditions.append(f'{cl[0]} < {cl[1]}')
            elif '=' in cond and '>' not in cond and '<' not in cond:
                cl = cond.split('=')
                parsed_conditions.append(f'{cl[0]} == {cl[1]}')
            elif '<=' in cond:
                cl = cond.split('<=')
                parsed_conditions.append(f'{cl[0]} <= {cl[1]}')
            elif '>=' in cond:
                cl = cond.split('>=')
                parsed_conditions.append(f'{cl[0]} >= {cl[1]}')
        for row in db:
            allTrue = True
            for cond in parsed_conditions:
                # if condition is met, check next condition to determine if all true
                cond_list = cond.split()
                result_tokens = []
                for token in cond_list:
                    try: 
                        token_val = row[column_names[token]]
                        if isinstance(token_val, str):
                            token_val = "'" + token_val + "'"
                        if isinstance(token_val, datetime.date):
                            token_val = "'" + str(token_val) + "'"
                        result_tokens.append(str(token_val))
                    except:
                        result_tokens.append(str(token))
                logic_statement = " ".join(result_tokens)
                if not eval(logic_statement):
                    allTrue = False
            # if all conditions are met...
            if allTrue:
                # then update rows in H table
                groupingValues = []
                for var in groupingVariables:
                    groupingValues.append(row[column_names[var]])
                groupingValues = set(groupingValues)
                for h_row in hTable:
                    # find the h_row that we need to update, should exist already
                    if groupingValues == h_row.get_grouping_values():
                        for agg in fVector:
                            agg_list = agg.split('_')
                            if len(agg_list) == 3 and agg_list[0] == str(i):
                                h_row.set_attribute_value(agg, row)


    for h_row in hTable:
        for key, value in h_row.map.items():
            split_att = key.split('_')
            agg = split_att[1] if len(split_att) == 3 else split_att[0]
            if agg.lower() == 'avg':
                avg_val = round(h_row.map[key]['avg'], 2)
                h_row.map[key] = avg_val


    if len(havingClause) != 0:
        result_hTable = []
        # Iterate through each h_row to check if meets having condition
        for h_row in hTable:
            having_tokens = havingClause[0].split()
            result_tokens = []
            for token in having_tokens:
                token = '==' if token == '=' else token
                try: 
                    token_val = h_row.map[token]
                    result_tokens.append(str(token_val))
                except:
                    result_tokens.append(str(token))
            logic_statement = " ".join(result_tokens)
            if eval(logic_statement):
                result_hTable.append(h_row)
        hTable = result_hTable


    newHTable = []
    # project only the attributes given in the SELECT clause

    for h_row in hTable:
        projected_h_row = {}
        for key, value in h_row.map.items():
            if key in selectAttributes:
                projected_h_row[key] = value 
        newHTable.append(projected_h_row)
    
    if order_by != 0:
        sort_order = groupingVariables[:order_by]
        newHTable.sort(key=lambda x: tuple(x.get(key, '') for key in sort_order))

    hTable = newHTable


    """

    # Note: The f allows formatting with variables.
    #       Also, note the indentation is preserved.

    tmp = f"""
import os
import sys
import psycopg2
import psycopg2.extras
import tabulate
import datetime
from dotenv import load_dotenv
from connect import get_database

# DO NOT EDIT THIS FILE, IT IS GENERATED BY generator.py

selectAttributes = {mf_struct["S"]}
numberGrouping = {mf_struct["n"]}
groupingVariables = {mf_struct["V"]}
fVector = {mf_struct["F"]}
conditions = {mf_struct["sigma"]}
havingClause = {mf_struct["G"]}

db = {repr(database)}
column_names = {col_names}

order_by = {order_by_}

def main():
    {body}
    print(tabulate.tabulate(hTable, headers='keys', tablefmt='grid'))
    
if "__main__" == __name__:
    main()
    """

    # Write the generated code to a file
    open("_generated.py", "w").write(tmp)
    # Execute the generated code
    subprocess.run(["python", "_generated.py"])


if "__main__" == __name__:
    main()
