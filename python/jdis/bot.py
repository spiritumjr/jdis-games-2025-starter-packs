import typing
from .utils import *
from .strategy import StrategySelector
from .memory import GameMemory

TOKEN = "5dxymvfr"

# Initialize game memory and strategy selector
memory = GameMemory()
strategy_selector = StrategySelector()

async def on_tick(state: GameState) -> typing.Union[MoveAction, PhaseAction, OpenChestAction, UseItemAction, SegFaultAction, SkipAction]:
    """
    Main tick handler - updates memory and selects best action
    """
    # Update game memory with current state
    memory.update(state)
    
    # Print minimap for debugging
    print(get_minimap(state))
    
    # Select best strategy based on current state
    strategy = strategy_selector.select_strategy(state, memory)
    
    return move(state, CardinalDirection.up)
    # Execute the strategy and return the action
    #return await strategy.execute(state, memory)

async def on_game_start():
    """
    Called once at game start - reset memory
    """
    memory.reset()