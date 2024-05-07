import sys
import re
import calendar
import warnings

class PhiOperator:
    """Class to perform operations with the Phi Operator and ESQL"""
    def __init__(self, filename):
        self.file = filename
        self._mf_struct = self.make_struct()

    def make_struct(self):
        """Makes the mf_struct given raw txt in the input query before any input error checking"""
        struct = {}
        lines = []
        with open(self.file, 'r') as f:
            for line in f:
                if not line:
                    continue
                lines.append(line)
        curr_idx = 0
        while curr_idx < len(lines):
            line = lines[curr_idx]
            '''
            SELECT ATTRIBUTE(S)
            struct['S'] should be a list of select attributes,
            set to an empty list when no select attributes are provided
            '''
            if line.startswith("SELECT ATTRIBUTE"):
                if lines[curr_idx + 1].startswith("NUMBER OF "):
                    struct['S'] = []
                    curr_idx += 1
                    continue
                s_list = lines[curr_idx + 1].strip()
                if len(s_list) == 0:
                    struct['S'] = []
                else:
                    struct['S'] = [s.strip() for s in s_list.split(',')]
                curr_idx += 2
                continue 
            '''
            NUMBER OF GROUPING VARIABLES(n)
            struct['n'] should be an integer,
            set to 0 when there is no input
            '''
            if line.startswith("NUMBER OF GROUPING"):
                if lines[curr_idx + 1].startswith("GROUPING ATTRIB"):
                    struct['n'] = '0'
                    curr_idx += 1
                    continue
                n =  lines[curr_idx + 1].strip()
                if len(n) == 0:
                    struct['n'] = '0'
                else:
                    struct['n'] = n
                curr_idx += 2
                continue
            '''
            GROUPING ATTRIBUTES(V)
            struct['V'] should be a list of grouping attributes, 
            set to an empty list when no grouping attribures are provided
            '''
            if line.startswith("GROUPING ATTRIBUTES"):
                if lines[curr_idx + 1].startswith("F-VECT"):
                    struct['V'] = []
                    curr_idx += 1
                    continue
                v_list = lines[curr_idx + 1].strip()
                if len(v_list) == 0:
                    struct['V'] = []
                else:
                    struct['V'] = [v.strip() for v in v_list.split(',')]
                curr_idx += 2
                continue
            '''
            F-VECT([F])
            struct['F'] should be a list of aggregate functions,
            set to an empty list when no aggregate functions are provided
            '''
            if line.startswith("F-VECT"):
                if lines[curr_idx + 1].startswith("SELECT CONDITION"):
                    struct['F'] = []
                    curr_idx += 1
                    continue
                f_list = lines[curr_idx + 1].strip()
                if len(f_list) == 0:
                    struct['F'] = []
                else:
                    
                    struct['F'] = [f.strip() for f in f_list.split(',')]

                curr_idx += 2
                continue
            '''
            SELECT CONDITION-VECT([σ])
            struct["sigma"] should be a list of all of the conditions,
            set to an empty list when there are no condition provided
            '''
            if line.startswith("SELECT CONDITION"):
                if lines[curr_idx + 1].startswith("HAVING"):
                    curr_idx += 1
                    struct['sigma'] = []
                    continue
                curr_idx += 1
                conditions = []
                while not lines[curr_idx].startswith("HAVING"):
                    conditions.append(lines[curr_idx].strip())
                    curr_idx += 1
                struct['sigma'] = conditions
                continue
            '''
            HAVING_CONDITION(G)
            struct['G'] should be a list with 1 string having clause,
            set to an empty list when therte is no having clause provided
            '''
            if line.startswith("HAVING"):
                if curr_idx + 1 == len(lines):
                    struct['G'] = []
                    break
                struct['G'] = [lines[curr_idx + 1].strip()]
                break
        return struct
    
    def process_mf_struct(self, columns, column_datatypes):
        '''checks the phi operator input to ensure proper computation'''
        
        # OIDs for datatypes in postgreSQL
        NUMERICAL_OIDs = [21, 23, 20, 1700, 700, 701]
        STRING_OID = [25, 1042, 1043]
        DATE_OID = 1082

        def check_agg(agg_list, exception):
            '''Function used to check if the aggregates are valid'''
            for agg in agg_list:
                agg_split = agg.split('_')
                if len(agg_split) == 2:
                    if not (agg_split[0] in ['avg','min','max','sum'] 
                        and agg_split[1] in columns
                        and column_datatypes[agg_split[1]] in NUMERICAL_OIDs
                        or
                        agg_split[0] == 'count' 
                        and agg_split[1] in columns
                    ):
                        raise exception
                elif len(agg_split) == 3:
                    try:
                        group = int(agg_split[0])
                        n = self._mf_struct['n']
                        if group > n or group < 1:
                            raise exception
                    except ValueError:
                        raise exception
                    if not (agg_split[1] in ['avg','min','max','sum'] 
                        and agg_split[2] in columns
                        and column_datatypes[agg_split[2]] in NUMERICAL_OIDs
                        or
                        agg_split[1] == 'count' 
                        and agg_split[2] in columns
                    ):
                        raise exception
                else:
                    raise exception

        try:

            '''
            First check if the number of grouping variables is a valid integer 
            '''
            n = self._mf_struct['n']
            try:
                n = int(n)
                self._mf_struct['n'] = n
            except Exception:
                raise PhiInputError("NUMBER OF GROUPING VARIABLES(n)", "Number of grouping variables not inputted as an integer")
            
            ''' 
            For the select clause, if it is empty there is no query.
            If the input is *, then it is selecting all of the column names.
            Then, make sure the select clause inputs are valid columns or add them to the aggregates list.
            '''

            '''
            If select is * (all columns), the number of grouping variables should be 0,
            there should be no aggregates in the F-VECT, the grouping attributes should be 
            all columns as well, and there should be no HAVING clause.
            Do not touch the conditions vector because there may still be a WHERE clause.
            '''

            # to check if values in SELECT are in the grouping variables or F-Vector 
            s_grouping_attributes = []
            s_aggregates = []

            s = self._mf_struct['S']

            if s == []:
                raise PhiInputError('SELECT ATTRIBUTE(S)', 'No select attributes inputted')
        
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
                
            else:
                for att in [att.strip() for att in s]:
                    if att in columns:
                        s_grouping_attributes.append(att)
                        continue
                    else:
                        s_aggregates.append(att)

            
            ''' 
            For the grouping attributes, they must contain the same attributes as the grouping attributes found in the select clause.
            Order does not matter, but note that grouping attributes takes precedence over the order in the select clause.
            Also, if select was '*' (all columns), the grouping attributes should be all of the columns as well.
            '''

            v = self._mf_struct['V']
            if not select_all_flag and set(v) != set(s_grouping_attributes):
                warnings.warn(GroupingAttributesWarning(s_grouping_attributes))
                self._mf_struct['V'] = s_grouping_attributes
            
            
            '''
            For the having clause, check if all items in the clause are a math operation or a number.
            If not, append to the aggregates list to be checked with the rest of the aggregates.
            '''

            # to check if values in the HAVING CLAUSE are in the F-Vector
            g_aggregates = []

            g = self._mf_struct['G']
            if len(g) != 0:
                g_= g[0]
                g_split = g_.split(' ')

                ops = ['+','-','*','/','//','%', 'and', 'or', 'not', '(', ')','**', '>', '==', '=', '<', '<=', '>=']
                for item in [item.strip() for item in g_split]:
                    if item in ops:
                        continue
                    try:
                        _ = float(item)
                    except Exception:
                        g_aggregates.append(item)


            ''' 
            For the F-Vector, make sure all aggregates in select, having, and f-vector are valid.
            Then make sure all of the aggregates in the select statement and having clause are in the F-Vector.
            Warn the user if their F-Vector was modified.
            '''

            f_aggregates = self._mf_struct['F']

            check_agg(s_aggregates, PhiInputError('SELECT ATTRIBUTE(S)', 'Select contains an invalid attribute or aggregate function'))
            check_agg(g_aggregates, PhiInputError('HAVING CLAUSE(G)', 'Having clause contains an invalid varaible or aggregate function. Make sure gaving clause inputs have spaces between different entities'))
            check_agg(f_aggregates, PhiInputError('F-VECT([F])', 'F-Vector contains an invalid aggregate function'))

            f_aggregates_updated = False
            for s_agg in [s_agg.strip() for s_agg in s_aggregates]:
                if s_agg not in f_aggregates:
                    f_aggregates.append(s_agg)
                    f_aggregates_updated = True
            for g_agg in [g_agg.strip() for g_agg in g_aggregates]:
                if g_agg not in f_aggregates:
                    f_aggregates.append(s_agg)
                    f_aggregates_updated = True

            if f_aggregates_updated:
                warnings.warn(FVectorWarning(f_aggregates))
                self._mf_struct['F'] = f_aggregates


            '''
            For the conditions vector, construct a new conditions vector of conditions that can be evaluated. 
            Warn the user if their conditions vector was modified.
            '''

            sigma = self._mf_struct['sigma']
            new_sigma = []

            n = self._mf_struct['n']
            n_list = [str(i) for i in range(1, n + 1)]
            
            for cond in sigma:
                split_cond = cond.split(".")
                if len(split_cond) == 2 and split_cond[0].strip() in n_list:
                    if '<=' in split_cond[1]:
                        operation = '<='
                        cl = split_cond[1].split('<=')
                    elif '>=' in split_cond[1]:
                        operation = '>='
                        cl = split_cond[1].split('>=')
                    elif '=' in split_cond[1]:
                        operation = '='
                        cl = split_cond[1].split('=')
                    elif '<' in split_cond[1]:
                        operation = '<'
                        cl = split_cond[1].split('<')
                    elif '>' in split_cond[1]:
                        operation = '>'
                        cl = split_cond[1].split('>')
                    if len(cl) == 2:
                        if cl[0].strip() in columns:
                            d_type = column_datatypes[cl[0].strip()]
                            if d_type in NUMERICAL_OIDs:
                                try:
                                    _ = float(cl[1])
                                    new_cond = split_cond[0].strip() + '.' + cl[0].strip() + operation + cl[1].strip()
                                    new_sigma.append(cond)
                                except Exception:
                                    pass
                            elif d_type in STRING_OID:
                                comp = cl[1].strip()
                                front_single = comp[0] == "'"
                                back_single = comp[-1] == "'"
                                front_double= comp[0] == '"'
                                back_double = comp[-1] == '"'
                                if front_single and back_single:     # 'xxx'
                                    pass
                                elif front_double and back_double:   # "xxx"
                                    pass
                                elif front_single and back_double:   # 'xxx"
                                    comp = comp[:-1] + "'"
                                elif front_double and back_single:   # 'xxx"
                                    comp = + "'" + comp[1:]
                                elif front_single:                   # 'xxx
                                    comp += "'"
                                elif front_double:                   # "xxx
                                    comp += '"'
                                elif back_single:                    # xxx'
                                    comp = "'" + comp
                                elif back_double:                    # xxx"
                                    comp += "'"
                                new_cond = split_cond[0].strip() + '.' + cl[0].strip() + operation + comp
                                new_sigma.append(new_cond)
                            elif d_type == DATE_OID:
                                split_date = [part for part in re.split(r'\D+', cl[1]) if part]
                                if (len(split_date) == 3 and len(split_date[0]) == 4 and 
                                        len(split_date[1]) == 2 and len(split_date[2]) == 2):
                                    year = int(split_date[0])
                                    month = int(split_date[1])
                                    day = int(split_date[2])
                                    days_in_month = [calendar.monthrange(year, i)[1] for i in range(1, 13)]
                                    print(days_in_month)
                                    if month in range(1,13) and day in range(1, days_in_month[month-1] + 1):
                                        date_format = "'" + split_date[0] + '-' + split_date[1] + '-' + split_date[2] + "'"
                                        new_cond = split_cond[0].strip() + '.' + cl[0].strip() + operation + date_format
                                        new_sigma.append(new_cond)
            
            if set(new_sigma) != set(sigma):
                warnings.warn(ConditionsVectorWarning(new_sigma))
                self._mf_struct['sigma'] = new_sigma


        except PhiInputError as input_error:
            print(input_error)
            sys.exit(1)


    @property
    def mf_struct(self):
        return self._mf_struct 



