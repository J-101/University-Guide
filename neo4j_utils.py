from neo4j import GraphDatabase
import pandas as pd

def get_neo4j_connection(uri, user, password):
    return GraphDatabase.driver(uri, auth = (user, password))

def close_neo4j_connection(driver):
    driver.close()

def run_neo4j_query(driver, query, database="academicworld"):
    with driver.session(database = database) as session:
        result = session.run(query)
        data = []
        for record in result:
            row = {key: str(record[key]) for key in record.keys()}  # Convert vals to strs for display
            data.append(row)
        return pd.DataFrame(data)

# Usage example:
def neo4j_data(query):
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "CS411SQL@Illinois"
    driver = get_neo4j_connection(uri, user, password)
    df = run_neo4j_query(driver, query)
    close_neo4j_connection(driver)
    return df
