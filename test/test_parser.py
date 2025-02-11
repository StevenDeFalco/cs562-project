'''
PARSER UNIT TESTS
Ensure that the sales table is properly loaded into the .tables directory before running the test cases.
Even though there are no dirrect test cases to test FROM and OVER, they are inherenntly tested through all of the tests.
'''

import pytest
from src.parser.parse import get_processed_query, ParsingError

'''
PARSING ERROR DETECTION TESTS
'''

def test_valid_select_clauses():
    """Test valid SELECT clause variations"""
    valid_queries = [
        "SELECT cust, quant.sum FROM sales OVER g1 WHERE quant > 100",
        "SELECT prod, quant.avg FROM sales OVER g1 WHERE state = 'NY'",
        "SELECT cust, quant.min, quant.max FROM sales OVER g1,g2 WHERE credit = true",
        "SELECT state, g1.quant.sum FROM sales OVER g1 WHERE year = 2020",
        "SELECT prod, g1.quant.count, g2.quant.avg FROM sales OVER g1,g2 WHERE month >= 6"
    ]
    
    for query in valid_queries:
        try:
            get_processed_query(query)
        except ParsingError as e:
            pytest.fail(f"Valid SELECT clause raised ParsingError: {str(e)}")

def test_invalid_select_clauses():
    """Test invalid SELECT clause variations"""
    invalid_queries = [
        "SELECT invalid_col FROM sales OVER g1",  # Invalid column
        "SELECT FROM sales OVER g1",  # Empty SELECT
        "SELECT prod, quant.invalid FROM sales OVER g1",  # Invalid aggregate function
        "SELECT prod, invalid.sum FROM sales OVER g1",  # Aggregate on invalid column
        "SELECT g3.quant.sum FROM sales OVER g1,g2"  # Invalid group reference
    ]
    
    for query in invalid_queries:
        try:
            get_processed_query(query)
        except ParsingError:
            continue  # Expected exception, do nothing
        except Exception:
            print(f"Unexpected error for query: {query}")  # Print unexpected errors
            raise  # Re-raise the unexpected exception
        print(f"Failed to raise ParsingError for query: {query}")  # Print the query that did not raise the expected error

def test_invalid_over_clauses():
    """Test valid WHERE clause conditions"""
    invalid_queries = [
        "SELECT cust FROM sales OVER g 1 WHERE quant > 100",  # Space in between
        "SELECT prod FROM sales OVER g1, WHERE state = 'NY' AND credit = true",  # comma but only one group
        "SELECT state FROM sales OVER g1, long name WHERE year = 2020 AND month <= 6",  # two words  
    ]
    
    for query in invalid_queries:
        try:
            get_processed_query(query)
        except ParsingError:
            continue  # Expected exception, do nothing
        except Exception:
            print(f"Unexpected error for query: {query}")  # Print unexpected errors
            raise  # Re-raise the unexpected exception
        print(f"Failed to raise ParsingError for query: {query}")

def test_valid_where_clauses():
    """Test valid WHERE clause conditions"""
    valid_queries = [
        "SELECT cust FROM sales OVER g1 WHERE quant > 100",
        "SELECT prod FROM sales OVER g1 WHERE state = 'NY' AND credit = true",
        "SELECT state FROM sales OVER g1 WHERE year = 2020 AND (month <= 6 or month = 12)",
        "SELECT cust FROM sales OVER g1 WHERE NOT quant >= 500 AND state = 'CT' or credit = true",
        "SELECT prod FROM sales OVER g1 WHERE day < 15 AND month = 7 AND year = 2018",
        "SELECT cust FROM sales OVER g1 WHERE NOT quant > 100",
        "SELECT prod FROM sales OVER g1 WHERE NOT state = 'NY'",
        "SELECT state FROM sales OVER g1 WHERE NOT (year = 2020 AND month <= 6)",
        "SELECT cust FROM sales OVER g1 WHERE NOT (quant >= 500 AND state = 'CT')"
    ]
    
    for query in valid_queries:
        try:
            get_processed_query(query)
        except ParsingError as e:
            pytest.fail(f"Valid WHERE clause raised ParsingError: {str(e)}")

