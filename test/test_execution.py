import os
import psycopg2
import psycopg2.extras
import pytest
from decimal import Decimal
from dotenv import load_dotenv
import src.execution.execute as exe 

##############################
# Helper Functions
##############################

def execute_sql_query_through_postgres(sql):
    """
    Connect to Postgres using environment variables,
    execute the given SQL query, and return the rows as a list of dictionaries.
    """
    load_dotenv()
    host = os.getenv('HOST')
    user = os.getenv('USERNAME')
    password = os.getenv('PASSWORD')
    dbname = os.getenv('DBNAME')
    port = os.getenv('PORT')
    
    conn = psycopg2.connect(
        host=host,
        dbname=dbname,
        user=user,
        password=password,
        port=port,
        cursor_factory=psycopg2.extras.DictCursor
    )
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def round_value(val):
    """
    Recursively convert numeric values (floats and Decimals) to float and round them to 2 decimals.
    For dicts or lists, apply recursively.
    """
    if isinstance(val, (float, int)):
        return round(val, 2)
    elif isinstance(val, Decimal):
        return round(float(val), 2)
    elif isinstance(val, dict):
        return {k: round_value(v) for k, v in val.items()}
    elif isinstance(val, (list, tuple)):
        return type(val)(round_value(x) for x in val)
    else:
        return val

def normalize_row(row):
    """
    Return a new dictionary where all numeric values are rounded to 2 decimals
    (and Decimals are converted to floats).
    """
    return {k: round_value(v) for k, v in row.items()}

def normalize_result(rows, sort_key='cust'):
    """
    Normalize the result rows by rounding numbers and sort them by the given sort_key.
    """
    normalized = [normalize_row(row) for row in rows]
    return sorted(normalized, key=lambda row: row.get(sort_key))

def rows_to_value_set(rows):
    """
    Convert a list of dictionaries (rows) into a set of tuples of values.
    For each row, sort the keys alphabetically and create a tuple of the corresponding values.
    This ignores the column names.
    """
    return {tuple(row[k] for k in sorted(row.keys())) for row in rows}

##############################
# Test Cases
##############################

@pytest.mark.timeout(5)
def test_execute_not_hanging():
    query = """
        SELECT cust, prod, day, month, year, state, quant, date, credit
        FROM sales
    """
    result = exe.execute(query)
    assert result is not None, "execute() returned None or did not complete."

@pytest.mark.timeout(5)
def test_select_all():
    sql = "SELECT * FROM sales"
    esql = """
        SELECT cust, prod, day, month, year, state, quant, date, credit
        FROM sales
    """
    sql_res = execute_sql_query_through_postgres(sql)
    expected = normalize_result(sql_res)
    esql_res = exe.execute(esql)
    received = normalize_result(esql_res)
    
    assert len(expected) == len(received), f"Expected {len(expected)} rows but received {len(received)} rows."
    
    expected_set = rows_to_value_set(expected)
    received_set = rows_to_value_set(received)
    # We use set comparison here. Column names are ignored.
    assert expected_set == received_set, f"Rows differ: {expected_set ^ received_set}"

@pytest.mark.timeout(5)
def test_basic_query1():
    sql = """
        SELECT cust, quant
        FROM sales
        WHERE quant > 100
        GROUP BY cust, quant
    """
    esql = """
        SELECT cust, quant
        FROM sales
        WHERE quant > 100
    """
    sql_res = execute_sql_query_through_postgres(sql)
    expected = normalize_result(sql_res)
    esql_res = exe.execute(esql)
    received = normalize_result(esql_res)
    
    assert len(expected) == len(received), f"Expected {len(expected)} rows but received {len(received)} rows."
    
    expected_set = rows_to_value_set(expected)
    received_set = rows_to_value_set(received)
    assert expected_set == received_set, f"Rows differ: {expected_set ^ received_set}"

