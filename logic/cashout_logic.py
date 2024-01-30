from functools import cache
import requests
import time

from api_integration import fetch_betting_data, accept_cashout_offer

# This module contains the logic to check for cashout offers and accept 
# them if they meet the criteria.

CACHE_TTL = 60

""" def check_and_accept_cashout(api_url, bet_id, initial_bet_amount, headers):
    cashout_offer = fetch_cashout_offer(api_url, bet_id, headers)
    if cashout_offer and cashout_offer > initial_bet_amount:
        cashout_details = {'bet_id': bet_id}
        accept_cashout_offer(api_url, cashout_details, headers)

def fetch_cashout_offer(api_url, bet_id, headers):
    # Fetch the current cashout offer for a given bet
    cashout_api_url = f"{api_url}/cashout/{bet_id}"
    response = requests.get(cashout_api_url, headers=headers)
    if response.status_code == 200:
        return response.json().get('offer_amount')
    return None """

@cache
def fetch_cashout_offer(url, bet_id, headers):
    response = requests.get(url + f"/cashout/{bet_id}", headers=headers)
    return response.json().get('offer_amount')

def check_and_accept_cashout(api_url, bet_id, initial_bet_amount, headers):
    start = time.time()
    cashout_offer = fetch_cashout_offer(api_url, bet_id, headers)
    if time.time() - start > CACHE_TTL:
        # Cache expired, clear cache
        fetch_cashout_offer.cache_clear() 
    if cashout_offer and cashout_offer > initial_bet_amount:
        cashout_details = {'bet_id': bet_id}
        accept_cashout_offer(api_url, cashout_details, headers)

# Example Usage
bet_id = 'example_bet_id'
initial_bet_amount = 100
check_and_accept_cashout(api_url, bet_id, initial_bet_amount, headers)