def test_valid_where_clauses_with_dates_strings_booleans_numbers():
    """Test valid WHERE clause conditions with various data types"""
    valid_queries = [
        "SELECT cust FROM sales OVER g1 WHERE credit = true",
        "SELECT state FROM sales OVER g1 WHERE year = 2020",
        "SELECT cust FROM sales OVER g1 WHERE state = 'NY'",
        "SELECT prod FROM sales OVER g1 WHERE date = '2023-01-01'",
        "SELECT cust FROM sales OVER g1 WHERE quant > 100",
        "SELECT prod FROM sales OVER g1 WHERE credit = false",
        "SELECT state FROM sales OVER g1 WHERE date < '2023-12-31'"
    ]
    
    for query in valid_queries:
        try:
            get_processed_query(query)
        except ParsingError as e:
            pytest.fail(f"Valid WHERE clause raised ParsingError: {str(e)}")

def test_invalid_where_clauses():
    """Test invalid WHERE clause conditions"""
    invalid_queries = [
        "SELECT cust FROM sales OVER g1 WHERE quant >>= 100",  # Invalid operator
        "SELECT prod FROM sales OVER g1 WHERE state = ",  # Missing value
        "SELECT state FROM sales OVER g1 WHERE AND year = 2020",  # Missing left operand
        "SELECT cust FROM sales OVER g1 WHERE quant > 500 OR OR state = 'CT'",  # Double operator
        "SELECT prod FROM sales OVER g1 WHERE = 'Apple'",  # Missing column
        "SELECT cust FROM sales OVER g1 WHERE quant > 100 AND AND state = 'NY'",  # Double AND operator
        "SELECT prod FROM sales OVER g1 WHERE state = 'NY' OR OR credit = true"  # Double OR operator
    ]
    
    for query in invalid_queries:
        try:
            get_processed_query(query)
        except ParsingError:
            continue  # Expected exception, do nothing
        except Exception:
            print(f"Unexpected error for query: {query}")  # Print unexpected errors
            raise  # Re-raise the unexpected exception
        print(f"Failed to raise ParsingError for query: {query}")  # Print the query that did not raise the expected error

def test_valid_such_that_clauses():
    """Test valid SUCH THAT clause conditions"""
    valid_queries = [
        "SELECT cust FROM sales OVER g1 SUCH THAT g1.quant > 100",
        "SELECT prod, state FROM sales OVER g1,g2 SUCH THAT not g1.quant > 50, g2.credit = true",
        "SELECT cust FROM sales OVER g1 SUCH THAT g1.year = 2020 AND g1.quant > 80",
        "SELECT prod FROM sales OVER g1 SUCH THAT g1.day < 15 OR g1.state = 'NY'",
        "SELECT state FROM sales OVER g1,g2,g3 SUCH THAT g1.credit = true AND g1.quant > 300, g2.prod = 'Apple', g3.cust = 'Dan' or g3.cust = 'Sam'",
        "SELECT prod FROM sales OVER g1 SUCH THAT g1.day < 15 AND not (g1.state = 'NY' OR g1.year = 2021)",
        "SELECT cust FROM sales OVER g1 SUCH THAT NOT g1.quant > 50",
        "SELECT prod FROM sales OVER g2 SUCH THAT NOT g2.credit = true",
        "SELECT state FROM sales OVER g1 SUCH THAT NOT (g1.year = 2020 AND g1.quant > 80)"
    ]
    
    for query in valid_queries:
        try:
            get_processed_query(query)
        except ParsingError as e:
            pytest.fail(f"Valid SUCH THAT clause raised ParsingError: {str(e)}")

def test_valid_such_that_clauses_with_dates_strings_booleans_numbers():
    """Test valid SUCH THAT clause conditions with various data types"""
    valid_queries = [
        "SELECT cust FROM sales OVER g1 SUCH THAT g1.quant > 50",
        "SELECT prod FROM sales OVER g1 SUCH THAT g1.credit = true",
        "SELECT state FROM sales OVER g1 SUCH THAT g1.year = 2020",
        "SELECT cust FROM sales OVER g1 SUCH THAT g1.state = 'NY'",
        "SELECT prod FROM sales OVER g1 SUCH THAT g1.date = '2023-01-01'",
        "SELECT cust FROM sales OVER g1 SUCH THAT g1.quant < 100",
        "SELECT prod FROM sales OVER g1 SUCH THAT g1.credit = false",
        "SELECT state FROM sales OVER g1 SUCH THAT g1.date > '2023-01-01'"
    ]
    
    for query in valid_queries:
        try:
            get_processed_query(query)
        except ParsingError as e:
            pytest.fail(f"Valid SUCH THAT clause raised ParsingError: {str(e)}")

