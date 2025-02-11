import datetime

# Global variables for the current datatable, column indexes, and column types.
DATATABLE = []
COLUMN_INDEXES = {}
COLUMN_TYPES = {}  # Mapping of column names to their expected types (e.g., 'date', 'string', etc.)

def normalize_column_indexes(col_indexes, expected_columns=None):
    """
    Ensure that col_indexes is a dictionary mapping column names to integer indices.
    If col_indexes is a list, convert it using the expected order.
    """
    if isinstance(col_indexes, dict):
        return col_indexes
    elif isinstance(col_indexes, list):
        if expected_columns is None:
            return {col: idx for idx, col in enumerate(col_indexes)}
        else:
            return {col: idx for idx, col in enumerate(expected_columns)}
    else:
        raise TypeError("Column indexes must be either a dict or a list.")

def set_datatable_information(datatable, col_indexes, columns):
    """
    Set the global DATATABLE, COLUMN_INDEXES, and COLUMN_TYPES.
    Converts any column marked as 'date' (in the columns dict) from a string (in 'YYYY-MM-DD' format)
    to a datetime.date object.
    
    Parameters:
        datatable (list): List of rows (each row is a list/tuple).
        col_indexes (dict or list): Either a dict mapping column names to indices or a list of column names.
        columns (dict): Mapping of column names to their types.
    """
    global DATATABLE, COLUMN_INDEXES, COLUMN_TYPES
    expected_columns = list(columns.keys())
    COLUMN_INDEXES = normalize_column_indexes(col_indexes, expected_columns)
    COLUMN_TYPES = {col: str(columns[col]).lower() for col in columns}
    
    new_datatable = []
    for row in datatable:
        new_row = list(row)
        for col, idx in COLUMN_INDEXES.items():
            if COLUMN_TYPES.get(col) == 'date' and isinstance(new_row[idx], str):
                new_row[idx] = datetime.datetime.strptime(new_row[idx], '%Y-%m-%d').date()
        new_datatable.append(new_row)
    DATATABLE = new_datatable

def set_datatable(datatable):
    """
    Reset the global DATATABLE (for example, after filtering).
    Reapply the date conversion using COLUMN_TYPES and COLUMN_INDEXES if available.
    """
    global DATATABLE
    if COLUMN_TYPES and COLUMN_INDEXES:
        new_datatable = []
        for row in datatable:
            new_row = list(row)
            for col, idx in COLUMN_INDEXES.items():
                if COLUMN_TYPES.get(col) == 'date' and isinstance(new_row[idx], str):
                    new_row[idx] = datetime.datetime.strptime(new_row[idx], '%Y-%m-%d').date()
            new_datatable.append(new_row)
        DATATABLE = new_datatable
    else:
        DATATABLE = datatable

###############################################################################
# Condition Evaluation
###############################################################################

