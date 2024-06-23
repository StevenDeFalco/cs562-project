import pytest
import tempfile


from src.query_parser.parser import Parser, ParsingError
from src.connect import get_database

# define unit tests for the query parser
# include all edge cases for each clause

database, columns, column_datatypes = get_database()
columns = [col.lower() for col in columns]
column_datatypes = {col.lower(): dtype for col,dtype in column_datatypes.items()}

@pytest.fixture
def test_query_file(request):
    content = request.param
    file = tempfile.NamedTemporaryFile(delete=True, mode='w', suffix='.txt')
    file.write(content)
    file.seek(0)
    filename = file.name
    yield filename
    file.close()

def parse_and_catch_error(file_path):
    try:
        parser = Parser(file_path, columns, column_datatypes)
    except ParsingError as e:
        return str(e)
    return None


# Queries with SELECT errors
no_select = "OVER 2 WHERE 1.prod = prod, 2.prod != prod"
empty_select = "SELECT WHERE cust='Dan'"
select_bad_column = "SELECT cust,product,sum_quant HAVING sum_quant >= 1"
select_wrong_group_aggregate1 = "SELECT cust,month,day,2_avg_quant OVER 1 where 1.year = 2016"
select_wrong_group_aggregate2 = "SELECT cust,month,day,0_avg_quant OVER 7 where 1.year = 2016"
select_bad_aggregate1 = "SELECT cust, div_quant"
select_bad_aggregate2 = "SELECT cust, sum_q"
select_bad_aggregate3 = "SELECT cust, 1_div_quant OVER 1"
select_bad_aggregate4 = "SELECT cust, 1_sum_q OVER 1"

@pytest.mark.parametrize('test_query_file', [no_select], indirect=True)
def test_selecterror1(test_query_file):
    error_message = parse_and_catch_error(test_query_file)
    assert error_message == "Every query must start with SELECT"

@pytest.mark.parametrize('test_query_file', [empty_select], indirect=True)
def test_selecterror2(test_query_file):
    error_message = parse_and_catch_error(test_query_file)
    assert error_message == "No SELECT argument found"

@pytest.mark.parametrize('test_query_file', [select_bad_column], indirect=True)
def test_selecterror3(test_query_file):
    error_message = parse_and_catch_error(test_query_file)
    assert error_message == "'product' is not a valid SELECT argument"

@pytest.mark.parametrize('test_query_file', [select_wrong_group_aggregate1], indirect=True)
def test_selecterror4(test_query_file):
    error_message = parse_and_catch_error(test_query_file)
    assert error_message == "'2_avg_quant' is not a valid SELECT argument"

@pytest.mark.parametrize('test_query_file', [select_wrong_group_aggregate2], indirect=True)
def test_selecterror5(test_query_file):
    error_message = parse_and_catch_error(test_query_file)
    assert error_message == "'0_avg_quant' is not a valid SELECT argument"

@pytest.mark.parametrize('test_query_file', [select_bad_aggregate1], indirect=True)
def test_selecterror6(test_query_file):
    error_message = parse_and_catch_error(test_query_file)
    assert error_message == "'div_quant' is not a valid SELECT argument"

@pytest.mark.parametrize('test_query_file', [select_bad_aggregate2], indirect=True)
def test_selecterror7(test_query_file):
    error_message = parse_and_catch_error(test_query_file)
    assert error_message == "'sum_q' is not a valid SELECT argument"

@pytest.mark.parametrize('test_query_file', [select_bad_aggregate3], indirect=True)
def test_selecterror8(test_query_file):
    error_message = parse_and_catch_error(test_query_file)
    assert error_message == "'1_div_quant' is not a valid SELECT argument"

@pytest.mark.parametrize('test_query_file', [select_bad_aggregate4], indirect=True)
def test_selecterror9(test_query_file):
    error_message = parse_and_catch_error(test_query_file)
    assert error_message == "'1_sum_q' is not a valid SELECT argument"


# Queries with OVER errors

# NOTE: NOT going to work now, chnaged 
empty_over = "select cust over where state='NY'"
non_number_over = "select prod over x,y where cust = 'Dan"

