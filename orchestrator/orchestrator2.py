# {filename: c:/Users/cigba/sports_app/orchestrator.py}

import transforms
import authenticate
import integrate
import models.bets as bets
import databases
import logic.models as models
import asyncio
from errors.logger import log_error

async def orchestrate(event_data):
    try:
        # Get new game data
        game_data = await transform_event_data(event_data)
        
        # Save to database
        await save_game_data(game_data)
        
        # Make bets
        bet_result = await place_bets(game_data)
        
        # Log bet results
        await save_bet_results(bet_result)
        
    except Exception as e:
        log_error(f"Orchestration failed: {e}")
        
async def transform_event_data(event_data):
    return await transforms.process()

async def save_game_data(game_data):
    return databases.save_game_data(game_data)

async def place_bets(game_data):  
    return bets.place_bets(game_data)

async def save_bet_results(bet_result):
    return databases.save_bet_results(bet_result)