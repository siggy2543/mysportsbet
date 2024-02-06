class SpreadBet:
    def __init__(self, team, spread, amount): 
        self.team = team
        self.spread = spread
        self.amount = amount
        self.payout = self.calculate_payout()

    def calculate_payout(self):
        if self.spread != 0:
            return self.amount * (1 + abs(self.spread) / 100)
        else:
            return self.amount

    def is_favorite_winner(self, result):
        if self.spread != 0:
            return result - self.spread > 0
        else:
            return True

def place_spread_bet(user, team, spread, amount):
    bet = SpreadBet(team, spread, amount)
    user.place_bet(bet, bet.payout)