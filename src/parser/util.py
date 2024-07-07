import re
import datetime as dt

from src.parser.error import ParsingError


# OIDs for datatypes in postgreSQL
NUMERICAL_OIDs = [21, 23, 20, 1700, 700, 701]
STRING_OIDs = [25, 1042, 1043]
DATE_OID = 1082
BOOLEAN_OID = 16


def get_keyword_clauses(query, keywords):
    keyword_indices = []
    keyword_clauses = []
    
    # Find the location of each keyword in the query
    query_lower = query.lower()
    for keyword in keywords:
        pattern = r'\b' + re.escape(keyword.strip()) + r'\b'
        matches = list(re.finditer(pattern, query_lower))

        if matches:
            keyword_indices.append(matches[0].start())
        else:
            keyword_indices.append(-1)

    # Check that 'select' is the first keyword and starts the query
    if keyword_indices[0] != 0:
        raise ParsingError("Every query must start with SELECT")

    # Find the clauses of the keywords, check for keywords out of order
    previous_index = 0
    previous_keyword = keywords[0]
    for keyword, keyword_index in zip(keywords[1:], keyword_indices[1:]):
        if keyword_index == -1:
            continue
        if keyword_index < previous_index:
            raise ParsingError(f"Unexpected position of '{keyword.strip().upper()}'")
        clause = query[previous_index+len(previous_keyword):keyword_index].strip()
        if not clause:
            raise ParsingError(f"No {previous_keyword.strip().upper()} argument found")
        keyword_clauses.append(clause)
        previous_index = keyword_index
        previous_keyword = keyword
    clause = query[previous_index+len(previous_keyword):].strip()
    if not clause:
        raise ParsingError(f"No {previous_keyword.strip().upper()} argument found")
    keyword_clauses.append(clause)

    for i in range(0, len(keywords)):
        if keyword_indices[i] == -1:
            keyword_clauses[i:i] = ['']
        
    return keyword_clauses


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
                numerical_columns.sort(reverse=True)
                
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
                boolean_columns.sort(reverse=True)

                for column in boolean_columns:
                    pattern = r'\b' + re.escape(column) + r'\b'
                    right_side = re.sub(pattern, 'true', right_side)
                
                right_side = right_side.lower()

                try:
                    evaluate = eval(right_side)
                    return isinstance(evaluate, bool)
                except:
                    return False
                
            # right side of string datatypes must evaluate to a string value
            # right side must have strings wrapped in quotes
            if datatype in STRING_OIDs:
                string_columns = [column for column in column_names if column_datatypes.get(column) in STRING_OIDs]
                string_columns.sort(reverse=True)


                # Split the text into parts that are inside and outside quotes
                quoted_text_pattern = r'"[^"]*"|\'[^\']*\''
                right_side_parts = re.split(f'({quoted_text_pattern})', right_side)
                
                # Iterate over the parts and replace only in the parts outside quotes
                for i, part in enumerate(right_side_parts):
                    if not re.match(quoted_text_pattern, part):
                        for column in string_columns:
                            pattern = r'\b' + re.escape(column) + r'\b'
                            right_side_parts[i] = re.sub(pattern, '', part)
                right_side = ''.join(right_side_parts) 
                
                try:
                    evaluate = eval(right_side)
                    return isinstance(evaluate, str)
                except:
                    return False

            # right side must be a valid date, this may be buggy and may have to be dealt with in generator
            # i.e. can it handle '2022/1/1'? 
            if datatype == DATE_OID:
                date_columns = [column for column in column_names if column_datatypes.get(column) == DATE_OID]
                date_columns.sort(reverse=True)

                for column in date_columns:
                    pattern = r'\b' + re.escape(column) + r'\b'
                    right_side = re.sub(pattern, "'2022-1-1'", right_side)

                try:
                    date = dt.strptime(right_side, '%Y-%m-%d')
                    return True
                except:
                    return False
                   
    return False


''' 
Check for proper aggregate format and with a valid group, aggregate function, and table column.
If the return value is false, the function will return a code described below to identify
the reason that the aggregate was found to be invalid.

    RETURN
        0 --> split into incorrect length
        1 --> incorrect group error 
        2 --> incorrect aggregate function
        3 --> incorrect column name
        4 --> column name not numerical OIDs
        None for valid aggregates
'''
def is_valid_aggregate(aggregate, column_names, column_datatypes, aggregate_groups):
    # will change it aggregate format changes
    #should eventually not split at _
    split_aggregate = aggregate.split('_') 

    if len(split_aggregate) == 2:
        if split_aggregate[0] in ['avg','min','max','sum']:
            if split_aggregate[1] in column_names:
                if column_datatypes[split_aggregate[1]] in NUMERICAL_OIDs:
                    return True, None
                else:
                    return False, 4
            else:
                return False, 3 
        elif split_aggregate[0] == 'count':
            if split_aggregate[1] not in column_names:
                return False, 3   
        else:
            return False, 2
        
    elif len(split_aggregate) == 3:
        group = split_aggregate[0]
        if group not in aggregate_groups:
            return False, 1
        if split_aggregate[1] in ['avg','min','max','sum']:
            if split_aggregate[2] in column_names:
                if column_datatypes[split_aggregate[2]] in NUMERICAL_OIDs:
                    return True, None
                else:
                    return False, 4
            else:
                return False, 3 
        elif split_aggregate[1] == 'count':
            if split_aggregate[2] not in column_names:
                return False, 3   
        else:
            return False, 2
        
    return False, 0