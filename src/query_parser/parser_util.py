
import re
from datetime import datetime
from .parsing_error import ParsingError

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

    for i in range(0, 5):
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
        left_side = condition_split[0].strip().lower()
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
                    date = datetime.strptime(right_side, '%Y-%m-%d')
                    return True
                except:
                    return False
                   
    return False



def is_valid_aggregate(aggregate, column_names, column_datatypes, number_of_grouping_variables):
    '''check for proper aggregate format and with usable group, aggregate function, and table column'''
    #will change it aggregate format changes
    #should eventually not split at _ 

    '''
    RETURN
    0 --> split into incorrect length
    1 --> wrong function or column
    2 --> incorrect group error 
    None for valid aggregates
    '''
    aggregate = aggregate.lower()
    aggregate_split = aggregate.split('_')
    if len(aggregate_split) == 2:
        if not (aggregate_split[0] in ['avg','min','max','sum'] and 
                aggregate_split[1] in column_names and 
                column_datatypes[aggregate_split[1]] in NUMERICAL_OIDs
                or
                aggregate_split[0] == 'count' and
                aggregate_split[1] in column_names):
            return False, 1
        return True, None
        
    elif len(aggregate_split) == 3:
        try:
            group = int(aggregate_split[0])
            if group > number_of_grouping_variables or group < 1:
                return False, 2
        except Exception:
            return False, 2
        if group > number_of_grouping_variables or group < 1:
            return False, 2
        if not (aggregate_split[1] in ['avg','min','max','sum'] and
                aggregate_split[2] in column_names and 
                column_datatypes[aggregate_split[2]] in NUMERICAL_OIDs
                or
                aggregate_split[1] == 'count' and
                aggregate_split[2] in column_names):
            return False, 1
        return True, None
        
    return False, 0