@pytest.mark.timeout(5)
def test_basic_query2():
    sql = """
        SELECT cust, prod, quant, date
        FROM sales
        GROUP BY cust, prod, quant, date
        ORDER BY cust
    """
    esql = """
        SELECT cust, prod, quant, date
        FROM sales
        ORDER BY 1
    """
    sql_res = execute_sql_query_through_postgres(sql)
    expected = normalize_result(sql_res)
    esql_res = exe.execute(esql)
    received = normalize_result(esql_res)
    
    assert len(expected) == len(received), f"Expected {len(expected)} rows but received {len(received)} rows."
    
    expected_set = rows_to_value_set(expected)
    received_set = rows_to_value_set(received)
    assert expected_set == received_set, f"Rows differ: {expected_set ^ received_set}"

@pytest.mark.timeout(5)
def test_basic_query3():
    sql = """
        SELECT cust, prod, year
        FROM sales
        WHERE state = 'NY'
        GROUP BY cust, prod, year
    """
    esql = """
        SELECT cust, prod, year
        FROM sales
        WHERE state = 'NY'
    """
    sql_res = execute_sql_query_through_postgres(sql)
    expected = normalize_result(sql_res)
    esql_res = exe.execute(esql)
    received = normalize_result(esql_res)
    
    assert len(expected) == len(received), f"Expected {len(expected)} rows but received {len(received)} rows."
    
    expected_set = rows_to_value_set(expected)
    received_set = rows_to_value_set(received)
    assert expected_set == received_set, f"Rows differ: {expected_set ^ received_set}"


@pytest.mark.timeout(5)
def test_basic_query2():
    sql = """
        SELECT cust, prod, quant, date
        FROM sales
        GROUP BY cust, prod, quant, date
        ORDER BY cust
    """
    esql = """
        SELECT cust, prod, quant, date
        FROM sales
        ORDER BY 1
    """
    sql_res = execute_sql_query_through_postgres(sql)
    expected = normalize_result(sql_res)
    esql_res = exe.execute(esql)
    received = normalize_result(esql_res)
    
    assert len(expected) == len(received), f"Expected {len(expected)} rows but received {len(received)} rows."
    
    expected_set = rows_to_value_set(expected)
    received_set = rows_to_value_set(received)
    assert expected_set == received_set, f"Rows differ: {expected_set ^ received_set}"

@pytest.mark.timeout(5)
def test_basic_query3():
    sql = """
        SELECT cust, prod, year
        FROM sales
        WHERE state = 'NY'
        GROUP BY cust, prod, year
    """
    esql = """
        SELECT cust, prod, year
        FROM sales
        WHERE state = 'NY'
    """
    sql_res = execute_sql_query_through_postgres(sql)
    expected = normalize_result(sql_res)
    esql_res = exe.execute(esql)
    received = normalize_result(esql_res)
    
    assert len(expected) == len(received), f"Expected {len(expected)} rows but received {len(received)} rows."
    
    expected_set = rows_to_value_set(expected)
    received_set = rows_to_value_set(received)
    assert expected_set == received_set, f"Rows differ: {expected_set ^ received_set}"

@pytest.mark.timeout(5)
def test_mf_query():
    """
    Compare a multi-fact query (using OVER and SUCH THAT clauses)
    to a standard SQL query using CTEs and LEFT JOINs.
    """
    sql = """
        WITH groups AS (
            SELECT cust, prod, year
            FROM sales
            GROUP BY cust, prod, year
        ),
        nj AS (
            SELECT cust, prod, year, AVG(quant) AS avg, MAX(quant) AS max
            FROM sales
            WHERE state = 'NJ'
            GROUP BY cust, prod, year
        ),
        ny AS (
            SELECT cust, prod, year, AVG(quant) AS avg, MAX(quant) AS max
            FROM sales
            WHERE state = 'NY'
            GROUP BY cust, prod, year
        ),
        ct AS (
            SELECT cust, prod, year, AVG(quant) AS avg, MAX(quant) AS max
            FROM sales
            WHERE state = 'CT'
            GROUP BY cust, prod, year
        )
        SELECT 
            g.cust, 
            g.prod, 
            g.year, 
            nj.avg AS nj_avg, 
            nj.max AS nj_max, 
            ny.avg AS ny_avg, 
            ny.max AS ny_max,
            ct.avg AS ct_avg, 
            ct.max AS ct_max
        FROM groups g
        LEFT JOIN nj ON nj.cust = g.cust AND nj.prod = g.prod AND nj.year = g.year
        LEFT JOIN ny ON ny.cust = g.cust AND ny.prod = g.prod AND ny.year = g.year
        LEFT JOIN ct ON ct.cust = g.cust AND ct.prod = g.prod AND ct.year = g.year
        ORDER BY g.cust, g.prod, g.year
    """
    esql = """
        SELECT cust, prod, year, nj.quant.avg, nj.quant.max, ny.quant.avg, ny.quant.max, ct.quant.avg, ct.quant.max
        FROM sales OVER nj,ny,ct
        SUCH THAT nj.state = 'NJ', ny.state = 'NY', ct.state = 'CT'
    """
    sql_res = execute_sql_query_through_postgres(sql)
    expected = normalize_result(sql_res)
    esql_res = exe.execute(esql)
    received = normalize_result(esql_res)
    
    assert len(expected) == len(received), f"Expected {len(expected)} rows but received {len(received)} rows."
    
    expected_set = rows_to_value_set(expected)
    received_set = rows_to_value_set(received)
    assert expected_set == received_set, f"Rows differ: {expected_set ^ received_set}"

