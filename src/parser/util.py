import re
from datetime import datetime
from src.parser.error import ParsingError

# =============================================================================
# Keyword & Clause Extraction
# =============================================================================

def get_keyword_clauses(query, keywords):
    """
    Split query into clauses based on keywords.

    Parameters:
        query (str): The full query string.
        keywords (list): A list of keywords (e.g., ['select', 'from', ...]).

    Returns:
        List of clause strings corresponding to each keyword.

    Raises:
        ParsingError: If the query is missing required clauses or if keywords appear out of order.
    """
    keyword_indices = []
    keyword_clauses = []
    
    # Find the location of each keyword in the query.
    for keyword in keywords:
        pattern = r'\b' + re.escape(keyword.strip()) + r'\b'
        matches = list(re.finditer(pattern, query))
        if matches:
            keyword_indices.append(matches[0].start())
        else:
            keyword_indices.append(-1)

    # Check that 'select' is the first keyword and starts the query.
    if keyword_indices[0] != 0:
        raise ParsingError("Every query must start with SELECT")

    # Extract clauses based on keyword positions.
    previous_index = 0
    previous_keyword = keywords[0]
    for keyword, keyword_index in zip(keywords[1:], keyword_indices[1:]):
        if keyword_index == -1:
            continue
        if keyword_index < previous_index:
            raise ParsingError(f"Unexpected position of '{keyword.strip().upper()}'")
        clause = query[previous_index + len(previous_keyword):keyword_index].strip()
        if not clause:
            raise ParsingError(f"No {previous_keyword.strip().upper()} argument found")
        keyword_clauses.append(clause)
        previous_index = keyword_index
        previous_keyword = keyword

    clause = query[previous_index + len(previous_keyword):].strip()
    if not clause:
        raise ParsingError(f"No {previous_keyword.strip().upper()} argument found")
    keyword_clauses.append(clause)

    # For any missing keywords, insert an empty clause.
    for i in range(len(keywords)):
        if keyword_indices[i] == -1:
            keyword_clauses.insert(i, '')
            
    return keyword_clauses

# =============================================================================
# SELECT Clause Parsing
# =============================================================================

def parse_select_clause(select_clause, groups, columns):
    """
    Parse the SELECT clause into columns and aggregate expressions.

    Parameters:
        select_clause (str): The SELECT clause string.
        groups (list): List of valid group identifiers.
        columns (dict): Dictionary of available columns and their types.

    Returns:
        dict: A dictionary with keys 'columns' (list of simple column names)
              and 'aggregates' (a dict with keys 'global' and 'group_specific').
    
    Raises:
        ParsingError: If an invalid column or aggregate expression is encountered.
    """
    aggregates = {'global': [], 'group_specific': []}
    columns_list = []
    
    for item in select_clause.split(','):
        item = item.strip()
        if '.' in item:
            aggregate_result = parse_aggregate(item, groups, columns)
            if aggregate_result is None:
                raise ParsingError(f"Invalid aggregate in the SELECT clause: {item}")
            if 'group' in aggregate_result:
                aggregates['group_specific'].append(aggregate_result)
            else:
                aggregates['global'].append(aggregate_result)
        else:
            if item in columns:
                columns_list.append(item)
            else:
                raise ParsingError(f"Invalid column: {item}")

    return {
        'columns': columns_list,
        'aggregates': aggregates
    }


# =============================================================================
# WHERE Clause Parsing
# =============================================================================

