from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import pandas as pd
import pickle

# Dummy function to load your dataset
def load_dataset():
    # Replace this with code to load your sports data
    return pd.DataFrame({
        'feature1': [1, 2, 3],
        'feature2': [2, 3, 4],
        'label': [0, 1, 0]
    })

def train_and_predict():
    df = load_dataset()
    X = df[['feature1', 'feature2']]
    y = df['label']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    model = LogisticRegression()
    model.fit(X_train, y_train)
    
    predictions = model.predict(X_test)
    return predictions

if __name__ == '__main__':
    predictions = train_and_predict()
    print(predictions)

def make_predictions(games_df):
    
    # Features for model
    features = ["home_team", "away_team", "home_win_pct"] 
    
    # Prediction target
    target = "home_team_won"

    # Train logistic regression model
    model = LogisticRegression()
    model.fit(games_df[features], games_df[target])

    # Make predictions on new games
    predictions = model.predict(new_games[features])
    
    return predictions

# Load existing model if available
model_file = 'model.pkl'
if model_file in os.listdir():
   with open(model_file, 'rb') as f:
      model = pickle.load(f)
# Train and save new model  
else:   
   # Train model
   X_train, X_test, y_train, y_test = train_test_split(X, y)  
   model = LogisticRegression()
   model.fit(X_train, y_train)
    
   # Save model 
   with open(model_file, 'wb') as f:
      pickle.dump(model, f)

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