def evaluate_condition(condition, row):
    """
    Recursively evaluate a condition structure against a row.
    
    The condition can be:
      - A leaf condition with keys 'column', 'operator', and 'value'
      - A compound condition with an 'operator' key ('AND', 'OR', or 'NOT') and either a list of subconditions
        (key "conditions") or a single subcondition (key "condition").
    
    Returns:
        bool: True if the condition is met by the row, False otherwise.
    
    Raises:
        KeyError: If a referenced column is not found in COLUMN_INDEXES.
        Exception: If an unknown operator is encountered.
    """
    if isinstance(condition, dict) and "column" in condition:
        # Leaf condition.
        col = condition.get("column")
        operator = condition.get("operator")
        expected_value = condition.get("value")
        index = COLUMN_INDEXES.get(col)
        if index is None:
            raise KeyError(f"Column '{col}' not found in COLUMN_INDEXES.")
        actual_value = row[index]
        if isinstance(actual_value, datetime.date) and isinstance(expected_value, str):
            expected_value = datetime.datetime.strptime(expected_value, '%Y-%m-%d').date()
        elif isinstance(expected_value, datetime.date) and isinstance(actual_value, str):
            actual_value = datetime.datetime.strptime(actual_value, '%Y-%m-%d').date()
        if operator in ['=', '==']:
            return actual_value == expected_value
        elif operator == '>':
            return actual_value > expected_value
        elif operator == '<':
            return actual_value < expected_value
        elif operator == '>=':
            return actual_value >= expected_value
        elif operator == '<=':
            return actual_value <= expected_value
        elif operator == '!=':
            return actual_value != expected_value
        else:
            raise Exception(f"Unknown operator in leaf condition: {operator}")
    elif isinstance(condition, dict):
        # Compound condition.
        op = condition.get("operator", "").upper()
        if op == "AND":
            return all(evaluate_condition(sub, row) for sub in condition.get("conditions", []))
        elif op == "OR":
            return any(evaluate_condition(sub, row) for sub in condition.get("conditions", []))
        elif op == "NOT":
            return not evaluate_condition(condition.get("condition"), row)
        else:
            raise Exception(f"Unknown compound operator: {op}")
    else:
        return bool(condition)

###############################################################################
# H Table Construction and Aggregation
###############################################################################

class H:
    """
    Each H object represents one group (a unique combination of grouping attribute values)
    and stores both the grouping values and computed aggregate values in a data map.
    
    Aggregate descriptors are dictionaries:
      - Global: {"column": <col>, "function": <func>, "datatype": ...}
      - Group-specific: {"group": <grp>, "column": <col>, "function": <func>, "datatype": ...}
    """
    def __init__(self, grouping_attributes, aggregates, initial_row):
        self.grouping_attributes = grouping_attributes
        self.aggregates_desc = aggregates
        self.initial_row = initial_row
        self._data_map = {}
        self.build_data_map()

    def aggregate_key(self, agg):
        """
        Generate a unique key for an aggregate based on its descriptor.
        For group-specific aggregates, returns e.g. "nj.quant.avg"; for globals, returns e.g. "quant.avg".
        """
        if 'group' in agg:
            return f"{agg['group']}.{agg['column']}.{agg['function']}"
        else:
            return f"{agg['column']}.{agg['function']}"

    def build_data_map(self):
        # Save grouping attribute values.
        for attribute in self.grouping_attributes:
            index = COLUMN_INDEXES[attribute]
            self._data_map[attribute] = self.initial_row[index]
        # Initialize global aggregates only.
        for agg in self.aggregates_desc:
            if 'group' not in agg:
                key = self.aggregate_key(agg)
                func = agg['function']
                col = agg['column']
                index = COLUMN_INDEXES[col]
                val = self.initial_row[index] or 0
                if func in ['sum', 'min', 'max']:
                    self._data_map[key] = val
                elif func == 'count':
                    self._data_map[key] = 1
                elif func == 'avg':
                    self._data_map[key] = {'sum': val, 'count': 1, 'avg': val}
        # Do not initialize group-specific aggregates here.

    def update_data_map(self, agg, row):
        """
        Update the aggregate value in the data map using the given row.
        For group-specific aggregates, if the key is not yet present, initialize it.
        """
        key = self.aggregate_key(agg)
        func = agg['function']
        col = agg['column']
        index = COLUMN_INDEXES[col]
        val = row[index]
        if key not in self._data_map:
            if func in ['sum', 'min', 'max']:
                self._data_map[key] = val
            elif func == 'count':
                self._data_map[key] = 1
            elif func == 'avg':
                self._data_map[key] = {'sum': val, 'count': 1, 'avg': val}
        else:
            if func == 'sum':
                self._data_map[key] += val
            elif func == 'min':
                if val < self._data_map[key]:
                    self._data_map[key] = val
            elif func == 'max':
                if val > self._data_map[key]:
                    self._data_map[key] = val
            elif func == 'count':
                self._data_map[key] += 1
            elif func == 'avg':
                curr = self._data_map[key]
                new_sum = curr['sum'] + val
                new_count = curr['count'] + 1
                self._data_map[key] = {'sum': new_sum, 'count': new_count, 'avg': new_sum/new_count}

    def convert_avg_in_data_map(self):
        for agg in self.aggregates_desc:
            if agg['function'] == 'avg':
                key = self.aggregate_key(agg)
                if key in self._data_map and isinstance(self._data_map[key], dict):
                    avg_val = round(self._data_map[key]['avg'], 2)
                    self._data_map[key] = avg_val

    def get_grouping_values(self):
        return {self._data_map[attr] for attr in self.grouping_attributes}

    @property
    def data_map(self):
        return self._data_map

    def __str__(self):
        return ', '.join(f"{k}: {v}" for k, v in self._data_map.items())

    def __repr__(self):
        return self.__str__()