@pytest.mark.timeout(5)
def test_mf_query_having():
    """
    Compare a multi-fact query (using OVER and SUCH THAT clauses)
    to a standard SQL query using CTEs and LEFT JOINs.
    """
    sql = """
        WITH groups AS (
            SELECT cust, state
            FROM sales
            GROUP BY cust, state
        ),
        q1 AS (
            SELECT cust, state , min(quant) AS min, MAX(quant) AS max
            FROM sales
            WHERE month = 1 or month = 2 or month = 3
            GROUP BY cust, state
        ),
		q2 AS (
            SELECT cust, state , min(quant) AS min, MAX(quant) AS max
            FROM sales
            WHERE month = 4 or month = 5 or month = 6
            GROUP BY cust, state
        ),
		q3 AS (
            SELECT cust, state , min(quant) AS min, MAX(quant) AS max
            FROM sales
            WHERE month = 7 or month = 8 or month = 9
            GROUP BY cust, state
        ),
		q4 AS (
            SELECT cust, state , min(quant) AS min, MAX(quant) AS max
            FROM sales
            WHERE month = 10 or month = 11 or month = 12
            GROUP BY cust, state
        )
        SELECT 
            g.cust, 
            g.state,
            q1.min AS q1_min, 
            q1.max AS q1_max, 
			q2.min AS q2_min, 
            q2.max AS q2_max,
			q3.min AS q3_min, 
            q3.max AS q3_max,
			q4.min AS q4_min, 
            q4.max AS q4_max
        FROM groups g
        LEFT JOIN q1 ON q1.cust = g.cust AND q1.state = g.state
		LEFT JOIN q2 ON q2.cust = g.cust AND q2.state = g.state
		LEFT JOIN q3 ON q3.cust = g.cust AND q3.state = g.state
		LEFT JOIN q4 ON q4.cust = g.cust AND q4.state = g.state
        WHERE q1.max < 1000 and not q2.min < 20
        ORDER BY g.cust, g.state
    """
    esql = """
        SELECT cust, state, q1.quant.min, q1.quant.max, q2.quant.min, q2.quant.max, q3.quant.min, q3.quant.max, q4.quant.min, q4.quant.max
        FROM sales OVER q1,q2,q3,q4
        SUCH THAT q1.month = 1 or q1.month = 2 or q1.month = 3,
                  q2.month = 4 or q2.month = 5 or q2.month = 6,
                  q3.month = 7 or q3.month = 8 or q3.month = 9,
                  q4.month = 10 or q4.month = 11 or q4.month = 12
        HAVING q1.quant.max < 1000 and not q2.quant.min < 20
    """
    #
    sql_res = execute_sql_query_through_postgres(sql)
    expected = normalize_result(sql_res)
    esql_res = exe.execute(esql)
    received = normalize_result(esql_res)
    
    assert len(expected) == len(received), f"Expected {len(expected)} rows but received {len(received)} rows."
    
    expected_set = rows_to_value_set(expected)
    received_set = rows_to_value_set(received)
    assert expected_set == received_set, f"Rows differ: {expected_set ^ received_set}"


if __name__ == '__main__':
    pytest.main()


