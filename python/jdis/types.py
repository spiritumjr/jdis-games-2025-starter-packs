import json
from .internal import serde, Union, List, Enum

# Base Types
@serde
class Vector:
    x: int
    y: int

    def __add__(self, other):
        if not isinstance(other, Vector): return NotImplemented
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        if not isinstance(other, Vector): return NotImplemented
        return Vector(self.x - other.x, self.y - other.y)

CardinalDirection = Enum({
    "up": Vector(0, -1),
    "down": Vector(0, 1),
    "left": Vector(-1, 0),
    "right": Vector(1, 0)
})

Direction = Enum({
    "up": CardinalDirection.up,
    "down": CardinalDirection.down,
    "left": CardinalDirection.left,
    "right": CardinalDirection.right,
    "upLeft": CardinalDirection.up + CardinalDirection.left,
    "upRight": CardinalDirection.up + CardinalDirection.right,
    "downLeft": CardinalDirection.down + CardinalDirection.left,
    "downRight": CardinalDirection.down + CardinalDirection.right
})

# Actions
@serde
class MoveAction:
    _ = {"action": "move"}
    position: Vector

@serde
class PhaseAction:
    _ = {"action": "phase"}
    direction: CardinalDirection

@serde
class OpenChestAction:
    _ = {"action": "openChest"}
    position: Vector

@serde
class UseItemBuff:
    _ = {"type": "buff"}

@serde
class UseItemNuke:
    _ = {"type": "nuke"}

@serde
class UseItemProjectile:
    _ = {"type": "projectile"}
    direction: Direction

@serde
class UseItemPlaced:
    _ = {"type": "placed"}
    position: Vector
    placeRectangleVertical: bool

UseItemData = Union("type", UseItemBuff, UseItemNuke, UseItemProjectile, UseItemPlaced)

@serde
class UseItemAction:
    _ = {"action": "useItem"}
    name: str
    data: UseItemData

@serde
class SegFaultAction:
    _ = {"action": "segFault"}

@serde
class SkipAction:
    _ = {"action": "skip"}

Action = Union("action", MoveAction, PhaseAction, OpenChestAction, UseItemAction, SegFaultAction, SkipAction)

# Client -> Server Messages
@serde
class SetActionMessage:
    _ = {"type": "action"}
    action: Action

@serde
class LinkMessage:
    _ = {"type": "link", "clientType": "agent"}
    teamId: str

@serde
class ConfirmMessage:
    _ = {"type": "confirm"}
    teamToken: str

Message = Union("type", SetActionMessage, LinkMessage, ConfirmMessage)

# Types used in Client -> Server Messages
BuffEffect = Enum(["heal", "haste", "score", "shield", "damage", "healAndShield"])

@serde
class Buff:
    name: str
    effect: BuffEffect
    power: int
    duration: int

@serde
class InventoryItemBuff:
    _ = {"type": "buff"}
    name: str
    remaining_ticks: int
    quantity: int

    effect: BuffEffect
    power: int
    duration: int

@serde
class InventoryItemProjectile:
    _ = {"type": "projectile"}
    name: str
    remaining_ticks: int
    quantity: int

    range: int
    speed: int
    damage: int
    pattern: str

@serde
class InventoryItemPlaced:
    _ = {"type": "placed"}
    name: str
    remaining_ticks: int
    quantity: int

    object: str
    pattern: str
    range: int

@serde
class InventoryItemNuke:
    _ = {"type": "nuke"}
    name: str
    remaining_ticks: int
    quantity: int

    damage: int

InventoryItem = Union("type", InventoryItemBuff, InventoryItemProjectile, InventoryItemPlaced, InventoryItemNuke)

@serde
class ObjectResistance:
    _ = {"type": "resistance"}
    position: Vector
    hp: int

@serde
class ObjectChest:
    _ = {"type": "chest"}
    position: Vector

@serde
class ObjectTrap:
    _ = {"type": "trap"}
    position: Vector
    owner: str
    name: str
    damage: int

Object = Union("type", ObjectResistance, ObjectChest, ObjectTrap)

@serde
class Projectile:
    name: str
    position: Vector
    remainingTicks: int
    speed: int
    damage: int

Cell = Enum(["groundPlane", "firewall", "via", "chest", "resistance", "pcb"])

@serde
class Ground:
    width: int
    height: int
    data: List(Cell)
    offset: Vector

@serde
class Player:
    name: str
    score: int
    kills: int
    hp: int
    shield: int
    position: Vector
    last_position: Vector
    inventory: List(InventoryItem)
    effects: List(Buff)

@serde
class GameState:
    player: Player
    enemies: List(Player)
    stats: dict
    ground: Ground
    objects: List(Object)
    projectiles: List(Projectile)

# Server -> Client Messages
@serde
class ServerMessageGameStart:
    _ = {"type": "gameStart"}

@serde
class ServerMessageTickInfo:
    _ = {"type": "tickInfo"}
    state: GameState

@serde
class ServerMessageTickInfoDead:
    _ = {"type": "tickInfoDead"}

@serde
class ServerMessageInfo:
    _ = {"type": "info"}

@serde
class ServerMessageIncorrectLogin:
    _ = {"type": "linkFailed"}

ServerMessage = Union("type", ServerMessageGameStart, ServerMessageTickInfo, ServerMessageTickInfoDead, ServerMessageInfo, ServerMessageIncorrectLogin)