def build_hTable(grouping_attributes, aggregate_functions, aggregate_groups, such_that_conditions, having_conditions, where_conditions=None):
    """
    Build the H table by grouping the (optionally filtered) DATATABLE rows and computing aggregates.
    
    The global WHERE clause (if provided) is applied to the raw DATATABLE (without grouping).
    Then the filtered rows are grouped by the grouping_attributes, and global aggregates are computed.
    Finally, group-specific aggregates are updated using the SUCH THAT conditions.
    
    Parameters:
        grouping_attributes (list): List of non-aggregate columns used for grouping.
        aggregate_functions (list): List of aggregate descriptor dictionaries.
        aggregate_groups (list): List of group identifiers (from the OVER clause).
        such_that_conditions (list): List of group-specific condition dictionaries.
        having_conditions (dict): The HAVING clause condition structure.
        where_conditions (dict, optional): The global WHERE clause condition structure.
        
    Returns:
        list: A list of H objects (one per unique grouping) that satisfy the HAVING clause.
    """
    if where_conditions:
        filtered_rows = [row for row in DATATABLE if evaluate_condition(where_conditions, row)]
    else:
        filtered_rows = DATATABLE

    hTable = {}
    for row in filtered_rows:
        key = tuple(row[COLUMN_INDEXES[attr]] for attr in grouping_attributes)
        if key in hTable:
            h_obj = hTable[key]
            for agg in aggregate_functions:
                if 'group' not in agg:
                    h_obj.update_data_map(agg, row)
        else:
            h_obj = H(grouping_attributes, aggregate_functions, row)
            hTable[key] = h_obj
    hTable_list = list(hTable.values())
    
    for group in aggregate_groups:
        group_condition = next((cond for cond in such_that_conditions if cond.get('group') == group), None)
        if not group_condition:
            continue
        for row in filtered_rows:
            if evaluate_condition(group_condition, row):
                key = tuple(row[COLUMN_INDEXES[attr]] for attr in grouping_attributes)
                h_obj = hTable.get(key)
                if h_obj:
                    for agg in aggregate_functions:
                        if 'group' in agg and agg['group'] == group:
                            h_obj.update_data_map(agg, row)
    for h_obj in hTable_list:
        h_obj.convert_avg_in_data_map()
    
    if having_conditions:
        hTable_list = [h_obj for h_obj in hTable_list if evaluate_having_clause(having_conditions, h_obj.data_map)]
    
    return hTable_list