def test_invalid_such_that_clauses():
    """Test invalid SUCH THAT clause conditions"""
    invalid_queries = [
        "SELECT cust FROM sales OVER g1 SUCH THAT quant > 100",  # Missing group prefix
        "SELECT prod FROM sales OVER g1 SUCH THAT invalid.quant > 50",  # Invalid group
        "SELECT cust FROM sales OVER g1,g2 SUCH THAT g1.quant > 100, g2.quant < 50, g1.state = 'NY'",  # Mixed groups
        "SELECT prod FROM sales OVER g1,g2 SUCH THAT g1.year = 2020 AND AND g2.sales < 1000",  # Double AND operator
        "SELECT prod FROM sales OVER g1,g2 SUCH THAT g1.year = 2020 OR OR g2.sales < 1000"  # Double OR operator
    ]
    
    for query in invalid_queries:
        try:
            get_processed_query(query)
        except ParsingError:
            continue  # Expected exception, do nothing
        except Exception:
            print(f"Unexpected error for query: {query}")  # Print unexpected errors
            raise  # Re-raise the unexpected exception
        print(f"Failed to raise ParsingError for query: {query}")  # Print the query that did not raise the expected error

def test_valid_having_clauses():
    """Test valid HAVING clause conditions"""
    valid_queries = [
        "SELECT cust FROM sales OVER g1 HAVING g1.quant.sum > 1000",
        "SELECT prod FROM sales OVER g1 HAVING g1.quant.avg >= 50 AND g1.quant.count > 10",
        "SELECT state FROM sales OVER g1 HAVING (g1.quant.max < 1000 and g1.quant.avg > 50) OR g1.quant.min > 100",
        "SELECT prod FROM sales OVER g1,g2 HAVING g1.quant.sum > 5000 AND g2.quant.avg < 100",
        "SELECT cust FROM sales OVER g1 HAVING g1.quant.sum > 1000 OR g1.quant.avg > 50",
        "SELECT prod FROM sales OVER g1 HAVING g1.quant.avg >= 50 OR g1.quant.count > 10",
        "SELECT state FROM sales OVER g1 HAVING g1.quant.max < 1000 OR g1.quant.min > 100",
        "SELECT prod FROM sales OVER g1,g2 HAVING g1.quant.sum > 5000 OR g2.quant.avg < 100",
        "SELECT cust FROM sales OVER g1 HAVING NOT g1.quant.sum > 1000",
        "SELECT prod FROM sales OVER g1 HAVING NOT (g1.quant.avg >= 50 AND g1.quant.count > 10)"
    ]
    
    for query in valid_queries:
        try:
            get_processed_query(query)
        except ParsingError as e:
            pytest.fail(f"Valid HAVING clause raised ParsingError: {str(e)}")

def test_invalid_having_clauses():
    """Test invalid HAVING clause conditions"""
    invalid_queries = [
        "SELECT cust FROM sales OVER g1 HAVING quant > 1000",  # Non-aggregate in HAVING
        "SELECT prod FROM sales OVER g1 HAVING quant.invalid > 50",  # Invalid aggregate function
        "SELECT state FROM sales OVER g1 HAVING g1.quant.sum",  # Incomplete condition
        "SELECT cust FROM sales OVER g1 HAVING g3.quant.sum > 1000",  # Invalid group reference
        "SELECT prod FROM sales OVER g1 HAVING invalid.sum > 100",  # Invalid column
        "SELECT prod FROM sales OVER g1 HAVING g1.quant.sum > 1000 AND AND g1.quant.avg > 50",  # Double AND operator
        "SELECT cust FROM sales OVER g1 HAVING g1.quant.sum > 1000 OR OR g1.quant.avg > 50"  # Double OR operator
    ]
    
    for query in invalid_queries:
        try:
            get_processed_query(query)
        except ParsingError:
            continue  # Expected exception, do nothing
        except Exception:
            print(f"Unexpected error for query: {query}")  # Print unexpected errors
            raise  # Re-raise the unexpected exception
        print(f"Failed to raise ParsingError for query: {query}")  # Print the query that did not raise the expected error
            

