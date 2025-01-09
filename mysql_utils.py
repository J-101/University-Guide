from sqlalchemy import create_engine
import pandas as pd
# https://www.datacamp.com/tutorial/sqlalchemy-tutorial-examples

def get_connection():
    # Connect MySQL database - SQLAlchemy
    try:
        engine = create_engine(
            'mysql+mysqlconnector://tester:SuperSecurePasswordForProject0@127.0.0.1/academicworld'
        )
        return engine
    except Exception as e:
        print(f"Error creating engine: {e}")
        return None

def sql_db_data(query, params=None):
    # Get data from database, return as DataFrame
    connection = get_connection()
    if connection is None:
        print("Failed to create database engine.")
        return pd.DataFrame() # Empty

    try:
        df = pd.read_sql(query, connection, params=params)
        return df
    except Exception as e:
        print(f"Error: {e}")
        return pd.DataFrame() # Empty
