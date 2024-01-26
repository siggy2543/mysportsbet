import pandas as pd
from sklearn.model_selection import train_test_split
import ingest
import process
import retrain

def ingest_data():
    # Logic to ingest new data
    ingest.run() 

def process_data():
   # Logic to pre-process data
   process.transform()
   
def retrain_models():
   # Logic to retrain models
   retrain.update()

def load_data():
    """Loads data from CSV into dataframe"""
    df = pd.read_csv('data.csv') 
    return df

def preprocess(df):
    """Preprocesses data for modeling"""
    # transformations
    return df

def split_data(df):
    """Splits data into train and test sets"""
    X = df.drop('target', axis=1) 
    y = df['target']
    X_train, X_test, y_train, y_test = train_test_split(X, y)
    return X_train, X_test, y_train, y_test

def retrain_model():
    """Retrains ML model on new data"""
    df = load_data()
    df = preprocess(df)
    X_train, X_test, y_train, y_test = split_data(df)
    
    # retrain model
    model.fit(X_train, y_train)