def parse_where_clause(where_clause, columns):
    """
    Parse the WHERE clause into a nested structure with support for logical operators and parentheses.

    Parameters:
        where_clause (str): The WHERE clause string.
        columns (dict): Dictionary of available columns.

    Returns:
        dict: A nested dictionary representing the condition structure.
    """
    where_clause = where_clause.strip()

    # Remove outer parentheses if they wrap the entire clause.
    if where_clause.startswith('(') and where_clause.endswith(')'):
        paren_level = 0
        is_outermost = True
        for i, char in enumerate(where_clause):
            if char == '(':
                paren_level += 1
            elif char == ')':
                paren_level -= 1
            if paren_level == 0 and i < len(where_clause) - 1:
                is_outermost = False
                break
        if is_outermost:
            return parse_where_clause(where_clause[1:-1].strip(), columns)

    # Split by top-level OR operators.
    or_conditions = split_by_operator(where_clause, 'or')
    if len(or_conditions) > 1:
        return {
            'operator': 'OR',
            'conditions': [parse_where_clause(cond, columns) for cond in or_conditions]
        }

    # Split by top-level AND operators.
    and_conditions = split_by_operator(where_clause, 'and')
    if len(and_conditions) > 1:
        return {
            'operator': 'AND',
            'conditions': [parse_where_clause(cond, columns) for cond in and_conditions]
        }

    # Handle a leading NOT operator.
    if where_clause.lower().startswith('not '):
        condition = where_clause[4:].strip()
        if condition.startswith('(') and condition.endswith(')'):
            condition = condition[1:-1].strip()
        return {
            'operator': 'NOT',
            'condition': parse_where_clause(condition, columns)
        }

    # Parse as a single condition.
    return parse_where_condition(where_clause, columns)

def parse_where_condition(condition, columns):
    """
    Parse a single condition for the WHERE clause.

    Parameters:
        condition (str): The condition string.
        columns (dict): Dictionary of available columns and their data types.

    Returns:
        dict: A dictionary representing the condition.

    Raises:
        ParsingError: If the condition is invalid or uses an unknown column.
    """
    condition = condition.strip()

    if condition.startswith('(') and condition.endswith(')'):
        condition = condition[1:-1].strip()

    operators = ['>=', '<=', '>', '<', '=']
    operator_pattern = r'\s*(' + '|'.join(re.escape(op) for op in operators) + r')\s*'
    match = re.search(operator_pattern, condition)
    if not match:
        if condition in columns and columns[condition] == 'boolean':
            return {'column': condition, 'operator': '=', 'value': True}
        raise ParsingError(f"Invalid condition: {condition}")

    operator = match.group(1)
    parts = re.split(r'\s*' + re.escape(operator) + r'\s*', condition)
    if len(parts) != 2:
        raise ParsingError(f"Invalid condition: {condition}")

    column = parts[0].strip()
    value = parts[1].strip()
    if operator and value == '':
        raise ParsingError(f"Missing value for condition: {condition}")

    if operator in ['>=', '<=', '>', '<']:
        value = value.strip()
        if re.match(r"^'\d{4}-\d{2}-\d{2}'$|^\"\d{4}-\d{2}-\d{2}\"$", value):
            value = datetime.strptime(value.strip("'\""), '%Y-%m-%d').date()
        else:
            try:
                value = float(value)
            except ValueError:
                raise ParsingError(f"Invalid value for condition: {condition}")
    elif operator == '=':
        value = value.strip()
        if value.lower() in ['true', 'false']:
            value = value.lower() == 'true'
        elif re.match(r"^'\d{4}-\d{2}-\d{2}'$|^\"\d{4}-\d{2}-\d{2}\"$", value):
            value = datetime.strptime(value.strip("'\""), '%Y-%m-%d').date()
        elif (value.startswith("'") and value.endswith("'")) or (value.startswith('"') and value.endswith('"')):
            value = value[1:-1]
        elif value.isdigit():
            value = float(value)
        elif value is None:
            raise ParsingError(f"Missing value for condition: {condition}")
        else:
            raise ParsingError(f"Invalid value for condition: {condition}")
    else:
        value = f"'{value}'"

    if column not in columns:
        raise ParsingError(f"Invalid column: {column}")

    return {
        'column': column,
        'operator': operator,
        'value': value
    }


# =============================================================================
# SUCH THAT Clause Parsing
# =============================================================================

