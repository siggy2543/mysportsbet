import apis.request.requests as requests
from logger import log_error, log_info

# This module contains the functions to interact with the sports betting API. 
# It includes fetching data, placing bets, and handling cashouts.

def fetch_betting_data(api_url, headers):
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Failed to fetch data from API")

def place_bet(api_url, bet_details, headers):
    response = requests.post(api_url, json=bet_details, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Failed to place bet")

def accept_cashout_offer(api_url, cashout_details, headers):
    response = requests.post(api_url, json=cashout_details, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Failed to accept cashout offer")
    
# Use try-except blocks to catch and log exceptions.    
def fetch_betting_data(api_url, headers):
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as errh:
        log_error(f"Http Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        log_error(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        log_error(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        log_error(f"Error: {err}")

# Example Usage
api_url = 'https://api.espn.com/bet/odds'
headers = {'Authorization': 'Bearer YOUR_API_TOKEN'}
betting_data = fetch_betting_data(api_url, headers)