def evaluate_having_clause(condition, data_map):
    """
    Recursively evaluate a HAVING clause condition against the H object's data_map.

    The condition can be a compound condition with an "operator" key and either a list
    of subconditions ("conditions") or a single subcondition ("condition"), or it can be
    a leaf condition.

    For a leaf condition that refers to an aggregate, it should have keys "column", "function",
    and optionally "group". In that case, the corresponding key in data_map is constructed as:
      - Global aggregate: "{column}.{function}"
      - Group‑specific aggregate: "{group}.{column}.{function}"

    Otherwise, the condition is assumed to refer to a normal (non‑aggregate) column.

    Returns:
        bool: True if the condition is met, False otherwise.
    """
    if isinstance(condition, dict):
        op = condition.get("operator", "").upper()
        # Handle NOT operator first, regardless of whether "conditions" exists.
        if op == "NOT":
            return not evaluate_having_clause(condition.get("condition"), data_map)

        # For compound conditions with a "conditions" list:
        if "conditions" in condition:
            if op == "AND":
                return all(evaluate_having_clause(sub, data_map) for sub in condition["conditions"])
            elif op == "OR":
                return any(evaluate_having_clause(sub, data_map) for sub in condition["conditions"])
            else:
                raise Exception(f"Unknown compound operator in HAVING clause: {op}")

        # Otherwise, this is a leaf condition.
        # Build the key for an aggregate if one is referenced.
        if "function" in condition:
            if "group" in condition:
                key = f"{condition['group']}.{condition['column']}.{condition['function']}"
            else:
                key = f"{condition['column']}.{condition['function']}"
        else:
            # Assume it's a normal column condition.
            key = condition.get("column")
        
        actual = data_map.get(key)
        expected = condition.get("value")
        
        # If actual is a datetime.date and expected is a string, convert expected.
        if isinstance(actual, datetime.date) and isinstance(expected, str):
            expected = datetime.datetime.strptime(expected, '%Y-%m-%d').date()
        
        if op in ['=', '==']:
            return actual == expected
        elif op == '>':
            return actual > expected
        elif op == '<':
            return actual < expected
        elif op == '>=':
            return actual >= expected
        elif op == '<=':
            return actual <= expected
        elif op == '!=':
            return actual != expected
        else:
            raise Exception(f"Unknown operator in HAVING leaf condition: {op}")
    else:
        return bool(condition)



###############################################################################
# Projection and Ordering
###############################################################################

def project_select_attributes(hTable, select_attributes, aggregate_descriptors):
    """
    Build the final result table by selecting the specified attributes.
    
    The final result includes:
      - The grouping (non-aggregate) columns from select_attributes.
      - Aggregate columns from aggregate_descriptors. For each aggregate descriptor, the key is
        built using the same method as in H.aggregate_key(). If a key is missing in an H object's data_map,
        its value is set to None.
    
    Parameters:
        hTable (list): List of H objects.
        select_attributes (list): List of non-aggregate column names.
        aggregate_descriptors (dict): Dictionary with keys 'global' and 'group_specific',
                                      each a list of aggregate descriptor dictionaries.
    
    Returns:
        list: A list of dictionaries representing the final output rows.
    """
    agg_keys = []
    if 'global' in aggregate_descriptors:
        for agg in aggregate_descriptors['global']:
            key = f"{agg['column']}.{agg['function']}"
            agg_keys.append(key)
    if 'group_specific' in aggregate_descriptors:
        for agg in aggregate_descriptors['group_specific']:
            key = f"{agg['group']}.{agg['column']}.{agg['function']}"
            agg_keys.append(key)
    
    final_attrs = select_attributes + agg_keys
    select_table = []
    for entry in hTable:
        row = {}
        for attr in final_attrs:
            row[attr] = entry.data_map.get(attr, None)
        select_table.append(row)
    return select_table

def order_by_sort(select_table, order_by, grouping_attributes):
    """
    Sort the resulting table according to the ORDER BY clause.
    Instead of sorting on a single column, this version sorts on a tuple of the first N grouping attributes,
    where N is the value of order_by.
    
    Parameters:
        select_table (list): A list of dictionaries representing the result rows.
        order_by (int): The number of grouping attributes to sort by.
        grouping_attributes (list): The list of grouping attributes, in order.
    
    Returns:
        list: The sorted result table.
    """
    if order_by:
        sort_keys = tuple(grouping_attributes[:order_by])
        select_table.sort(key=lambda row: tuple(row.get(attr, 0) for attr in sort_keys))
    return select_table
