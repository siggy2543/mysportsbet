import apis.request.requests as requests
import logger
import database

from api_integration import place_bet
import apis.request.requests as requests

  
def select_parlay_bets(betting_data):

    try:
        # Logic to select top 4 bets based on win ratio
        bets = get_top_bets(betting_data) 
    except Exception as e:
        logger.error("Error selecting bets: %s" % e)

    return bets

def get_top_bets(betting_data):
    
    bets = []
    
    for event in betting_data:
        if 'win_ratio' in event and 'odds' in event:
            bets.append(event)

    # Sort bets by win ratio 
    bets.sort(key=lambda x: x['win_ratio'], reverse=True)

    # Select top 4 bets 
    return bets[:4]

def select_parlay_bets(betting_data):
    try:
        bets = get_top_bets(betting_data)
    except Exception as e:
        logger.error("Error selecting bets: %s" % e)
        return []

    return bets

def get_top_bets(betting_data):
    bets = [event for event in betting_data if 'win_ratio' in event and 'odds' in event]
    bets.sort(key=lambda x: x['win_ratio'], reverse=True)
    return bets[:4]


def create_bet_payload(selected_bets):
    payload = {
        "bet_ids": [b['id'] for b in selected_bets],
        "bet_type": "parlay"
    }
    return payload


def place_parlay_bet(api_url, selected_bets, headers):
    try:
        bet_payload = create_bet_payload(selected_bets)
        response = requests.post(api_url, json=bet_payload, headers=headers)
        database.log_bet(bet_payload)
    except requests.exceptions.RequestException as e:
        logger.error("Failed to place bet: %s" % e)
        return {}

    return response.json()

def create_bet_payload(selected_bets):

    # Populate payload 
    payload = {
        "bet_ids": [b['id'] for b in selected_bets], 
        "bet_type": "parlay"
    }
    
    return payload

# Use Python's type checking and conditional statements to validate API responses.

def validate_betting_data(betting_data):
    if not isinstance(betting_data, list):
        raise ValueError("Invalid data format: Expected a list")
    for event in betting_data:
        if 'event_id' not in event or 'odds' not in event or 'win_ratio' not in event:
            raise ValueError("Missing required event fields")


# Example Usage
api_url = 'https://api.espn.com/bet/odds'
headers = {'Authorization': 'Bearer YOUR_API_TOKEN'}
betting_data = fetch_betting_data(api_url, headers)
selected_bets = select_parlay_bets(betting_data)
place_parlay_bet(api_url, selected_bets, headers)
