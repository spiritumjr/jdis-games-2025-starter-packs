import typing
from .utils import *

TOKEN = "YOUR_TOKEN_HERE"

async def on_tick(state: GameState) -> typing.Union[MoveAction, PhaseAction, OpenChestAction, UseItemAction, SegFaultAction, SkipAction]:
    """
    fr: Cette fonction est appelée à chaque tick. C'est ici que vous programmez
        le fonctionnement de votre agent en retournant l'action qui sera executée
        sur le serveur.

    en: This function is called every tick. Program the behaviour of your agent
        here by returning the action to be executed on the server.
    """
    print(get_minimap(state))
    move(state, CardinalDirection.up)


async def on_game_start():
    """
    fr: Cette fonction est appelée une seule fois au début de chaque partie.

    en: This function is called at the beginning of each game.
    """
    pass

