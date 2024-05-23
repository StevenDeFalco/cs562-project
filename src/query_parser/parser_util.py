
import re
from datetime import datetime

# OIDs for datatypes in postgreSQL
NUMERICAL_OIDs = [21, 23, 20, 1700, 700, 701]
STRING_OIDs = [25, 1042, 1043]
DATE_OID = 1082
BOOLEAN_OID = 16


def is_valid_condition(condition_no_group,column_names,column_datatypes):

    condition_split = []
    conditional_operators = ['=','!=','<=','>=','<','>']

    for operator in conditional_operators:
        if operator in condition_no_group:
            condition_split =  condition_no_group.split(operator)
            break
    
    if len(condition_split) == 2:
        left_side = condition_split[0].strip()
        right_side = condition_split[1].strip()
        
        if left_side in column_names:
            datatype = column_datatypes[left_side]

            # right side of numerical datatypes can have math operations, numbers, and data from columns that are numerical
            # check if the right side of the condition can be evaluated as a number
            if datatype in NUMERICAL_OIDs:
                numerical_columns = [column for column in column_names if column_datatypes.get(column) in NUMERICAL_OIDs]
                numerical_columns.sort(reversed=True)
                
                for column in numerical_columns:
                    pattern = r'\b' + re.escape(column) + r'\b'
                    right_side = re.sub(pattern, '1', right_side)

                try:
                    evaluate = eval(right_side)
                    return isinstance(evaluate, (int, float, complex))
                except:
                    return False

            # right side of boolean datatypes must evaluate to a boolean value
            if datatype == BOOLEAN_OID:
                boolean_columns = [column for column in column_names if column_datatypes.get(column) == BOOLEAN_OID]
                boolean_columns.sort(reversed=True)

                for column in boolean_columns:
                    pattern = r'\b' + re.escape(column) + r'\b'
                    right_side = re.sub(pattern, 'True', right_side)

                try:
                    evaluate = eval(right_side)
                    return isinstance(evaluate, bool)
                except:
                    return False
                
            # right side of string datatypes must evaluate to a string value
            # right side must have strings wrapped in quotes
            if datatype in STRING_OIDs:
                string_columns = [column for column in column_names if column_datatypes.get(column) in STRING_OIDs]
                string_columns.sort(reversed=True)

                for column in string_columns:
                    pattern = r'\b' + re.escape(column) + r'\b'
                    right_side = re.sub(pattern, "''", right_side)
                
                try:
                    evaluate = eval(right_side)
                    return isinstance(evaluate, bool)
                except:
                    return False

            # right side must be a valid date, this may be buggy and may have to be dealt with in generator
            # i.e. can it handle '2022/1/1'? 
            if datatype == DATE_OID:
                date_columns = [column for column in column_names if column_datatypes.get(column) == DATE_OID]
                date_columns.sort(reversed=True)

                for column in date_columns:
                    pattern = r'\b' + re.escape(column) + r'\b'
                    right_side = re.sub(pattern, "'2022-1-1'", right_side)

                try:
                    date = datetime.strptime(right_side, '%Y-%m-%d')
                    return True
                except:
                    return False
                   
    return False



def is_valid_aggregate(aggregate, column_names, column_datatypes, number_of_grouping_variables):
    '''check for proper aggregate format and with usable group, aggregate function, and table column'''
    #will change it aggregate format changes
    #should eventually not split at _ 
    aggregate_split = aggregate.split('_')
    if len(aggregate_split) == 2:
        if not (aggregate_split[0] in ['avg','min','max','sum'] and 
                aggregate_split[1] in column_names and 
                column_datatypes[aggregate_split[1]] in NUMERICAL_OIDs
                or
                aggregate_split[0] == 'count' and
                aggregate_split[1] in column_names):
            return False
    elif len(aggregate_split) == 3:
        group = int(aggregate_split[0])
        if group > number_of_grouping_variables or group < 1:
            return False
        if not (aggregate_split[1] in ['avg','min','max','sum'] and
                aggregate_split[2] in column_names and 
                column_datatypes[aggregate_split[2]] in NUMERICAL_OIDs
                or
                aggregate_split[1] == 'count' and
                aggregate_split[2] in column_names):
            return False
    return True