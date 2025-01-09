from pymongo import MongoClient
import pandas as pd

def get_mongo_connection():
    # Connect MongoDB database
    try:
        client = MongoClient('mongodb://127.0.0.1:27017/')
        db = client['academicworld']
        return db
    except Exception as e:
        print(f"Error: {e}")
        return None

def flatten_list(value):
    if isinstance(value, list):
        return ', '.join(map(str, value))
    return value

def convert_dict_to_string(value):
    if isinstance(value, dict):
        return str(value)
    return value

def preprocess_dataframe(df):
    # Ensure compatibility w/ DataTable
    for col in df.columns:
        # Flatten lists to comma separated strs
        if df[col].apply(isinstance, args=(list,)).any():
            df[col] = df[col].apply(flatten_list)
        
        # Convert dicts to str representations
        if df[col].apply(isinstance, args=(dict,)).any():
            df[col] = df[col].apply(convert_dict_to_string)
        
        df[col] = df[col].astype(str) # Convert columns to strs
    
    return df

def mongo_db_data(collection_name, pipeline=None):
    # Get data from database, return as DataFrame
    db = get_mongo_connection()
    if db is None:
        print("Failed to connect to the database.")
        return pd.DataFrame()  # Empty

    try:
        collection = db[collection_name]
        if pipeline:
            data = collection.aggregate(pipeline)
        else:
            data = collection.find({})
        df = pd.DataFrame(list(data))
        if '_id' in df.columns:
            df = df.drop(columns=['_id']) # Remove MongoDB _id field
        
        df = preprocess_dataframe(df) # Preprocess DataFrame to handle complex types
        
        return df
    except Exception as e:
        print(f"Error: {e}")
        return pd.DataFrame()  # Empty