@pytest.mark.parametrize('test_query_file', [empty_over], indirect=True)
def test_overerror1(test_query_file):
    error_message = parse_and_catch_error(test_query_file)
    assert error_message == "No OVER argument found"

@pytest.mark.parametrize('test_query_file', [non_number_over], indirect=True)
def test_overerror2(test_query_file):
    error_message = parse_and_catch_error(test_query_file)
    assert error_message == "'x,y' could not be parsed as the OVER argument"


# Queries with WHERE errors
empty_where = "select cust,prod where "
wrong_group_where = "select cust,state over 2 where 1.prod = 'Apple', 2.prod = 'Jelly', 3.prod = 'Butter'"
wrong_column_where = "select prod over 1 where 1.location='NJ'"
no_group_where = "select prod where location = 'NJ'"
double_equals_where = "select state over 1 where 1.cust == 'Dan'"
bad_comparison_string_where = "select day over 1 where 1.prod = Jelly"
bad_comparison_number_where = "select cust over 1 where 1.day = '5'"
bad_comparison_date_where = "select prod over 1 where 1.date = 'string'"
# no boolean test
and_or_where = "select cust over 1 where 1.prod = 'Apple' and 1.day = 5"       # this should eventually be ok

@pytest.mark.parametrize('test_query_file', [empty_where], indirect=True)
def test_whereerror1(test_query_file):
    error_message = parse_and_catch_error(test_query_file)
    assert error_message == "No WHERE argument found"

@pytest.mark.parametrize('test_query_file', [wrong_group_where], indirect=True)
def test_whereerror2(test_query_file):
    error_message = parse_and_catch_error(test_query_file)
    assert error_message == "Invalid group in the WHERE condition '3.prod = 'Butter''"

@pytest.mark.parametrize('test_query_file', [wrong_column_where], indirect=True)
def test_whereerror3(test_query_file):
    error_message = parse_and_catch_error(test_query_file)
    assert error_message == "WHERE condition '1.location='NJ'' could not be evaluated"

@pytest.mark.parametrize('test_query_file', [no_group_where], indirect=True)
def test_whereerror4(test_query_file):
    error_message = parse_and_catch_error(test_query_file)
    assert error_message == "No group in the WHERE condition 'location = 'NJ''"

@pytest.mark.parametrize('test_query_file', [double_equals_where], indirect=True)
def test_whereerror5(test_query_file):
    error_message = parse_and_catch_error(test_query_file)
    assert error_message == "WHERE condition '1.cust == 'Dan'' could not be evaluated"

@pytest.mark.parametrize('test_query_file', [bad_comparison_string_where], indirect=True)
def test_whereerror6(test_query_file):
    error_message = parse_and_catch_error(test_query_file)
    assert error_message == "WHERE condition '1.prod = Jelly' could not be evaluated"

@pytest.mark.parametrize('test_query_file', [bad_comparison_number_where], indirect=True)
def test_whereerror7(test_query_file):
    error_message = parse_and_catch_error(test_query_file)
    assert error_message == "WHERE condition '1.day = '5'' could not be evaluated"

@pytest.mark.parametrize('test_query_file', [bad_comparison_date_where], indirect=True)
def test_whereerror8(test_query_file):
    error_message = parse_and_catch_error(test_query_file)
    assert error_message == "WHERE condition '1.date = 'string'' could not be evaluated"

@pytest.mark.parametrize('test_query_file', [and_or_where], indirect=True)
def test_whereerror9(test_query_file):
    error_message = parse_and_catch_error(test_query_file)
    assert error_message == "WHERE condition '1.prod = 'Apple' and 1.day = 5' could not be evaluated"


# Queries with HAVING errors
bad_aggregate1_having = "select cust over 1 where 1.prod = 'Apple' having 1_average_quant >= 100 and 2_avg_quant <= 20"
bad_aggregate2_having = "select cust,prod over 2 where 1.cust = 'Dan',2.prod = 'Apple' having 0_quant >= 100"
bad_aggregate3_having = "select cust,month over 3 where 3.prod = 'Jelly',2.prod = 'Apple' having 2_div_quant <= 20"
bad_aggregate4_having = "select cust having 0_sum_quant < 10000"
bad_eval1_having = "SELECT cust HAVING (1+ sum_quant > 7890"
bad_eval2_having = "Select cust having 7 < > 2"
not_aggregate1_having = "select prod having day = 2"