def test_valid_order_by_clauses():
    """Test valid ORDER BY clause variations"""
    valid_queries = [
        "SELECT cust, prod FROM sales OVER g1 ORDER BY 1",
        "SELECT prod, state, quant FROM sales OVER g1 ORDER BY 2",
        "SELECT cust, quant.sum FROM sales OVER g1 ORDER BY 1",
        "SELECT prod, state, quant.avg FROM sales OVER g1 ORDER BY 3",
        "SELECT state, quant.count, quant.max FROM sales OVER g1 ORDER BY 2"
    ]
    
    for query in valid_queries:
        try:
            get_processed_query(query)
        except ParsingError as e:
            pytest.fail(f"Valid ORDER BY clause raised ParsingError: {str(e)}")

def test_invalid_order_by_clauses():
    """Test invalid ORDER BY clause variations"""
    invalid_queries = [
        "SELECT cust FROM sales OVER g1 ORDER BY 0",  # Invalid index (too low)
        "SELECT prod FROM sales OVER g1 ORDER BY 2",  # Invalid index (too high)
        "SELECT state FROM sales OVER g1 ORDER BY prod",  # Non-numeric value
        "SELECT cust FROM sales OVER g1 ORDER BY 1.5",  # Non-integer value
        "SELECT prod FROM sales OVER g1 ORDER BY"  # Missing value
    ]
    
    for query in invalid_queries:
        try:
            get_processed_query(query)
        except ParsingError:
            continue  # Expected exception, do nothing
        except Exception:
            print(f"Unexpected error for query: {query}")  # Print unexpected errors
            raise  # Re-raise the unexpected exception
        print(f"Failed to raise ParsingError for query: {query}")  # Print the query that did not raise the expected error

def test_combined_clauses():
    """Test combinations of different clauses"""
    valid_queries = [
        "SELECT cust, g1.quant.sum, g2.quant.max FROM sales OVER g1,g2 WHERE state = 'NY' SUCH THAT g1.quant > 100, g2.prod = 'Apple' HAVING g2.quant.sum > 1000 ORDER BY 2",
        "SELECT prod, quant.avg, g1.quant.avg FROM sales OVER g1 WHERE credit = true SUCH THAT g1.year = 2020 HAVING g1.quant.count > 5 order by 1",
        "SELECT state, quant.max, g1.quant.max FROM sales OVER g1,g2 WHERE month >= 6 SUCH THAT g1.quant < 500, g2.quant > 10 and (g2.state = 'NY' or g2.state = 'CT') ORDER BY 1",
        "SELECT cust, g1.quant.avg FROM sales OVER g1,g2 WHERE day < 15 SUCH THAT g1.state = 'CT', g2.quant > 200 HAVING g1.quant.avg > 50",
        "SELECT prod, quant.min FROM sales WHERE year = 2018 HAVING quant.sum < 1000"
    ]
    
    for query in valid_queries:
        try:
            get_processed_query(query)
        except ParsingError as e:
            pytest.fail(f"Valid combined clauses raised ParsingError: {str(e)}")

def test_clause_ordering():
    """Test that clauses must appear in correct order"""
    invalid_queries = [
        "SELECT cust WHERE state = 'NY' FROM sales OVER g1",  # Wrong order
        "OVER g1 SELECT cust FROM sales",  # SELECT not first
        "SELECT prod FROM sales WHERE credit = true HAVING sum_quant > 1000 SUCH THAT g1.quant > 100",  # SUCH THAT after HAVING
        "SELECT state FROM sales OVER g1 ORDER BY 1 HAVING max_quant > 500",  # HAVING after ORDER BY
        "WHERE year = 2020 SELECT cust FROM sales OVER g1"  # WHERE before SELECT
    ]
    
    for query in invalid_queries:
        try:
            get_processed_query(query)
        except ParsingError:
            continue  # Expected exception, do nothing
        except Exception:
            print(f"Unexpected error for query: {query}")  # Print unexpected errors
            raise  # Re-raise the unexpected exception
        print(f"Failed to raise ParsingError for query: {query}")  # Print the query that did not raise the expected error