def parse_such_that_clause(condition, groups, columns):
    """
    Parse a condition for a specific group ensuring that each section contains only one group.
    
    This function supports logical operators (OR, AND, NOT) and nested parentheses with the following precedence:
      1. OR (lowest)
      2. AND
      3. NOT (highest)

    Parameters:
        condition (str): The SUCH THAT clause condition.
        groups (list): List of valid group identifiers.
        columns (dict): Dictionary of available columns.

    Returns:
        dict: A dictionary representing the parsed condition.
    
    Raises:
        ParsingError: If the condition is invalid or references multiple groups.
    """
    condition = condition.strip()

    if condition.startswith('(') and condition.endswith(')'):
        paren_level = 0
        is_outermost = True
        for i, char in enumerate(condition):
            if char == '(':
                paren_level += 1
            elif char == ')':
                paren_level -= 1
            if paren_level == 0 and i < len(condition) - 1:
                is_outermost = False
                break
        if is_outermost:
            return parse_such_that_clause(condition[1:-1].strip(), groups, columns)

    or_conditions = split_by_operator(condition, 'or')
    if len(or_conditions) > 1:
        parsed_or_conditions = [parse_such_that_clause(cond, groups, columns) for cond in or_conditions]
        groups_found = {sub['group'] for sub in parsed_or_conditions if 'group' in sub}
        if len(groups_found) != 1:
            raise ParsingError("Multiple groups found in OR conditions. Each section must contain only one group.")
        return {
            'group': parsed_or_conditions[0]['group'],
            'operator': 'OR',
            'conditions': parsed_or_conditions
        }

    and_conditions = split_by_operator(condition, 'and')
    if len(and_conditions) > 1:
        parsed_and_conditions = [parse_such_that_clause(cond, groups, columns) for cond in and_conditions]
        groups_found = {sub['group'] for sub in parsed_and_conditions if 'group' in sub}
        if len(groups_found) != 1:
            raise ParsingError("Multiple groups found in AND conditions. Each section must contain only one group.")
        return {
            'group': parsed_and_conditions[0]['group'],
            'operator': 'AND',
            'conditions': parsed_and_conditions
        }

    if condition.lower().startswith('not '):
        inner_condition = condition[4:].strip()
        if inner_condition.startswith('(') and inner_condition.endswith(')'):
            inner_condition = inner_condition[1:-1].strip()
        return {
            'operator': 'NOT',
            'condition': parse_such_that_clause(inner_condition, groups, columns)
        }

    # Validate that the condition begins with a valid group.
    group_found = None
    for group in groups:
        if condition.startswith(group + '.'):
            group_found = group
            break
    if not group_found:
        raise ParsingError(f"Invalid group condition: {condition}. No valid group found.")

    if any(other_group + '.' in condition for other_group in groups if other_group != group_found):
        raise ParsingError(f"Condition '{condition}' contains multiple groups. Each section must contain only one group.")

    return parse_group_condition(condition, group_found, columns)

def parse_group_condition(condition, group, columns):
    """
    Parse a single condition for a specific group.

    Parameters:
        condition (str): The condition string.
        group (str): The expected group identifier.
        columns (dict): Dictionary of available columns.

    Returns:
        dict: A dictionary representing the parsed condition.

    Raises:
        ParsingError: If the condition is invalid.
    """
    condition = condition.strip()
    if condition.startswith('(') and condition.endswith(')'):
        condition = condition[1:-1].strip()

    operators = ['>=', '<=', '!=', '=', '>', '<']
    operator_pattern = r'\s*(' + '|'.join(re.escape(op) for op in operators) + r')\s*'
    match = re.search(operator_pattern, condition)
    if not match:
        raise ParsingError(f"Invalid condition: {condition}")
    operator = match.group(1)
    parts = re.split(r'\s*' + re.escape(operator) + r'\s*', condition)
    if len(parts) != 2:
        raise ParsingError(f"Invalid condition: {condition}")

    left = parts[0].strip()
    right = parts[1].strip()

    if not left.startswith(group + '.'):
        raise ParsingError(f"Invalid group condition: {condition}")
    column = left[len(group) + 1:]
    if column not in columns:
        raise ParsingError(f"Invalid column: {column}")

    if right.isdigit():
        value = float(right)
    elif right.lower() in ['true', 'false']:
        value = right.lower() == 'true'
    elif re.match(r"^'\d{4}-\d{2}-\d{2}'$", right) or re.match(r'^"\d{4}-\d{2}-\d{2}"$', right):
        value = datetime.strptime(right.strip("'\""), '%Y-%m-%d').date()
    else:
        value = right.strip('"').strip("'")

    return {
        'group': group,
        'column': column,
        'operator': operator,
        'value': value
    }


