import sys
import datetime

DATATABLE = []
COLUMN_INDEXES = []

def set_datatable_information(datatable,column_indexes):
    global DATATABLE, COLUMN_INDEXES
    DATATABLE = datatable
    COLUMN_INDEXES = column_indexes
    

''' 
Each row of the H Table. The H Table holds 1 H class for each distinct 
combination of grouping attributes in the select clause and is used to 
compute the values of the aggregates in the select and having clause.
'''    

class H:
    def __init__(self, grouping_attributes, aggregates, initial_row):
        self.grouping_attributes = grouping_attributes
        self.aggregates = aggregates
        self.initial_row = initial_row
        self._data_map = {}
        self.build_data_map()

    def build_data_map(self):
        # Set the combination of grouping attributes 
        for attribute in self.grouping_attributes:
            index = COLUMN_INDEXES[attribute]
            self._data_map[attribute] = self.initial_row[index]
            
        # Set the initial values of the aggregates
        for aggregate in self.aggregates:
            split_aggregate = aggregate.split('_')
            
            if len(split_aggregate) == 2:
                aggregate_function, value_attribute = split_aggregate[0], split_aggregate[1]    
                index = COLUMN_INDEXES[value_attribute]
                attribute_value = self.initial_row[index]
                if(attribute_value == None):
                    attribute_value = 0
                
                if aggregate_function in ['sum', 'min', 'max']:
                    self._data_map[aggregate] = attribute_value
                elif aggregate_function == 'count':
                    self._data_map[aggregate] = 1
                elif aggregate_function == 'avg':
                   self._data_map[aggregate] = {'sum': attribute_value, 'count': 1, 'avg': attribute_value}
            
            else:
                aggregate_function, value_attribute = split_aggregate[1], split_aggregate[2]    
                
                if aggregate_function in ['sum', 'count']:
                    self._data_map[aggregate] = 0
                elif aggregate_function == 'min':
                    self._data_map[aggregate] = sys.maxsize
                elif aggregate_function == 'max':
                    self._data_map[aggregate] = - sys.maxsize - 1
                elif aggregate_function == 'avg':
                    self._data_map[aggregate] = {'sum': 0, 'count': 0, 'avg': 0}
    

    def update_data_map(self, aggregate, row):
        split_aggregate = aggregate.split('_')

        if len(split_aggregate) == 2:
            aggregate_function, value_attribute = split_aggregate[0],split_aggregate[1]    
        else: 
            aggregate_function, value_attribute = split_aggregate[1],split_aggregate[2]

        index = COLUMN_INDEXES[value_attribute]
        attribute_value = row[index]
    
        if aggregate_function == 'sum':
            current = self._data_map[aggregate]
            new = current + attribute_value
            self._data_map[aggregate] = new
        elif aggregate_function == 'min':
            current = self._data_map[aggregate]
            if attribute_value < current:
                self._data_map[aggregate] = attribute_value
        elif aggregate_function == 'max':
            current = self._data_map[aggregate]
            if attribute_value > current:
                self._data_map[aggregate] = attribute_value
        elif aggregate_function == 'count':
            self._data_map[aggregate] += 1
        elif aggregate_function == 'avg':
            current = self._data_map[aggregate]
            new_sum = current['sum'] + attribute_value
            new_count = current['count'] + 1
            self._data_map[aggregate] = {'sum': new_sum, 
                                        'count': new_count, 
                                        'avg': (new_sum/new_count)}
    
    def convert_avg_in_data_map(self):
        for aggregate in self.aggregates:
            split_aggregate = aggregate.split('_')
            aggregate_function = split_aggregate[1] if len(split_aggregate) == 3 else split_aggregate[0]
            if aggregate_function == 'avg':
                avg = round(self.data_map[aggregate]['avg'], 2)
                self._data_map[aggregate] = avg
   
    def get_grouping_values(self):
        grouping_value_list = []
        for attribute in self.grouping_attributes:
            grouping_value_list.append(self._data_map[attribute])
        return set(grouping_value_list)
    
    def __str__(self):
        result = ''
        for key, value in self._data_map.items():
            result += f"{key}: {value}, "
        return result

    def __repr__(self):
        return self.__str__()
    
    @property
    def data_map(self):
        return self._data_map



