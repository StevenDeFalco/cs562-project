
import random

# Function to add random boolean to each insert statement
def add_random_boolean_to_inserts(input_file, output_file):
    with open(input_file, 'r') as file:
        lines = file.readlines()
    
    updated_lines = []
    for line in lines:
        if line.lower().startswith("insert into sales values"):
            line = line.strip()
            # Find the position of the last closing parenthesis
            last_parenthesis_index = line.rfind(')')
            # Insert the random boolean before the last closing parenthesis
            random_boolean = str(random.choice([True, False])).lower()
            updated_line = line[:last_parenthesis_index] + f", {random_boolean}" + line[last_parenthesis_index:]
            updated_lines.append(updated_line + '\n')
        else:
            updated_lines.append(line)

    with open(output_file, 'w') as file:
        file.writelines(updated_lines)

# Usage example
input_file = 'load_sales_10000_table.sql'
output_file = 'updated_sales_inserts.sql'
add_random_boolean_to_inserts(input_file, output_file)
