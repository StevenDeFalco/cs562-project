from .parser_util import *
from .parsing_error import ParsingError

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

    def read_query_file(self):
        '''Read the query file and produce a string with a single space between every term '''
        with open(self.file, 'r') as f:
            query = f.read().replace('\n', ' ')
            query = [term for term in query.split(' ') if term != '']
            query = ' '.join(query)
        return query


    def build_query_struct(self):
        '''
        Builds a struct of the important information in the query.
        Validates the information in the query to reduce errors when running the generated algorithm. 
        '''
        struct = {}

        keywords = ['select', 'over', 'where', 'having', 'order by']
        # keyword_clauses contains the clause of each keyword at the same index as the keyword above
        keyword_clauses = get_keyword_clauses(self.query, keywords)

        # Process OVER clause to get the number of grouping variables
        try:
            if not keyword_clauses[1]:
                number_of_grouping_variables = 0
            else:
                number_of_grouping_variables = int(keyword_clauses[1])
            struct['number_of_grouping_variables'] = number_of_grouping_variables
        except Exception:
            raise ParsingError(f"'{keyword_clauses[1]}' could not be parsed as the OVER argument")

        # Process SELECT clause and categorize values as a grouping attribute or aggregate
        select_clause = keyword_clauses[0]
        select_grouping_attributes = []
        select_aggregates = []

        select_clause_split = select_clause.split(',')
        number_of_select_arguments = len(select_clause_split)
        for attribute in [attr.lower().strip() for attr in select_clause_split]:
            if attribute in self.columns:
                select_grouping_attributes.append(attribute)
            else:
                select_aggregates.append(attribute)

        for aggregate in select_aggregates:
            # deal with the error mode for better parsing errors and write test cases
            valid_aggregate, error_code = is_valid_aggregate(aggregate, self.columns, self.column_datatypes, number_of_grouping_variables)
            if not valid_aggregate:
                raise ParsingError(f"'{aggregate}' is not a valid SELECT argument")

        struct["select_clause"] = select_clause

        '''
        deal with select * eventually
        '''

        # Check conditions
        conditions = keyword_clauses[2]
        conditions_list = conditions.split(',')
        grouping_variables_list = [str(grouping_variable) for grouping_variable in range(1, number_of_grouping_variables + 1)]

        for condition in [condition.strip() for condition in conditions_list]:
            split_condition = condition.split('.')

            if len(split_condition) == 1:
                raise ParsingError(f"No group in the WHERE condition '{condition}'")

            if split_condition[0] not in grouping_variables_list:
                raise ParsingError(f"Invalid group in the WHERE condition '{condition}'")

            valid_condition = is_valid_condition(split_condition[1], self.columns, self.column_datatypes)
            if not valid_condition:
                raise ParsingError(f"WHERE condition '{condition}' could not be evaluated")

        struct['conditions'] = conditions

        # Process HAVING clause to make sure it will evaluate without error
        having_clause = keyword_clauses[3]
        having_aggregates = []

        having_clause_no_symbols = having_clause
        math_symbols = ['+', '-', '*', '/', '%', ' and ', ' or ', ' not ', '(', ')', '[', ']', '{', '}', '>', '=', '<']
        for symbol in math_symbols:
            while symbol in having_clause_no_symbols:
                having_clause_no_symbols = having_clause_no_symbols.replace(symbol, ' ')

        having_clause_no_symbols_split = having_clause_no_symbols.split(' ')
        for item in [item.strip() for item in having_clause_no_symbols_split]:
            if item != '':
                try:
                    _ = float(item)
                except Exception:
                    having_aggregates.append(item.lower())

        having_clause_test = having_clause
        having_aggregates.sort(reverse=True)
        for aggregate in having_aggregates:
            # deal with the error mode for better parsing errors
            valid_aggregate, error_mode = is_valid_aggregate(aggregate, self.columns, self.column_datatypes, number_of_grouping_variables)
            if not valid_aggregate:
                raise ParsingError(f"'{aggregate}' cannot be parsed as a HAVING argument")
            while aggregate in having_clause_test:
                having_clause_test = having_clause_test.replace(aggregate, '1')

        try:
            _ = eval(having_clause_test)
        except:
            raise ParsingError("HAVING could not be evaluated")

        struct['having_clause'] = having_clause

        # Order by is a list of numbers from 1 up to number of args in select clause
        order_by = keyword_clauses[4]
        order_by_list = order_by.split(',')
        number_of_select_arguments_list = [str(select_argument) for select_argument in range(1, number_of_select_arguments + 1)]

        for order_by_value in [order_by_value.strip() for order_by_value in order_by_list]:
            if order_by_value not in number_of_select_arguments_list:
                raise ParsingError(f"'{order_by_value}' cannot be parsed as an ORDER BY argument")

        struct['order_by'] = order_by

        return struct
    
    @property
    def query_struct(self):
        return self._query_struct