'''
Evaluates each aggregate present in both the select clause and having clause
for each combination of values of the grouping attributes in the select clause.
Utilizes a list of H objects (hTable), which store the data as the algorithm runs
through the data of the datatable.

When the initial hTable is built, a new hTable constructed 
with only the entries that satisfy the having conditions.
'''
def build_hTable(grouping_attributes, aggregates, aggregate_groups, conditions, having_clause):
    hTable = []
    
    # First pass through the datatable initialzing hTable
    # Iterates through each row of the datatable to find all combinations of grouping values
    # Calculate aggregates without a group in the over clause
    for row in DATATABLE:
        grouping_values = []
        for attribute in grouping_attributes:
            grouping_values.append(row[COLUMN_INDEXES[attribute]])
        grouping_values = set(grouping_values)
        
        in_hTable= False
        for entry in hTable:
            # If the row has the same grouping values as the entry in hTable
            if grouping_values == entry.get_grouping_values():
                in_hTable = True
                # Only update aggregates that arent in a group in the over clause
                for aggregate in aggregates:
                    split_aggregate = aggregate.split('_')
                    if len(split_aggregate) == 2:
                        entry.update_data_map(aggregate, row)
                break
        
        # If the grouping values aren't in a hTable entry, create a new entry
        if not in_hTable:
            entry = H(grouping_attributes, aggregates, row)
            hTable.append(entry)

        
    # One pass through the datatable for each group in the over clause
    for group in aggregate_groups:
        # Build a list of conditions in the group, removing the group for easier handling
        nth_conditions = []
        
        for condition in conditions:
            split_condition = condition.split(".")
            if split_condition[0] == group:
                nth_conditions.append(split_condition[1])
        
        # parsed_condition = [<attribute> <operator> <value>]
        parsed_conditions = []
        for condition in nth_conditions:
            if '<=' in condition:
                condition_list = condition.split('<=')
                parsed_condition = [condition_list[0].strip(), '<=', condition_list[1].strip()]
                parsed_conditions.append(parsed_condition)
            elif '>=' in condition:
                condition_list = condition.split('>=')
                parsed_condition = [condition_list[0].strip(), '>=', condition_list[1].strip()]
                parsed_conditions.append(parsed_condition)
            elif '>' in condition:
                condition_list = condition.split('>')
                parsed_condition = [condition_list[0].strip(), '>', condition_list[1].strip()]
                parsed_conditions.append(parsed_condition)
            elif '<' in condition:
                condition_list = condition.split('<')
                parsed_condition = [condition_list[0].strip(), '<', condition_list[1].strip()]
                parsed_conditions.append(parsed_condition)
            elif '=' in condition:
                condition_list = condition.split('=')
                parsed_condition = [condition_list[0].strip(), '==', condition_list[1].strip()]
                parsed_conditions.append(parsed_condition)


        # Determine for each row in the datatable all the conditions are met
        # If so, update the corresponding entry in hTable
        for row in DATATABLE:
            all_true = True
            
            # Evaluate all of the conditions to make sure they are all true
            for parsed_condition in parsed_conditions:
                # Prepare condition for evaluation
                build_logic_statement = parsed_condition.copy()
                attribute_value_in_row = row[COLUMN_INDEXES[parsed_condition[0]]]
                if isinstance(attribute_value_in_row, str):
                    build_logic_statement[0] = "'" + attribute_value_in_row + "'"
                elif isinstance(attribute_value_in_row, datetime.date):
                    build_logic_statement[0] = "'" + str(attribute_value_in_row) + "'"
                else:
                    build_logic_statement[0] = attribute_value_in_row
                
                logic_statement = ' '.join(build_logic_statement)
                if not eval(logic_statement):
                    all_true = False
                
            # If all conditions are met
            # Update the correct entry in hTable
            if all_true:
                grouping_values = []
                for attribute in grouping_attributes:
                    grouping_values.append(row[COLUMN_INDEXES[attribute]])
                grouping_values = set(grouping_values)
                
                # Find the hTable entry to update
                for h_row in hTable:
                    if grouping_values == h_row.get_grouping_values():
                        for aggregate in aggregates:
                            split_aggregate = aggregate.split('_')
                            if len(split_aggregate) == 3 and split_aggregate[0] == group:
                                h_row.update_data_map(aggregate, row)

    # Convert avg aggregates from 
    # {'sum': 0, 'count': 0, 'avg': 0} 
    # to just the avg value
    for entry in hTable:
        entry.convert_avg_in_data_map()

   
    # Build new hTable with entries 
    # that meet the having clause conditions
    if having_clause != '':
        new_hTable = []

        # Replace each aggregate in the having clause
        # with data from the entry, and then evaluate
        # the having clause with the entry data
        for entry in hTable:
            having_clause_evaluate = having_clause
            for aggregate in aggregates:
                if aggregate in having_clause_evaluate:
                    aggregate_value = entry.data_map[aggregate]
                    having_clause_evaluate = having_clause_evaluate.replace(aggregate, str(aggregate_value))
            if eval(having_clause_evaluate):
                new_hTable.append(entry)
        hTable = new_hTable

    return hTable


'''
Builds a new table from the hTable
based on the attributes in the select clause
'''
def project_select_attributes(hTable, select_attributes):
    select_table = []

    for entry in hTable:
        select_entry = {}
        for key, value in entry.data_map.items():
            if key in select_attributes:
                select_entry[key] = value 
        select_table.append(select_entry)

    return select_table


'''
Builds a new datatable
sorted by the order by value
'''
def order_by_sort(select_table, order_by, grouping_attributes):
    order_by_table = select_table
    
    if order_by != '':
        sort_order = grouping_attributes[:order_by]
        order_by_table.sort(key=lambda x: tuple(x.get(key, '') for key in sort_order))

    return order_by_table


