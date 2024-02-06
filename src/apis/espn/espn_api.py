import apis.request.requests as requests

API_KEY = "123abc"

class ESPNClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"apikey": API_KEY})

    def get_game_data(self):
        url = "https://api.espn.com/v1/sports"
        resp = self.session.get(url)
        return resp.json()

    def get_odds(self, game):
        # Call API and return odds 
        url = f"https://api.espn.com/v1/odds/{game}"
        resp = self.session.get(url)
        return resp.json()
        