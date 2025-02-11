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
    return {k: round_value(v) for k, v in row.items()}


def normalize_result(rows, sort_key='cust'):
    normalized = [normalize_row(row) for row in rows]
    return sorted(normalized, key=lambda row: row.get(sort_key))


def rows_to_value_set(rows):
    return {tuple(row[k] for k in sorted(row.keys())) for row in rows}


def debug_mismatch(expected_set, received_set):
    missing = expected_set - received_set
    extra = received_set - expected_set
    print("\n\n--- DEBUG INFO ---")
    print(f"Total expected rows: {len(expected_set)}")
    print(f"Total received rows: {len(received_set)}")
    print(f"Missing rows ({len(missing)}):", missing)
    print(f"Extra rows ({len(extra)}):", extra)
    print("--- END DEBUG ---\n\n")

def _test_query(sql, esql, sort_key='cust'):
    sql_res = execute_sql_query_through_postgres(sql)
    expected = normalize_result(sql_res, sort_key)
    esql_res = exe.execute(esql)
    received = normalize_result(esql_res, sort_key)

    assert len(expected) == len(received), f"Expected {len(expected)} rows but received {len(received)} rows."
    
    expected_set = rows_to_value_set(expected)
    received_set = rows_to_value_set(received)
    
    if expected_set != received_set:
        debug_mismatch(expected_set, received_set)
    
    assert expected_set == received_set, f"Rows differ: {expected_set ^ received_set}"

##############################
# Test Cases
##############################

@pytest.mark.timeout(5)
def test_execute_not_hanging():
    esql = """
        SELECT cust, prod, day, month, year, state, quant, date, credit
        FROM sales
    """
    result = exe.execute(esql)
    assert result is not None, "execute() returned None or did not complete."

@pytest.mark.timeout(5)
def test_select_all():
    sql = "SELECT * FROM sales"
    esql = """
        SELECT cust, prod, day, month, year, state, quant, date, credit
        FROM sales
    """
    _test_query(sql, esql, sort_key='cust')

@pytest.mark.timeout(5)
def test_basic_query_num():
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
    _test_query(sql, esql, sort_key='cust')

@pytest.mark.timeout(5)
def test_basic_query_boolean():
    sql = """
        SELECT cust, prod, quant, date
        FROM sales
        where credit = true
        GROUP BY cust, prod, quant, date
        
    """
    esql = """
        SELECT cust, prod, quant, date
        FROM sales
        Where credit = true
    """
    _test_query(sql, esql, sort_key='cust')

def test_basic_query_date():
    sql = """
        select cust,prod, sum(quant) from sales
        where date > '2019-04-12'
        group by cust,prod
        
    """
    esql = """
        SELECT cust, prod, quant.sum
        FROM sales
        where date > '2019-04-12'
    """
    _test_query(sql, esql, sort_key='cust')

@pytest.mark.timeout(5)
def test_basic_query_string():
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
    _test_query(sql, esql, sort_key='cust')

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
    _test_query(sql, esql, sort_key='cust')

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
    _test_query(sql, esql, sort_key='cust')

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
    _test_query(sql, esql, sort_key='cust')

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
    _test_query(sql, esql, sort_key='cust')

@pytest.mark.timeout(5)
def test_mf_query_where():
    """
    Compare a multi-fact query (using OVER and SUCH THAT clauses)
    to a standard SQL query using CTEs and LEFT JOINs.
    """
    sql = """
        WITH groups AS (
            SELECT cust, prod
            FROM sales
            GROUP BY cust, prod
        ),
        old AS (
            SELECT cust, prod , sum(quant) as sum, count(quant) as count
            FROM sales
            WHERE date < '2017-1-1' and credit = true
            GROUP BY cust, prod
        ),
		newer AS (
            SELECT cust, prod, sum(quant) as sum, count(quant) as count
            FROM sales
            WHERE date >= '2017-1-1' and date < '2018-12-31' and credit = true
            GROUP BY cust, prod
        ),
		new AS (
            SELECT cust, prod , sum(quant) as sum, count(quant) as count
            FROM sales
            WHERE date >= '2018-12-31' and credit = true
            GROUP BY cust, prod
        )
        SELECT 
            g.cust cust, 
            g.prod prod,
         	old.sum old_sum, old.count old_count,
			newer.sum newer_sum, newer.count newer_count,
			new.sum new_sum,new.count new_count
        FROM groups g
        LEFT JOIN old ON old.cust = g.cust AND old.prod = g.prod
		LEFT JOIN newer ON newer.cust = g.cust AND newer.prod = g.prod
		LEFT JOIN new ON new.cust = g.cust AND new.prod = g.prod
        ORDER BY g.cust, g.prod
    """
    esql = """
        SELECT cust, prod, old.quant.sum, old.quant.count, newer.quant.sum, newer.quant.count, new.quant.sum, new.quant.count
        FROM sales OVER old,newer,new
        WHERE credit = true
        SUCH THAT old.date < '2017-1-1',
                  newer.date >= '2017-1-1' and newer.date < '2018-12-31',
                  new.date >= '2018-12-31' 
    """
    _test_query(sql, esql, sort_key='cust')


if __name__ == '__main__':
    pytest.main()


