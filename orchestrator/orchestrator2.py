# {filename: c:/Users/cigba/sports_app/orchestrator.py}

import transform
import authenticate
import integrate
import bets
import database
import models

def orchestrate(event_data):
    # Get new game data
    game_data = models.transform_event_data(event_data)
    
    # Save to database
    database.save_game_data(game_data)
    
    # Make bets
    bet_result = bets.place_bets(game_data)
    
    # Log bet results
    database.save_bet_results(bet_result)

# Orchestration functions
def transform_data():
    """Handles data transformation"""
    return transform.process()

def handle_auth():
   """Manages user authentication"""
   return authenticate.verify()
   
def integrate_systems():
   """Integrates with legacy systems"""
   return integrate.ingest()