import json
import apis.request.requests as requests
import json
import apis.request.requests as requests

def place_parlay_bet(user_selections):

    # Call odds API to get latest odds
    odds_response = requests.get("http://api.odds.com/v1/odds", params={"sports": "nba,nfl"})
    odds_data = json.loads(odds_response.text)
    
    # Create parlay bet payload
    bet_payload = {
        "wager": 100,
        "legs": [] 
    }

    for sel in user_selections:
        # Lookup odds for selection
        odds = lookup_odds(odds_data, sel["team"], sel["game"])
        leg = {
            "team": sel["team"],
            "odds": odds,
            "to_win": odds * 100
        }
        bet_payload["legs"].append(leg)

    # Call bet placement API 
    response = requests.post("http://api.bets.com/v1/parlay", json=bet_payload)

    print(response.text)

def get_odds_data():
    # Call odds API to get latest odds
    odds_response = requests.get("http://api.odds.com/v1/odds", params={"sports": "nba,nfl"})
    return json.loads(odds_response.text)

def lookup_odds(odds_data, team, game):
    # Implementation to lookup odds for given team & game
    return 2.5

def place_parlay_bet(user_selections, odds_data):
    # Create parlay bet payload
    bet_payload = {
        "wager": 100,
        "legs": [
            {
                "team": sel["team"],
                "odds": lookup_odds(odds_data, sel["team"], sel["game"]),
                "to_win": lookup_odds(odds_data, sel["team"], sel["game"]) * 100
            }
            for sel in user_selections
        ]
    }

    # Call bet placement API 
    response = requests.post("http://api.bets.com/v1/parlay", json=bet_payload)

    print(response.text)
