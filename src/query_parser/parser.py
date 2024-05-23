import sys
import parser_util

class Parser:
    """Class to perform operations with the Phi Operator and ESQL"""
    def __init__(self, filename, column_names, column_datatypes):
        self.file = filename
        self.column_names = column_names
        self.column_datatypes = column_datatypes
        self._query_struct = self.make_struct()


    '''
    SELECT ... , ... , ...
    OVER X,Y, ... (will keep a number for now)
    WHERE  ... , ... , ...
    HAVING ...
    ORDER BY 2,3,1
    
    
    '''

    def build_struct(self):
        """Builds a struct of the query data"""
        struct = {}

        # read the query file and produce a lowercase string with a single space between every term
        with open(self.file, 'r') as f:
            query = f.read().lower().replace('\n',' ')
            query = [term for term in query.split(' ') if term != '']
            query = ' '.join(query)
            if len(query) == 0:
                sys.exit(1)

        keywords = ['select ', ' over ', ' where ', ' having ', ' order by ']
        keyword_indices = [query.find(keyword) for keyword in keywords]
        keyword_clauses = []

        # Check that 'select' is the first keyword and starts the query
        if keyword_indices[0] != 0:
            print("Error: 'select' must be first in the query.")
            sys.exit(1)
        
        # find the clauses of the keywords, check for keywords out of order
        previous_index = len(keywords[0])
        for keyword, keyword_index in zip(keywords[1:], keyword_indices[1:]):
            if keyword_index == -1:
                continue
            if keyword_index <= previous_index:
                print(f"Unexpected position of '{keyword.strip()}'.")
                sys.exit(1)
            keyword_clauses.append(query[previous_index : keyword_index].strip())
            previous_index = keyword_index + len(keyword)
        keyword_clauses.append(query[previous_index:].strip())

        for i in range(0,5):
            if keyword_indices[i] == -1:
                keyword_clauses[i:i] = ['']
        
        # Process SELECT clause and catagorize values as a grouping attribute or aggregate
        select_clause = keyword_clauses[0]
        select_grouping_attributes = []
        select_aggregates = []

        if not select_clause:
            print('No select clause')
            sys.exit(1)

        select_clause_split = select_clause.split(',')
        number_of_select_arguments = len(select_clause_split)
        for attribute in [attribute.strip() for attribute in select_clause_split]:
            if attribute in self.column_names:
                select_grouping_attributes.append(attribute)
            else:
                select_aggregates.append(attribute)
        
        for aggregate in select_aggregates:
            if not util.is_valid_aggregate(aggregate,self.column_names,self.column_datatypes,number_of_grouping_variables):
                print(f"{aggregate} is not a valid aggregate")
                sys.exit(1)
        
        struct["select_clause"] = select_clause


        # deal with select all later
        '''
        select_all_flag = False
        if s == ['*']:
            self._mf_struct['S'] = columns
            self._mf_struct['V'] = columns
            if self._mf_struct['n'] != 0 or self._mf_struct['F'] != [] or self._mf_struct['G'] != []:
                warnings.warn(SelectAllWarning)
            self._mf_struct['n'] = 0
            self._mf_struct['F'] = []
            self._mf_struct['G'] = []
            select_all_flag = True
        '''
            
        # Process OVER clause to get the number of grouping variables
        # could change over to a list of group nanes, when conditions gets modified
        try:
            if keyword_clauses[1] == '':
                number_of_grouping_variables = 0
            else:
                number_of_grouping_variables = int(keyword_clauses[1])
            struct['number_of_grouping_variables'] = number_of_grouping_variables
        except Exception:
            print("Unexpected input of OVER")



        # check conditions
        # currently only accepts conditions in groups
        # should extend to conditions out of groups
        # and split where clause and such that
        # also assume each condition seperated by a comma, no AND,OR
        conditions = keyword_clauses[2]
        conditions_list = conditions.split(',')
        grouping_variables_list = [str(grouping_variable) for grouping_variable in range(1, number_of_grouping_variables + 1)]
        
        for condition in [condition.stripI() for condition in conditions_list]:
            split_condition = condition.split('.')
            
            if len(split_condition) != 2:
                print("No group found in condition")
                sys.exit(1)

            if split_condition[0] not in grouping_variables_list:
                print("Invalid group found in condition")
                sys.exit(1)
            
            valid_condition = parser_util.is_valid_aggregate(split_condition[1], self.column_names, self.column_datatypes)
            if not valid_condition:
                print("Invalid condition")
                sys.exit(1)

        struct['conditions'] = conditions
            


        # Process HAVING clause to make sure it will evaluate witjout error
        having_clause = keyword_clauses[3]
        having_aggregates = []
        
        having_clause_no_symbols = having_clause
        math_symbols = ['+','-','*','/','%',' and ',' or ',' not ','(', ')','[',']','{','}','>','=','<']
        for symbol in math_symbols:
            while symbol in having_clause_no_symbols:
                having_clause_no_symbols = having_clause_no_symbols.replace(symbol,' ')

        having_clause_no_symbols_split = having_clause_no_symbols.split(' ')
        for item in [item.strip() for item in having_clause_no_symbols_split]:
            if item != '':
                try:
                    _ = float(item)
                except Exception:
                    having_aggregates.append(item)

        having_clause_test = having_clause
        having_aggregates.sort(reversed=True)
        for aggregate in having_aggregates:
            valid_aggregate = parser_util.is_valid_aggregate(aggregate,self.column_names,self.column_datatypes,number_of_grouping_variables)
            if not valid_aggregate:
                print(f"{aggregate} is not a valid aggregate")
                sys.exit(1)
            while aggregate in having_clause_test:
                having_clause_test.replace(aggregate,'1')
        
        try:
            _ = eval(having_clause_test)
        except:
            print('Unable to evaluate the HAVING clause')
            sys.exit(1)

        struct['having_clause'] = having_clause



        # Order by is a list of numbers from 1 up to number of args in select clause
        # i.e. 2,1,3 if there are 3+ arsg in select, can include aggregates
        order_by = keyword_clauses[4]
        order_by_list = order_by.split[',']
        number_of_select_arguments_list = [str(select_argument) for select_argument in range(1, number_of_select_arguments + 1)]
        
        for order_by_value in [order_by_value.strip() for order_by_value in order_by_list]:
            if order_by_value not in number_of_select_arguments_list:
                print('Error in order by')
                sys.exit(1)

        struct['order_by'] = order_by

        
        return struct
        
  
    @property
    def query_struct(self):
        return self._query_struct 