# =============================================================================
# HAVING Clause Parsing
# =============================================================================

def parse_having_clause(condition, groups, columns):
    """
    Parse the HAVING clause into a nested structure supporting AND, OR, and NOT operators.

    Parameters:
        condition (str): The HAVING clause string.
        groups (list): List of valid group identifiers.
        columns (dict): Dictionary of available columns.

    Returns:
        dict: A nested dictionary representing the HAVING clause.
    """
    condition = condition.strip()
    if condition.startswith('(') and condition.endswith(')'):
        paren_level = 0
        is_outermost = True
        for i, char in enumerate(condition):
            if char == '(':
                paren_level += 1
            elif char == ')':
                paren_level -= 1
            if paren_level == 0 and i < len(condition) - 1:
                is_outermost = False
                break
        if is_outermost:
            return parse_having_clause(condition[1:-1].strip(), groups, columns)

    or_conditions = split_by_operator(condition, 'or')
    if len(or_conditions) > 1:
        return {
            'operator': 'OR',
            'conditions': [parse_having_clause(cond, groups, columns) for cond in or_conditions]
        }

    and_conditions = split_by_operator(condition, 'and')
    if len(and_conditions) > 1:
        return {
            'operator': 'AND',
            'conditions': [parse_having_clause(cond, groups, columns) for cond in and_conditions]
        }

    if condition.lower().startswith('not '):
        inner_condition = condition[4:].strip()
        if inner_condition.startswith('(') and inner_condition.endswith(')'):
            inner_condition = inner_condition[1:-1].strip()
        return {
            'operator': 'NOT',
            'condition': parse_having_clause(inner_condition, groups, columns)
        }

    return parse_having_condition(condition, groups, columns)

def parse_having_condition(condition, groups, columns):
    """
    Parse a single HAVING condition with dot notation (e.g., quant.sum > 100 or g1.quant.avg = 50).

    Parameters:
        condition (str): The condition string.
        groups (list): List of valid group identifiers.
        columns (dict): Dictionary of available columns.

    Returns:
        dict: A dictionary representing the parsed HAVING condition.
    
    Raises:
        ParsingError: If the aggregate expression is invalid.
    """
    condition = condition.strip()
    operators = ['>=', '<=', '!=', '=', '>', '<']
    operator_pattern = r'\s*(' + '|'.join(re.escape(op) for op in operators) + r')\s*'
    match = re.search(operator_pattern, condition)
    if not match:
        raise ParsingError(f"Invalid HAVING condition: {condition}")
    operator = match.group(1)
    parts = re.split(r'\s*' + re.escape(operator) + r'\s*', condition)
    if len(parts) != 2:
        raise ParsingError(f"Invalid HAVING condition: {condition}")
    
    left = parts[0].strip()  # e.g., quant.sum or g1.quant.avg
    right = parts[1].strip()  # e.g., 100

    aggregate_parts = left.split('.')
    if len(aggregate_parts) == 2:  # Global aggregate.
        column, func = aggregate_parts
        group = None
    elif len(aggregate_parts) == 3:  # Group-specific aggregate.
        group, column, func = aggregate_parts
    else:
        raise ParsingError(f"Invalid aggregate expression: {left}")

    if group is not None and group not in groups:
        raise ParsingError(f"Invalid group in aggregate: {group}")
    if column not in columns:
        raise ParsingError(f"Invalid column in aggregate: {column}")
    if func not in ['sum', 'avg', 'min', 'max', 'count']:
        raise ParsingError(f"Invalid aggregate function: {func}")

    parsed_value = parse_value(right, 'numerical')
    if parsed_value is None:
        raise ParsingError(f"Invalid value for condition: {right}")

    if group is not None:
        return {
            'group': group,
            'column': column,
            'function': func,
            'operator': operator,
            'value': parsed_value
        }
    else:
        return {
            'column': column,
            'function': func,
            'operator': operator,
            'value': parsed_value
        }