class PhiInputError(Exception):
    '''Exception to use to handle bad query inputs for the Phi Operator'''
    def __init__(self, phi_component, message):
        self.phi_component = phi_component
        self.message = message
        super().__init__("INPUT ERROR: " + self.phi_component + " - " + self.message)


class SelectAllWarning(Warning):
    '''Warning to use to notify the user that the SELECT * removes n,F,G'''
    def __init__(self):
        self.message = "SelectAllWarning: Select all (*) updates inputs for all of the inputs other than the condition vector." 
        super().__init__()

    def __str__(self):
        return self.message


class GroupingAttributesWarning(Warning):
    '''Warning to use to notify the user that the grouping attributes have been altered'''
    def __init__(self, newV):
        self.message = (
            f"ConditionsVectorWarning: The grouping attributes were modified to match the grouping attributes in SELECT."
            f"The updated grouping attributes are: {newV}"
        )   
        super().__init__()

    def __str__(self):
        return self.message


class FVectorWarning(Warning):
    '''Warning to use to notify the user that the F-Vector has been altered'''
    def __init__(self, new_f_vector):
        self.message = (
            f"ConditionsVectorWarning: The F-Vector was modified since it did not include all of the aggregates in SELECT ATTRIBUTE(S) and the HAVING CLAUSE(G)."
            f"The updated conditions vector is: {new_f_vector}"
        )   
        super().__init__()

    def __str__(self):
        return self.message
    

class ConditionsVectorWarning(Warning):
    '''Warning to use to notify the user that the conditions vector has been altered'''
    def __init__(self, new_conditions_vector):
        self.message = (
            f"ConditionsVectorWarning: Conditions in the conditions vector may have been modified or "
            f"removed to eliminate computation errors. Check the formatting of the inputs for the conditions vector. "
            f"Ensure proper type matching and that dates are written as 'YYYY-MM-DD'. The updated conditions vector is: {new_conditions_vector}"
        )   
        super().__init__()

    def __str__(self):
        return self.message