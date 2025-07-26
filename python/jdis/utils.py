from .types import *

# Minimap drawing
CELL_DISPLAY = {
    "firewall":    "\033[38;5;166m█ \033[0m",
    "via":         "\033[30m█ \033[0m",
    "chest":       "\033[38;5;130m▩ \033[0m",
    "resistance":  "\033[38;5;178m█ \033[0m",
    "pcb":         "\033[38;5;22m█ \033[0m",
    "p":           "\033[96m◉ \033[0m",
    "e":           "\033[31m◉ \033[0m",
    "t":           "\033[35m⚠ \033[0m"
}

def build_ground_grid(state: GameState):
    """
    Grille 7x7 avec les composantes du sol
    """
    width, height = state.ground.width, state.ground.height
    grid = [
        [state.ground.data[y * width + x] for x in range(width)]
        for y in range(height)
    ]
    return grid

def get_enemies_position_grid(state : GameState):
    """
    Grille 7x7 Joueur (p) Enemies(e)
    """
    grid = [["." for _ in range(state.ground.width)] for _ in range(state.ground.height)]
    grid[3][3] = 'p'
    for enemie in state.enemies:
        dx = enemie.position.x - state.player.position.x
        dy = enemie.position.y - state.player.position.y
        grid[3+dy][3+dx] = 'e'

    return grid

def get_player_trap_grid(state : GameState) -> str:
    """
    Grille 7x7 ou les pieges = (t)
    """
    grid = [["." for _ in range(state.ground.width)] for _ in range(state.ground.height)]
    for trap in state.objects:
        if isinstance(trap, ObjectTrap):
            dx = trap.position.x - state.player.position.x
            dy = trap.position.y - state.player.position.y
            grid[3+dy][3+dx] = "t"
    return grid

def get_minimap(state: GameState) -> str:
    """
    Crée une grille de 7x7
    """
    ground_grid = build_ground_grid(state)
    enemies_grid = get_enemies_position_grid(state)
    traps_grid = get_player_trap_grid(state)
    minimap = ""
    height, width = len(ground_grid), len(ground_grid[0])

    for y in range(height):
        for x in range(width):
            if enemies_grid[y][x] != ".":
                symbol = enemies_grid[y][x]
            elif traps_grid[y][x] != ".":
                symbol = traps_grid[y][x]
            else:
                symbol = ground_grid[y][x]

            minimap += CELL_DISPLAY.get(symbol, "?")
        minimap += "\n"
    return minimap

# Actions
def move(state: GameState, direction: Vector):
    """
    Action pour le déplacement du joueur dans une direction. Le paramètre
    direction doit être de CardinalDirection.
    """
    return MoveAction(state.player.position + direction)

def phase(state: GameState, direction: CardinalDirection):
    """
    Action pour traverser des murs dans une direction. Le paramètre direction
    doit être de CardinalDirection.
    """
    return PhaseAction(direction)

def open_chest(state: GameState, chest: ObjectChest):
    """
    Action pour ouvrir un coffre à une position relative au joueur. Le paramètre
    direction doait être de CardinalDirection.
    """
    return OpenChestAction(chest.position)

def use_buff(state: GameState, item: InventoryItemBuff):
    """
    Action pour utiliser un item buff.
    """
    return UseItemAction(item.name, UseItemBuff(item.name))

def use_nuke(state: GameState, item: InventoryItemNuke):
    """
    Action pour utiliser un item nuke.
    """
    return UseItemAction(item.name, UseItemNuke())

def use_projectile(state: GameState, item: InventoryItemProjectile, direction: Vector):
    """
    Action pour utiliser un item projectile. Le paramètre direction doit être de
    Direction.
    """
    return UseItemAction(item.name, UseItemProjectile(direction))

def use_placed(state: GameState, item: InventoryItemPlaced, position: Vector, place_rectangle_vertical: bool = False):
    """
    Action pour utiliser un objet à placer. N.B. le paramètre position est
    relatif au joueur.
    """
    return UseItemAction(item.name, UseItemPlaced(state.player.position + position, place_rectangle_vertical))

def segfault(state: GameState):
    """
    Action pour segfault.
    """
    return SegFaultAction()

def do_nothing(state: GameState):
    """
    Action pour ne rien faire pendant un tour.
    """
    return SkipAction()

__all__ = [
    # re-export types
    "Vector", "MoveAction", "PhaseAction", "OpenChestAction", "UseItemBuff", "UseItemNuke", 
    "UseItemProjectile", "UseItemPlaced", "UseItemAction", "SegFaultAction", "SkipAction",
    "Buff", "InventoryItemBuff", "InventoryItemProjectile", "InventoryItemPlaced", "InventoryItemNuke", "ObjectResistance", "ObjectChest", "ObjectTrap", "Projectile",
    "Ground", "Player", "GameState", "CardinalDirection", "Direction", "Cell", "BuffEffect",
    "UseItemData", "Action", "InventoryItem", "Object",
    # export utils
    "get_minimap", "move", "phase", "open_chest", "use_buff", "use_nuke", "use_projectile", "use_placed", "segfault", "do_nothing",
]
