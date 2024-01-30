import numpy as np

import numpy as np
from sklearn.preprocessing import StandardScaler

def transform_event_data(raw_data):
    # Feature engineering and preprocessing logic
    
    return processed_data

# Define ORM models for key entities like:
# - Users
# - Bets
# - Results
# - etc.

""" class Bet:
    id: int
    user_id: int 
    event_id: int
    bet_amount: float
    bet_type: str # Moneyline, spread, over/under
    bet_selection: str # Team name, over, under
    odds: float
    stake: float
    payout: float
class Event:
    id: int
    sport: str
    teams: list[str]
    datetime: datetime
    status: str # scheduled, live, finished
    odds: dict
    line: float
class User:
    id: int 
    name: str
    balance: float """

class User(db.Model):
  __table_args__ = {'sqlite_autoincrement': True}
  id = db.Column(db.Integer, primary_key=True) 
  name = db.Column(db.String(80), index=True)

class Prediction(db.Model):
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
  team_id = db.Column(db.Integer, db.ForeignKey('team.id'), index=True)