from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import pandas as pd

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