@pytest.mark.parametrize('test_query_file', [bad_aggregate1_having], indirect=True)
def test_havingerror1(test_query_file):
    error_message = parse_and_catch_error(test_query_file)
    assert error_message == "'1_average_quant' cannot be parsed as a HAVING argument"

@pytest.mark.parametrize('test_query_file', [bad_aggregate2_having], indirect=True)
def test_havingerror2(test_query_file):
    error_message = parse_and_catch_error(test_query_file)
    assert error_message == "'0_quant' cannot be parsed as a HAVING argument"

@pytest.mark.parametrize('test_query_file', [bad_aggregate3_having], indirect=True)
def test_havingerror3(test_query_file):
    error_message = parse_and_catch_error(test_query_file)
    assert error_message == "'2_div_quant' cannot be parsed as a HAVING argument"

@pytest.mark.parametrize('test_query_file', [bad_aggregate4_having], indirect=True)
def test_havingerror4(test_query_file):
    error_message = parse_and_catch_error(test_query_file)
    assert error_message == "'0_sum_quant' cannot be parsed as a HAVING argument"

@pytest.mark.parametrize('test_query_file', [bad_eval1_having], indirect=True)
def test_havingerror5(test_query_file):
    error_message = parse_and_catch_error(test_query_file)
    assert error_message == "HAVING could not be evaluated"

@pytest.mark.parametrize('test_query_file', [bad_eval2_having], indirect=True)
def test_havingerror6(test_query_file):
    error_message = parse_and_catch_error(test_query_file)
    assert error_message == "HAVING could not be evaluated"

@pytest.mark.parametrize('test_query_file', [not_aggregate1_having], indirect=True)
def test_havingerror7(test_query_file):
    error_message = parse_and_catch_error(test_query_file)
    assert error_message == "'day' cannot be parsed as a HAVING argument"


# Queries with Order By errors
num0_orderby = "select cust, prod order by 0"
numtoohigh_orderby = "select cust,prod,month order by 4"
notnum_orderby = "select cust,prod order by apple"

@pytest.mark.parametrize('test_query_file', [num0_orderby], indirect=True)
def test_orderby1(test_query_file):
    error_message = parse_and_catch_error(test_query_file)
    assert error_message == "'0' cannot be parsed as an ORDER BY argument"

@pytest.mark.parametrize('test_query_file', [numtoohigh_orderby], indirect=True)
def test_orderby2(test_query_file):
    error_message = parse_and_catch_error(test_query_file)
    assert error_message ==  "'4' cannot be parsed as an ORDER BY argument"

@pytest.mark.parametrize('test_query_file', [notnum_orderby], indirect=True)
def test_orderby3(test_query_file):
    error_message = parse_and_catch_error(test_query_file)
    assert error_message == "'apple' cannot be parsed as an ORDER BY argument"

if __name__ == '__main__':
    pytest.main()


# keep this for when I need to test the output of the query
'''

import psycopg2
import pandas as pd

def upload_file_to_postgresql(file_path, table_name, conn_params):
    # Read the file into a DataFrame
    df = pd.read_csv(file_path)  # Change to pd.read_excel(file_path) for Excel files
    
    # Connect to PostgreSQL
    conn = psycopg2.connect(**conn_params)
    cur = conn.cursor()

    # Create table based on DataFrame columns
    columns = ", ".join([f"{col} TEXT" for col in df.columns])  # Assuming all columns are of type TEXT
    create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns});"
    cur.execute(create_table_query)
    conn.commit()

    # Insert DataFrame data into PostgreSQL table
    for _, row in df.iterrows():
        values = ', '.join([f"'{str(val)}'" for val in row])
        insert_query = f"INSERT INTO {table_name} VALUES ({values});"
        cur.execute(insert_query)
    
    conn.commit()

    # Query the resulting table
    select_query = f"SELECT * FROM {table_name};"
    cur.execute(select_query)
    rows = cur.fetchall()

    # Print the resulting table
    for row in rows:
        print(row)

    # Close the cursor and connection
    cur.close()
    conn.close()

if __name__ == "__main__":
    # Connection parameters to your PostgreSQL database
    conn_params = {
        'dbname': 'your_database_name',
        'user': 'your_username',
        'password': 'your_password',
        'host': 'your_host',
        'port': 'your_port'
    }

    # Path to the file you want to upload
    file_path = 'path/to/your/file.csv'  # or 'path/to/your/file.xlsx' for Excel files

    # Name of the table in PostgreSQL
    table_name = 'your_table_name'

    upload_file_to_postgresql(file_path, table_name, conn_params)

'''












