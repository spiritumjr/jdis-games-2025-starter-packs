from abc import ABC, abstractmethod
from typing import Union
from .utils import *
from .memory import GameMemory
from .constants import SCORING

class Strategy(ABC):
    """Base strategy class"""
    
    @abstractmethod
    async def execute(self, state: GameState, memory: GameMemory) -> Union[MoveAction, PhaseAction, OpenChestAction, UseItemAction, SegFaultAction, SkipAction]:
        pass
    
    def get_priority(self, state: GameState, memory: GameMemory) -> float:
        """Calculate priority of this strategy (0-100)"""
        return 0

class NukeStrategy(Strategy):
    """Use nuke if available"""
    
    async def execute(self, state: GameState, memory: GameMemory):
        for item in state.player.inventory:
            if isinstance(item, InventoryItemNuke):
                return use_nuke(state, item)
        return None
    
    def get_priority(self, state: GameState, memory: GameMemory) -> float:
        for item in state.player.inventory:
            if isinstance(item, InventoryItemNuke):
                return 100  # Highest priority if we have a nuke
        return 0

class ChestStrategy(Strategy):
    """Open nearby chests"""
    
    async def execute(self, state: GameState, memory: GameMemory):
        for obj in state.objects:
            if isinstance(obj, ObjectChest) and memory.is_chest_unopened(obj.position):
                # Check if chest is reachable
                if memory.is_position_reachable(obj.position):
                    return open_chest(state, obj)
        return None
    
    def get_priority(self, state: GameState, memory: GameMemory) -> float:
        # Higher priority if we see unopened chests
        unopened_chests = sum(1 for obj in state.objects 
                             if isinstance(obj, ObjectChest) and memory.is_chest_unopened(obj.position))
        return min(90, unopened_chests * 30)

class AttackStrategy(Strategy):
    """Attack nearby enemies"""
    
    async def execute(self, state: GameState, memory: GameMemory):
        if not state.enemies:
            return None
            
        # Find best weapon to use
        best_weapon = None
        for item in state.player.inventory:
            if isinstance(item, InventoryItemProjectile) and item.quantity > 0:
                if best_weapon is None or item.damage > best_weapon.damage:
                    best_weapon = item
        
        if best_weapon:
            # Find closest enemy
            closest_enemy = min(state.enemies, 
                              key=lambda e: (e.position - state.player.position).manhattan_distance())
            direction = memory.get_direction_toward(closest_enemy.position)
            return use_projectile(state, best_weapon, direction)
        
        return None
    
    def get_priority(self, state: GameState, memory: GameMemory) -> float:
        if not state.enemies:
            return 0
        # Higher priority if we have weapons and enemies are close
        has_weapons = any(isinstance(item, InventoryItemProjectile) and item.quantity > 0 
                         for item in state.player.inventory)
        return 80 if has_weapons else 0

class DefenseStrategy(Strategy):
    """Defensive actions (healing, shields, walls)"""
    
    async def execute(self, state: GameState, memory: GameMemory):
        # Use healing if low HP
        if state.player.hp < 50:
            for item in state.player.inventory:
                if isinstance(item, InventoryItemBuff) and item.effect == BuffEffect.heal:
                    return use_buff(state, item)
        
        # Use shield if available and low shield
        if state.player.shield < 30:
            for item in state.player.inventory:
                if isinstance(item, InventoryItemBuff) and item.effect == BuffEffect.shield:
                    return use_buff(state, item)
        
        # Place defensive walls if enemies nearby
        if len(state.enemies) > 0:
            for item in state.player.inventory:
                if isinstance(item, InventoryItemPlaced) and "Resistance" in item.name:
                    # Place wall between us and closest enemy
                    closest_enemy = min(state.enemies, 
                                      key=lambda e: (e.position - state.player.position).manhattan_distance())
                    direction = memory.get_direction_toward(closest_enemy.position)
                    return use_placed(state, item, direction)
        
        return None
    
    def get_priority(self, state: GameState, memory: GameMemory) -> float:
        priority = 0
        if state.player.hp < 50:
            priority += 70
        if state.player.shield < 30:
            priority += 50
        if len(state.enemies) > 0:
            priority += 40
        return min(85, priority)

class EscapeFirewallStrategy(Strategy):
    """Escape from approaching firewall"""
    
    async def execute(self, state: GameState, memory: GameMemory):
        # Get safest direction (away from firewall)
        safe_dir = memory.get_safest_direction()
        if safe_dir:
            # Check if we need to phase through walls
            target_pos = state.player.position + safe_dir
            if memory.get_cell_type(target_pos) == Cell.firewall:
                return phase(state, safe_dir)
            else:
                return move(state, safe_dir)
        return None
    
    def get_priority(self, state: GameState, memory: GameMemory) -> float:
        # Higher priority if firewall is close
        firewall_dist = memory.get_firewall_distance(state.player.position)
        return max(0, 90 - firewall_dist * 10)

class ExploreStrategy(Strategy):
    """Enhanced exploration with boundary awareness"""
    
    async def execute(self, state: GameState, memory: GameMemory):
        # First check for reachable chests
        for obj in state.objects:
            if isinstance(obj, ObjectChest) and memory.is_chest_unopened(obj.position):
                path = memory.pathfinder.find_path(state.player.position, obj.position, memory)
                if len(path) > 1:
                    next_step = path[1]
                    print(f"Moving toward chest at {obj.position.x},{obj.position.y}")
                    return move(state, next_step - state.player.position)
        
        # Explore new areas
        explore_target = memory.get_next_explore_position()
        if explore_target:
            path = memory.pathfinder.find_path(state.player.position, explore_target, memory)
            if len(path) > 1:
                next_step = path[1]
                print(f"Exploring toward {explore_target.x},{explore_target.y}")
                return move(state, next_step - state.player.position)
        
        # Fallback: move randomly if stuck
        print("No clear path - making random move")
        return move(state, Vector(1, 0))  # Default to moving right
    
    def get_priority(self, state: GameState, memory: GameMemory) -> float:
        return 25  # Lower than attack/defense priorities

class StrategySelector:
    """Selects the best strategy based on current game state"""
    
    def __init__(self):
        self.strategies = [
            NukeStrategy(),
            EscapeFirewallStrategy(),
            DefenseStrategy(),
            ChestStrategy(),
            AttackStrategy(),
            ExploreStrategy()
        ]
    
    def select_strategy(self, state: GameState, memory: GameMemory) -> Strategy:
        # Get strategy with highest priority
        best_strategy = max(self.strategies, 
                           key=lambda s: s.get_priority(state, memory))
        return best_strategy if best_strategy.get_priority(state, memory) > 0 else ExploreStrategy()