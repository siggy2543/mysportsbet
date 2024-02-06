class ParlayBet:
    def __init__(self, bets):
        self.bets = bets  # A list of bet objects
        self.payout = self.calculate_payout()

    def calculate_payout(self):
        payout = 1
        for bet in self.bets:
            payout *= bet.payout
        return payout

def place_parlay_bet(user, bets):
    parlay = ParlayBet(bets)
    user.place_bet(parlay)