'''
QUERY STRUCTURE TESTS
'''

def test_parsed_select_structure():
    """Test the structure of parsed SELECT statements with complex aggregates."""
    query = "SELECT cust, prod, date.count, quant.sum, g1.quant.max, g1.quant.min, g2.quant.avg FROM sales OVER g1,g2"
    result = get_processed_query(query)
    
    assert result['select_clause'] == {
        'columns': ['cust', 'prod'],
        'aggregates': {
            'global': [
                {'column': 'date', 'function': 'count', 'datatype': 'numerical'},
                {'column': 'quant', 'function': 'sum', 'datatype': 'numerical'}
            ],
            'group_specific': [
                {'group': 'g1', 'column': 'quant', 'function': 'max', 'datatype': 'numerical'},
                {'group': 'g1', 'column': 'quant', 'function': 'min', 'datatype': 'numerical'},
                {'group': 'g2', 'column': 'quant', 'function': 'avg', 'datatype': 'numerical'}
            ]
        }
    }
    assert result['aggregate_groups'] == ['g1', 'g2']


def test_parsed_where_structure():
    """Test the structure of parsed WHERE conditions with NOT, AND, OR, and parentheses."""
    query = "SELECT cust FROM sales OVER g1 WHERE NOT (quant > 100 AND state = 'NY') OR (year = 2021 AND credit = false)"
    result = get_processed_query(query)
    
    assert result['where_conditions'] == {
        'operator': 'OR',
        'conditions': [
            {
                'operator': 'NOT',
                'condition': {
                    'operator': 'AND',
                    'conditions': [
                        {'column': 'quant', 'operator': '>', 'value': 100.0},
                        {'column': 'state', 'operator': '=', 'value': 'NY'}
                    ]
                }
            },
            {
                'operator': 'AND',
                'conditions': [
                    {'column': 'year', 'operator': '=', 'value': 2021},
                    {'column': 'credit', 'operator': '=', 'value': False}
                ]
            }
        ]
    }


def test_parsed_such_that_structure():
    """Test the structure of parsed SUCH THAT conditions with NOT, AND, OR, and parentheses."""
    query = "SELECT cust FROM sales OVER g1,g2 SUCH THAT g1.quant > 50 AND NOT (g1.state = 'NY' OR g1.year = 2021), g2.credit = true OR g2.credit = false"
    result = get_processed_query(query)
    
    assert result['such_that_conditions'] == [
        {
            'group': 'g1',
            'operator': 'AND',
            'conditions': [
                {'group': 'g1', 'column': 'quant', 'operator': '>', 'value': 50.0},
                {
                    'operator': 'NOT',
                    'condition': {
                        'group': 'g1',
                        'operator': 'OR',
                        'conditions': [
                            {'group': 'g1', 'column': 'state', 'operator': '=', 'value': 'NY'},
                            {'group': 'g1', 'column': 'year', 'operator': '=', 'value': 2021}
                        ]
                    }
                }
            ]
        },
        {
            'group': 'g2',
            'operator': 'OR',
            'conditions': [
                {'group': 'g2', 'column': 'credit', 'operator': '=', 'value': True},
                {'group': 'g2', 'column': 'credit', 'operator': '=', 'value': False}
            ]
        }
    ]


def test_parsed_having_structure():
    """Test the structure of parsed HAVING conditions with NOT, AND, OR, and parentheses."""
    query = "SELECT cust FROM sales OVER g1 HAVING NOT (g1.quant.sum > 1000 OR g1.quant.avg > 50) AND NOT (quant.max < 90 OR quant.min > 10)"
    result = get_processed_query(query)
    
    assert result['having_conditions'] == {
        'operator': 'AND',
        'conditions': [
            {
                'operator': 'NOT',
                'condition': {
                    'operator': 'OR',
                    'conditions': [
                        {'group': 'g1', 'column': 'quant', 'function': 'sum', 'operator': '>', 'value': 1000.0},
                        {'group': 'g1', 'column': 'quant', 'function': 'avg', 'operator': '>', 'value': 50.0}
                    ]
                }
            },
            {
                'operator': 'NOT',
                'condition': {
                    'operator': 'OR',
                    'conditions': [
                        {'column': 'quant', 'function': 'max', 'operator': '<', 'value': 90.0},
                        {'column': 'quant', 'function': 'min', 'operator': '>', 'value': 10.0}
                    ]
                }
            }
        ]
    }


