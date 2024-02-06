class MoneylineBet:
    def __init__(self, team, amount, moneyline):
        self.team = team 
        self.amount = amount
        self.moneyline = moneyline
        self.payout = self.calculate_payout()

    def calculate_payout(self):
        if self.moneyline > 0:
            return self.amount * (self.moneyline / 100)
        else:
            return self.amount / (abs(self.moneyline) / 100)

def place_moneyline_bet(user, team, amount, moneyline):
    bet = MoneylineBet(team, amount, moneyline)
    user.place_bet(bet)
