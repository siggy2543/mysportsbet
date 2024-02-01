import apis.request.requests as requests
import time

from api_integration import fetch_betting_data, accept_cashout_offer

CACHE_TTL = 60

class CashoutLogic:
    def __init__(self):
        self.cache = {}

    def fetch_cashout_offer(self, url, bet_id, headers):
        if bet_id in self.cache and time.time() - self.cache[bet_id]['timestamp'] < CACHE_TTL:
            return self.cache[bet_id]['offer_amount']

        response = requests.get(url + f"/cashout/{bet_id}", headers=headers)
        offer_amount = response.json().get('offer_amount')

        self.cache[bet_id] = {
            'offer_amount': offer_amount,
            'timestamp': time.time()
        }

        return offer_amount

    def check_and_accept_cashout(self, api_url, bet_id, initial_bet_amount, headers):
        cashout_offer = self.fetch_cashout_offer(api_url, bet_id, headers)

        if cashout_offer and cashout_offer > initial_bet_amount:
            cashout_details = {'bet_id': bet_id}
            accept_cashout_offer(api_url, cashout_details, headers)

# Example Usage
bet_id = 'example_bet_id'
initial_bet_amount = 100

cashout_logic = CashoutLogic()
cashout_logic.check_and_accept_cashout(api_url, bet_id, initial_bet_amount, headers)
