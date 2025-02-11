import re
import src.parser.util as util
import src.parser.table as table
from src.parser.error import ParsingError

###############################################################################
# Main Query Processing Entry Point
###############################################################################

def get_processed_query(query):
    """
    Process the query and return a structured representation.

    Steps:
      1. Prepare the text by normalizing spaces and preserving quoted strings.
      2. Build the query structure by processing each clause.
    """
    prepared_query = prepare_text(query)
    query_struct = build_query_struct(prepared_query)
    return query_struct

###############################################################################
# Query Preparation
###############################################################################

def prepare_text(query):
    """
    Normalize the query text by reducing extra whitespace and handling quoted strings.

    The function converts all non-quoted text to lowercase and then re-inserts the 
    original quoted texts using placeholders.

    Parameters:
        query (str): The raw query string.

    Returns:
        str: A normalized query string.
    """
    # Find and separate quoted strings.
    pattern = r'"[^"]*"|\'[^\']*\''
    quoted_texts = re.findall(pattern, query)
    parts = re.split(f'({pattern})', query)

    # Lowercase all parts that are not within quotes.
    processed_parts = []
    quoted_index = 0
    for part in parts:
        if re.match(pattern, part):
            processed_parts.append(f'QUOTED{quoted_index}')
            quoted_index += 1
        else:
            processed_parts.append(part.lower())

    # Reinsert the quoted texts.
    query = ''.join(processed_parts)
    for i, qt in enumerate(quoted_texts):
        query = query.replace(f'QUOTED{i}', qt, 1)

    return ' '.join(query.split())

###############################################################################
# Building the Query Structure
###############################################################################

def build_query_struct(query):
    """
    Build a structured representation of the query by processing each clause.

    The query is expected to have the following clauses:
      SELECT, FROM, OVER, WHERE, SUCH THAT, HAVING, ORDER BY

    Returns:
        dict: A dictionary containing the processed query structure.

    Raises:
        ParsingError: For any missing or invalid clause.
    """
    struct = {}

    # Define keywords in the expected order.
    keywords = ['select', 'from', 'over', 'where', 'such that', 'having', 'order by']
    keyword_clauses = util.get_keyword_clauses(query, keywords)

    ###########################################################################
    # FROM and OVER Clauses
    ###########################################################################
    # Process FROM clause
    table_name = keyword_clauses[1].strip()
    if table_name == '':
        raise ParsingError('Query must contain a FROM clause')
    datatable, columns_data = table.get_table(table_name)
    if datatable is None:
        raise ParsingError(f"Error accessing table '{table_name}'")
    struct['datatable'] = datatable
    struct['columns'] = columns_data  # Dictionary of column names and their data types
    struct['column_indexes'] = {col: idx for idx, col in enumerate(columns_data.keys())} # Map column indexes top column names in the datatable

    # Process OVER clause
    aggregate_groups = [g.strip() for g in keyword_clauses[2].split(',')]
    for group in aggregate_groups:
        if len(group.split(' ')) != 1:
            raise ParsingError(f"'{group}' could not be parsed as an OVER group")
    struct['aggregate_groups'] = aggregate_groups

    ###########################################################################
    # SELECT Clause
    ###########################################################################
    select_clause = keyword_clauses[0].strip()
    try:
        select_struct = util.parse_select_clause(select_clause, aggregate_groups, struct['columns'])
        struct['select_clause'] = select_struct
    except ParsingError as e:
        raise ParsingError(f"Invalid SELECT clause: {str(e)}")

    ###########################################################################
    # WHERE Clause
    ###########################################################################
    if keyword_clauses[3].strip():
        where_clause = keyword_clauses[3].strip()
        # Check for double logical operators.
        if (' or or ' in where_clause.lower() or 
            ' and and ' in where_clause.lower() or 
            ' not not ' in where_clause.lower()):
            raise ParsingError("Invalid WHERE clause: Double logical operators are not allowed.")
        struct['where_conditions'] = util.parse_where_clause(where_clause, struct['columns'])
    else:
        struct['where_conditions'] = None

    ###########################################################################
    # SUCH THAT Clause
    ###########################################################################
    such_that_conditions = []
    if keyword_clauses[4].strip():
        conditions = keyword_clauses[4].strip().split(',')
        try:
            # Parse each condition and append to the list.
            for condition in conditions:
                parsed_condition = util.parse_such_that_clause(condition.strip(),
                                                               aggregate_groups,
                                                               struct['columns'])
                such_that_conditions.append(parsed_condition)
        except ParsingError as e:
            raise ParsingError(f"Invalid SUCH THAT clause: {str(e)}")
    struct['such_that_conditions'] = such_that_conditions

    ###########################################################################
    # HAVING Clause
    ###########################################################################
    if keyword_clauses[5].strip():
        having_clause = keyword_clauses[5].strip()
        # Check for double logical operators.
        if (' and and ' in having_clause.lower() or 
            ' or or ' in having_clause.lower() or 
            ' not not ' in having_clause.lower()):
            raise ParsingError("Invalid HAVING clause: Double logical operators are not allowed.")
        having_conditions = util.parse_having_clause(having_clause, aggregate_groups, struct['columns'])
        struct['having_conditions'] = having_conditions
    else:
        struct['having_conditions'] = None

    ###########################################################################
    # ORDER BY Clause
    ###########################################################################
    order_by = keyword_clauses[6].strip()
    if order_by:
        try:
            order_num = int(order_by)
            total_columns = (len(select_struct['columns']) +
                             len(select_struct['aggregates'].get('global', [])) +
                             len(select_struct['aggregates'].get('group_specific', [])))
            if order_num < 1 or order_num > total_columns:
                raise ValueError
            struct['order_by'] = order_num
        except ValueError:
            raise ParsingError(f"Invalid ORDER BY value: {order_by}")
    else:
        struct['order_by'] = 0

    ###########################################################################
    # Aggregate Functions Collection from SELECT and HAVING clauses.
    ###########################################################################
    aggregate_functions = []
    if 'aggregates' in select_struct:
        aggregate_functions.extend(select_struct['aggregates'].get('global', []))
        aggregate_functions.extend(select_struct['aggregates'].get('group_specific', []))
    if struct['having_conditions'] is not None:
        aggregates_from_having = util.collect_aggregates_from_having(struct['having_conditions'])
        aggregate_functions.extend(aggregates_from_having)
    struct['aggregate_functions'] = aggregate_functions

    return struct