'''








# Define your string
no_select = "OVER 2 WHERE 1.prod = prod, 2.prod != prod"

# Create a temporary file and write the string to it
with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt') as temp_file:
    temp_file.write(no_select)
    temp_file_path = temp_file.name

# Print the path to the temporary file
print(f"String written to temporary file: {temp_file_path}")


class TestQueryParser(unit.TestCase):
    def setUp(self):
        self.database, self.columns, self.column_datatypes = get_database()
       




    @pytest.fixture
def temp_file(request):
    content = request.param
    with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt') as temp_file:
        temp_file.write(content)
        temp_file_path = temp_file.name
    yield temp_file_path
    os.remove(temp_file_path)

@pytest.fixture
def parser(temp_file):
    column_names = ["prod"]
    column_datatypes = ["string"]
    return Parser(temp_file, column_names, column_datatypes)

@pytest.mark.parametrize('temp_file', ["OVER 2 WHERE 1.prod = prod, 2.prod != prod"], indirect=True)
def test_parser_with_content_1(parser):
    assert parser.file is not None
    assert parser.column_names == ["prod"]
    assert parser.column_datatypes == ["string"]

@pytest.mark.parametrize('temp_file', ["OVER 3 WHERE 1.prod = prod, 3.prod != prod"], indirect=True)
def test_parser_with_content_2(parser):
    assert parser.file is not None
    assert parser.column_names == ["prod"]
    assert parser.column_datatypes == ["string"]

    # Queries with SELECT errors
    def test_no_select(self):
        no_select = "OVER 2 WHERE 1.prod = prod, 2.prod != prod"
        with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt') as file:
            file.write(no_select)
            file_path = file.name
        with self.assertRaises(ParsingError) as cm:
            self.parser.parse(no_select)
        self.assertEqual(str(cm.exception), "ParsingError: Query must start with SELECT")

    def test_empty_select(self):
        empty_select = "SELECT WHERE cust='Dan'"
        with self.assertRaises(ParsingError) as cm:
            self.parser.parse(empty_select)
        self.assertEqual(str(cm.exception), "ParsingError: WHERE clause is missing")

    def test_select_bad_column(self):
        select_bad_column = "SELECT cust,product,sum_quant HAVING sum_quant >= 1"
        # Assuming this should also raise ParsingError based on your logic
        with self.assertRaises(ParsingError) as cm:
            self.parser.parse(select_bad_column)
        self.assertEqual(str(cm.exception), "ParsingError: HAVING clause without valid aggregate")

    def test_select_wrong_group_aggregate(self):
        select_wrong_group_aggregate = "SELECT cust,month,day,2_avg_quant OVER 1 where 1.year = 2016"
        # Assuming this should raise a ParsingError
        with self.assertRaises(ParsingError) as cm:
            self.parser.parse(select_wrong_group_aggregate)
        self.assertEqual(str(cm.exception), "ParsingError: HAVING clause without valid aggregate")  # Example message

    def test_select_bad_aggregate(self):
        select_bad_aggregate = "SELECT cust, div_quant"
        with self.assertRaises(ParsingError) as cm:
            self.parser.parse(select_bad_aggregate)
        self.assertEqual(str(cm.exception), "ParsingError: HAVING clause without valid aggregate")  # Example message

if __name__ == '__main__':
    pytest.main()

    '''