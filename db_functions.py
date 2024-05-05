def grouping(db, groupingVariables):
    """Function to return result after applying GROUP BY <groupingVariables>"""
    for row in db:
        # TODO 
        pass

def create_grouped_table(db, groupingVarNumber, sigma):
    conditions = []
    for condition in sigma:
        split = condition.split(".")
        number = split[0]
        clause = split[1]
        if number == groupingVarNumber:
            conditions.append(clause)
    for cond in conditions: 
        
