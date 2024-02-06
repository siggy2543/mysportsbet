class TotalBet:
    def __init__(self, over_under, total, amount): 
        self.over_under = over_under # 'over' or 'under'  
        self.total = total 
        self.amount = amount
        self.payout = self.calculate_payout()

    def calculate_payout(self):
        if self.over_under == 'over':
            return self.amount * 2
        elif self.over_under == 'under':
            return self.amount * 1.5
        else:
            return 0

def place_total_bet(user, over_under, total, amount):
    bet = TotalBet(over_under, total, amount)
    user.place_bet(bet)