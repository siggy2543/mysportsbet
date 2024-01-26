# Betting workflow functions
# {filename: c:/Users/cigba/sports_app/bets.py}

import models
import predict
import results

def place_bets():
    # Get predicted probabilities
    probabilities = predict.get_probabilities(game_data)
    
    # Define betting strategy 
    if probabilities['team1_win'] > 0.6:
        bet_amount = 100
    elif probabilities['team2_win'] > 0.6:
        bet_amount = 100
    else:
        bet_amount = 50
    # Place bets
    bet_team1 = bet_amount
    bet_team2 = bet_amount 
    
     # Get actual results
    result = results.get_result(game_data)
    
    # Evaluate bet performance
    if result['winner'] == "Team 1" and bet_team1 > bet_team2:
        return "Good bet"
    elif result['winner'] == "Team 2" and bet_team2 > bet_team1:
        return "Good bet"
    else:
        return "Bad bet"
    
  """   # Calculate odds of each outcome
    odds = {}
    for game in predictions:
        odds[game['id']] = models.calculate_odds(game)
        
    # Filter and select most favorable bets
    best_bets = models.select_best_bets(predictions, odds)
    
    return best_bets """