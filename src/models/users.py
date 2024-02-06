class User:
    def __init__(self, username, balance):
        self.username = username
        self.balance = balance
        self.bets = []

    def place_bet(self, bet):
        if bet <= self.balance:
            self.bets.append(bet)
            self.balance -= bet
            print(f"Bet placed for {self.username}: {bet}")
        else:
            print(f"Insufficient balance for {self.username} to place bet: {bet}")
        # Update balance logic here...        
    def place_parlay_bet(self, bets):
        total_bet = sum(bets)
        if total_bet <= self.balance:
            self.bets.extend(bets)
            self.balance -= total_bet
            print(f"Parlay bet placed for {self.username}: {bets}")
        else:
            print(f"Insufficient balance for {self.username} to place parlay bet: {bets}")
        # Update balance logic here...
