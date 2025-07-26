from enum import Enum

class BuffPriority(Enum):
    HEAL = 1
    SHIELD = 2
    DAMAGE_BOOST = 3
    SCORE_BOOST = 4

# Scoring values for different actions
SCORING = {
    "win_game": 150,
    "eliminate_player": 40,
    "open_chest": 5,
    "use_buff": 2,
    "survive_5_seconds": 2,
    "destroy_obstacle": 1,
    "step_on_trap": -10,
    "get_eliminated": -30,
    "segfault": -75
}

# Item priorities (higher means more likely to use)
ITEM_PRIORITY = {
    "Bluescreen": 100,  # Nuke
    "FullRepair": 90,
    "FullBuffer": 85,
    "RepairAndBuffer": 95,
    "Ping": 80,         # Sniper
    "DDOS": 70,         # Minigun
    "ByteCannon": 60,   # Pistol
    "Repair": 50,
    "Buffer": 40,
    "SimpleResistance": 30,
    "WindowsDefender": 20
}