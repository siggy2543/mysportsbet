from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import pandas as pd
import pickle
import os
def load_dataset():
    # Replace this with code to load your sports data
    return pd.DataFrame({
        'feature1': [1, 2, 3],
        'feature2': [2, 3, 4],
        'label': [0, 1, 0]
    })

def train_model(X, y):
    model = LogisticRegression()
    model.fit(X, y)
    return model

def train_and_predict():
    model_file = 'model.pkl'
    if model_file in os.listdir():
        with open(model_file, 'rb') as f:
            model = pickle.load(f)
    else:
        df = load_dataset()
        X = df[['feature1', 'feature2']]
        y = df['label']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
        model = train_model(X_train, y_train)
        with open(model_file, 'wb') as f:
            pickle.dump(model, f)

    predictions = model.predict(X_test)
    return predictions

if __name__ == '__main__':
    predictions = train_and_predict()
    print(predictions)

# Model training function
def train_model(X, y):
    model = LogisticRegression()
    model.fit(X, y)
    return model

# Load model if exists or train new one
if os.path.exists(model_file):
    model = pickle.load(open(model_file, "rb")) 
else:
    df = load_dataset()
    X = df[['feature1', 'feature2']] 
    y = df['label']
    model = train_model(X, y)
    pickle.dump(model, open(model_file, "wb"))

def make_predictions(X):
    return model.predict(X)
      
# Make predictions   
predictions = model.predict(X_test)