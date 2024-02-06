# Betting workflow functions
# {filename: c:/Users/cigba/sports_app/bets.py}

import logic.models as models
import logic.predict as predict
import results
from src.bets.moneyline import MoneylineBet
from src.bets.spread import SpreadBet
from src.bets.total import TotalBet
from src.bets.parlay_bet import ParlayBet

def place_bets(user, game_data):
    # Get predicted probabilities
    probabilities = predict.get_probabilities(game_data)
    
    # Define betting strategy 
    if probabilities['team1_win'] > 0.6:
        bet_amount = 100
        bet = MoneylineBet("Team 1", bet_amount, game_data['team1_moneyline'])
    elif probabilities['team2_win'] > 0.6:
        bet_amount = 100
        bet = MoneylineBet("Team 2", bet_amount, game_data['team2_moneyline'])
    elif probabilities['team1_spread'] > 0.6:
        bet_amount = 50
        bet = SpreadBet("Team 1", game_data['team1_spread'], bet_amount)
    elif probabilities['team2_spread'] > 0.6:
        bet_amount = 50
        bet = SpreadBet("Team 2", game_data['team2_spread'], bet_amount)
    elif probabilities['total_over'] > 0.6:
        bet_amount = 50
        bet = TotalBet("over", game_data['total'], bet_amount)
    elif probabilities['total_under'] > 0.6:
        bet_amount = 50
        bet = TotalBet("under", game_data['total'], bet_amount)
    else:
        bet_amount = 25
        bets = [MoneylineBet("Team 1", bet_amount, game_data['team1_moneyline']),
                 SpreadBet("Team 1", game_data['team1_spread'], bet_amount),
                 TotalBet("over", game_data['total'], bet_amount)]
        bet = ParlayBet(bets)

    # Place bet
    user.place_bet(bet)

    # Get actual results
    result = results.get_result(game_data)
    
    # Evaluate bet performance
    if result['winner'] == bet.team and bet.amount == bet_amount:
        return "Good bet"
    else:
        return "Bad bet"
    