import requests

API_KEY = "123abc"

def get_game_data():
    url = f"https://api.espn.com/v1/sports?apikey={API_KEY}"
    resp = requests.get(url)
    return resp.json()

# ESPN API client
class ESPNClient:

    def get_odds(self, game):
        # Call API and return odds