def collect_aggregates_from_having(having_condition):
    """
    Recursively collect aggregate conditions from a HAVING clause structure.

    Parameters:
        having_condition (dict): A nested HAVING clause structure.

    Returns:
        list: A list of aggregate condition dictionaries (leaf nodes with a 'function' key).
    """
    aggregates = []
    if isinstance(having_condition, dict):
        if 'operator' in having_condition:
            op = having_condition['operator']
            if op in ['AND', 'OR']:
                for sub in having_condition.get('conditions', []):
                    aggregates.extend(collect_aggregates_from_having(sub))
            elif op == 'NOT':
                aggregates.extend(collect_aggregates_from_having(having_condition.get('condition')))
            else:
                if 'function' in having_condition:
                    aggregates.append(having_condition)
        else:
            if 'function' in having_condition:
                aggregates.append(having_condition)
    return aggregates


# =============================================================================
# Helper Functions
# =============================================================================

def parse_aggregate(aggregate, groups, columns):
    """
    Parse an aggregate expression using dot notation (e.g., column.agg or group.column.agg).

    Parameters:
        aggregate (str): The aggregate expression.
        groups (list): List of valid group identifiers.
        columns (dict): Dictionary of available columns.

    Returns:
        dict or None: A dictionary describing the aggregate if valid; otherwise None.
    """
    parts = aggregate.split('.')
    
    if len(parts) == 2:  # Format: column.agg
        column, func = parts
        if column not in columns or func not in ['sum', 'avg', 'min', 'max', 'count']:
            return None
        return {
            'column': column,
            'function': func,
            'datatype': 'numerical'  # Assuming numerical for aggregates
        }
    elif len(parts) == 3:  # Format: group.column.agg
        group, column, func = parts
        if (group not in groups or 
            column not in columns or 
            func not in ['sum', 'avg', 'min', 'max', 'count']):
            return None
        return {
            'group': group,
            'column': column,
            'function': func,
            'datatype': 'numerical'
        }
    return None

def parse_value(value_str, datatype):
    """
    Parse a value string based on the expected datatype.

    Parameters:
        value_str (str): The value as a string.
        datatype (str): The expected datatype ('numerical', 'string', 'boolean', or 'date').

    Returns:
        The parsed value (float, str, bool, or datetime.date) or None if parsing fails.
    """
    value_str = value_str.strip()
    
    if datatype == 'numerical':
        try:
            return float(value_str)
        except ValueError:
            return None
            
    elif datatype == 'string':
        if re.match(r"^'.*'$|^\".*\"$", value_str):
            return value_str.strip("'\"")
        return None
        
    elif datatype == 'boolean':
        if value_str.lower() in ['true', 'false']:
            return value_str.lower() == 'true'
        return None
        
    elif datatype == 'date':
        try:
            return datetime.strptime(value_str.strip("'\""), '%Y-%m-%d').date()
        except ValueError:
            return None
            
    return None

def split_by_operator(condition, operator):
    """
    Split a condition by the given operator while respecting nested parentheses.

    Parameters:
        condition (str): The condition string.
        operator (str): The logical operator (e.g., 'and', 'or') to split by.

    Returns:
        list: A list of condition parts.
    """
    parts = []
    current = ''
    paren_level = 0
    i = 0

    while i < len(condition):
        char = condition[i]

        # Track parentheses.
        if char == '(':
            paren_level += 1
        elif char == ')':
            paren_level -= 1

        # Check for the operator only when not inside parentheses.
        if (char == ' ' and 
            i + 1 + len(operator) <= len(condition) and 
            condition[i + 1:i + 1 + len(operator)].lower() == operator and 
            paren_level == 0):
            parts.append(current.strip())
            current = ''
            i += len(operator) + 1  # Skip operator and following space.
        else:
            current += char
            i += 1

    if current.strip():
        parts.append(current.strip())

    return parts





