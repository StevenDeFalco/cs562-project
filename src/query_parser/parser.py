from .parser_util import *
from .parsing_error import ParsingError

import re

class Parser:
    """Class to perform operations with the Phi Operator and ESQL"""
    def __init__(self, filename, columns, column_datatypes):
        self.file = filename
        self.columns = columns
        self.column_datatypes = column_datatypes
        self.query = self.read_query_file()
        self._query_struct = self.build_query_struct()

    '''
    SELECT ... , ... , ...
    OVER 2
    WHERE  1... , 2... , 2...
    HAVING ...
    ORDER BY 2,3,1
    
    eventually:
    
    SELECT ... , ... , ...
    OVER X,Y, ... 
    WHERE  ... and ... or ...
    SUCH THAT X...., Y....
    HAVING ...
    ORDER BY 2,3,1
    '''


    '''
    Read the query file and produce a string with a single space between every term and 
    everything is set to lowercase other than text wrapped in quotes (in the where clause for String comparison)
    '''
    def read_query_file(self):
        with open(self.file, 'r') as f:
            query = f.read()

        # Find and seperate quoted strings
        pattern = r'"[^"]*"|\'[^\']*\''
        quoted_texts = re.findall(pattern, query)
        parts = re.split(f'({pattern})', query)

        # Set everything that isn't wrapped in quotes to lowercase
        processed_parts = []
        quoted_index = 0
        for part in parts:
            if re.match(pattern, part):
                processed_parts.append(f'QUOTED{quoted_index}')
                quoted_index += 1
            else:
                processed_parts.append(part.lower())

         # Reinsert the quoted texts using placeholders
        query = ''.join(processed_parts)
        for i, qt in enumerate(quoted_texts):
            query = query.replace(f'QUOTED{i}', qt, 1)

        query = ' '.join(query.split())
        return query

    '''
    Builds a struct of the important information in the query.
    Validates the information in the query to reduce errors when running the generated algorithm. 
    '''
    def build_query_struct(self):
        struct = {}

        keywords = ['select', 'over', 'where', 'having', 'order by']
        # keyword_clauses contains the clause of each keyword at the same index as the keyword above
        keyword_clauses = get_keyword_clauses(self.query, keywords)

        # Process OVER clause to get the list of grouping variables
        aggregate_groups = keyword_clauses[1]

        split_aggregate_groups = aggregate_groups.split(",")
        for group in [group.strip() for group in split_aggregate_groups]:
            if len(group.split(' ')) != 1:
                raise ParsingError(f"'{group}' could not be parsed as an OVER group")
    
        struct['aggregate_groups'] = aggregate_groups

        # Process SELECT clause and categorize values as a grouping attribute or aggregate
        select_clause = keyword_clauses[0]
        select_grouping_attributes = []
        select_aggregates = []

        split_select_clause = select_clause.split(',')
        number_of_select_arguments = len(split_select_clause)
        for attribute in [attribute.lower().strip() for attribute in split_select_clause]:
            if attribute in self.columns:
                select_grouping_attributes.append(attribute)
            else:
                select_aggregates.append(attribute)

        for aggregate in select_aggregates:
            # deal with the error mode for better parsing errors and write test cases
            valid_aggregate, error_code = is_valid_aggregate(aggregate, self.columns, self.column_datatypes, aggregate_groups)
            if not valid_aggregate:
                print(error_code)
                raise ParsingError(f"'{aggregate}' is not a valid SELECT argument")

        struct["select_clause"] = select_clause
        struct['select_grouping_attributes'] = select_grouping_attributes

        '''
        deal with select * eventually
        '''

        # Check conditions in the where clause
        conditions = keyword_clauses[2]
        
        if conditions.strip() != '':
            conditions_list = conditions.split(',')

            for condition in [condition.strip() for condition in conditions_list]:
                split_condition = condition.split('.')

                if len(split_condition) == 1:
                    raise ParsingError(f"No group in the WHERE condition '{condition}'")

                if split_condition[0] not in aggregate_groups:
                    raise ParsingError(f"Invalid group in the WHERE condition '{condition}'")

                valid_condition = is_valid_condition(split_condition[1], self.columns, self.column_datatypes)
                if not valid_condition:
                    raise ParsingError(f"WHERE condition '{condition}' could not be evaluated")

        struct['conditions'] = [condition.strip() for condition in conditions.split(",")]

        # Process HAVING clause to make sure it will evaluate without error
        having_clause = keyword_clauses[3]
        having_aggregates = []

        if having_clause.strip() != '':
            having_clause_no_symbols = having_clause
            math_symbols = ['+', '-', '*', '/', '%', '(', ')', '[', ']', '{', '}', '>', '=', '<']
            logic_operators = ['and', 'or', 'not']
            for symbol in math_symbols:
                while symbol in having_clause_no_symbols:
                    having_clause_no_symbols = having_clause_no_symbols.replace(symbol, ' ')

            having_clause_no_symbols_split = having_clause_no_symbols.split(' ')
            for item in [item.strip() for item in having_clause_no_symbols_split]:
                if item not in logic_operators and item != '':
                    try:
                        _ = float(item)
                    except Exception:
                        having_aggregates.append(item)

            having_clause_test = having_clause
            for aggregate in having_aggregates:
                # deal with the error mode for better parsing errors
                valid_aggregate, error_mode = is_valid_aggregate(aggregate, self.columns, self.column_datatypes, aggregate_groups)
                if not valid_aggregate:
                    raise ParsingError(f"'{aggregate}' cannot be parsed as a HAVING argument")
                while aggregate in having_clause_test:
                    having_clause_test = having_clause_test.replace(aggregate, '1')

            try:
                _ = eval(having_clause_test)
            except:
                raise ParsingError("HAVING could not be evaluated")

        struct['having_clause'] = having_clause
        struct['aggregates'] = set(select_aggregates + having_aggregates)

        # Order by is a numbes from 1 up to number of grouping attributes in the select clause
        order_by = keyword_clauses[4]
        number_of_select_arguments_list = [str(select_argument) for select_argument in range(0, number_of_select_arguments + 1)]

        if order_by in number_of_select_arguments_list:
            order_by = int(order_by)
        elif order_by == '':
            order_by = 0
        else:
            raise ParsingError(f"'{order_by}' cannot be parsed as an ORDER BY argument")

        struct['order_by'] = order_by

        return struct
    
    @property
    def query_struct(self):
        return self._query_struct