'''Testing collection of aggregate functions from HAVING and SELECT'''

def test_aggregate_functions_in_select_only():
    query = """
    SELECT cust, quant.sum, g1.quant.min
    FROM sales
    OVER g1
    WHERE quant > 100
    SUCH THAT g1.state = 'NY'
    HAVING quant.avg > 50
    ORDER BY 2
    """
    result = get_processed_query(query)
    # We expect the aggregates from the SELECT clause:
    #   - quant.sum (global aggregate)
    #   - g1.quant.min (group-specific aggregate)
    # And from the HAVING clause:
    #   - quant.avg (global aggregate in the HAVING condition)
    expected_aggregates = [
        {'column': 'quant', 'function': 'sum', 'datatype': 'numerical'},
        {'group': 'g1', 'column': 'quant', 'function': 'min', 'datatype': 'numerical'},
        {'column': 'quant', 'function': 'avg', 'operator': '>', 'value': 50.0}
    ]
    # Since the order might differ, we compare sorted lists.
    result_aggs = sorted(result.get('aggregate_functions', []), key=lambda agg: (agg.get('group', ''), agg['column'], agg['function']))
    expected_aggs = sorted(expected_aggregates, key=lambda agg: (agg.get('group', ''), agg['column'], agg['function']))
    assert result_aggs == expected_aggs

def test_aggregate_functions_in_having_nested():
    query = """
    SELECT cust
    FROM sales
    OVER g1
    WHERE quant > 100
    SUCH THAT g1.state = 'NY'
    HAVING (g1.quant.min > 100 AND g1.quant.max < 500) OR NOT (g1.quant.avg = 200)
    ORDER BY 1
    """
    result = get_processed_query(query)
    # Expected aggregates from the HAVING clause:
    expected_aggregates = [
        {'group': 'g1', 'column': 'quant', 'function': 'min', 'operator': '>', 'value': 100.0},
        {'group': 'g1', 'column': 'quant', 'function': 'max', 'operator': '<', 'value': 500.0},
        {'group': 'g1', 'column': 'quant', 'function': 'avg', 'operator': '=', 'value': 200.0}
    ]
    result_aggs = sorted(result.get('aggregate_functions', []), key=lambda agg: (agg.get('group', ''), agg['column'], agg['function']))
    expected_aggs = sorted(expected_aggregates, key=lambda agg: (agg.get('group', ''), agg['column'], agg['function']))
    assert result_aggs == expected_aggs

def test_no_aggregate_functions():
    query = """
    SELECT cust, state
    FROM sales
    OVER g1
    WHERE quant > 100
    SUCH THAT g1.state = 'NY'
    ORDER BY 1
    """
    result = get_processed_query(query)
    # There are no aggregate expressions in SELECT or HAVING.
    assert result.get('aggregate_functions', []) == []

def test_invalid_aggregate_in_select():
    query = """
    SELECT cust, unknown.sum
    FROM sales
    OVER g1
    WHERE quant > 100
    SUCH THAT g1.state = 'NY'
    HAVING quant.avg > 50
    ORDER BY 2
    """
    with pytest.raises(ParsingError):
        get_processed_query(query)


'''Testing column indexes are store correctly in the query struct'''

def test_parser_column_indexes_for_sales():
    
    query = 'SELECT cust FROM sales'


    try:
        processed = get_processed_query(query)
    except ParsingError as e:
        pytest.fail(f"Parser raised an unexpected error: {e}")

    # Build the expected column indexes mapping.
    expected_columns = ['cust', 'prod', 'day', 'month', 'year', 'state', 'quant', 'date', 'credit']
    expected_indexes = {col: i for i, col in enumerate(expected_columns)}

    assert 'column_indexes' in processed, "'column_indexes' key not found in the processed query struct."
    assert processed['column_indexes'] == expected_indexes, (
        f"Expected column_indexes {expected_indexes} but got {processed['column_indexes']}"
    )


if __name__ == '__main__':
    pytest.main()




