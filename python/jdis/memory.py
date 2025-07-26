from .pathfinding import Pathfinder
from .types import *
from collections import defaultdict

class GameMemory:
    """Complete game state memory with all tracking features"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset all memory at game start"""
        print("Resetting game memory...")
        # Core tracking
        self.known_map = {}  # position -> Cell type
        self.opened_chests = set()
        self.firewall_positions = set()
        self.firewall_pattern = None
        self.last_seen = {}  # positions of objects/enemies
        
        # Exploration system
        self.exploration_frontier = set()
        self.map_boundaries = {
            'min_x': 0,
            'max_x': 124,
            'min_y': 0,
            'max_y': 124
        }
        
        # Navigation
        self.pathfinder = Pathfinder()
        self.last_player_position = None

    def update(self, state: GameState):
        """Update all memory with current game state"""
        print(f"\n=== MEMORY UPDATE ===")
        
        # Track player position
        self.last_player_position = state.player.position
        print(f"Player at {state.player.position.x},{state.player.position.y}")

        # Update visible cells
        new_cells = 0
        for y in range(state.ground.height):
            for x in range(state.ground.width):
                pos = Vector(x, y) + state.ground.offset
                cell_type = state.ground.data[y * state.ground.width + x]
                
                if pos not in self.known_map:
                    new_cells += 1
                    # Add adjacent cells to exploration frontier
                    for dx, dy in [(0,1),(1,0),(0,-1),(-1,0)]:
                        neighbor = pos + Vector(dx, dy)
                        if neighbor not in self.known_map:
                            self.exploration_frontier.add(neighbor)
                
                self.known_map[pos] = cell_type
                
                # Track special cells
                if cell_type == Cell.firewall:
                    self.firewall_positions.add(pos)
                elif cell_type == Cell.groundPlane:
                    self._update_boundaries(pos)
        
        print(f"Added {new_cells} new cells to memory")

        # Track objects
        for obj in state.objects:
            self.last_seen[obj.position] = obj
            if isinstance(obj, ObjectChest):
                print(f"Chest at {obj.position.x},{obj.position.y}")
            elif isinstance(obj, ObjectTrap):
                print(f"Trap at {obj.position.x},{obj.position.y} (owner: {obj.owner})")

        # Track enemies
        for enemy in state.enemies:
            self.last_seen[enemy.position] = enemy
            print(f"Enemy {enemy.name} at {enemy.position.x},{enemy.position.y} (HP: {enemy.hp})")

        # Update firewall pattern detection
        if not self.firewall_pattern:
            self._detect_firewall_pattern()

    def _update_boundaries(self, pos: Vector):
        """Track map boundaries based on groundPlane cells"""
        self.map_boundaries['min_x'] = min(self.map_boundaries['min_x'], pos.x)
        self.map_boundaries['max_x'] = max(self.map_boundaries['max_x'], pos.x)
        self.map_boundaries['min_y'] = min(self.map_boundaries['min_y'], pos.y)
        self.map_boundaries['max_y'] = max(self.map_boundaries['max_y'], pos.y)

    def _detect_firewall_pattern(self):
        """Detect firewall spread pattern"""
        if len(self.firewall_positions) < 3:
            return
            
        min_x = min(p.x for p in self.firewall_positions)
        max_x = max(p.x for p in self.firewall_positions)
        min_y = min(p.y for p in self.firewall_positions)
        max_y = max(p.y for p in self.firewall_positions)
        
        if min_x == 0 and max_x == 124 and min_y == 0 and max_y == 124:
            self.firewall_pattern = "center"
        elif len(self.firewall_positions) < 20 and all(p.x in (0, 124) or p.y in (0, 124) for p in self.firewall_positions):
            self.firewall_pattern = "corners"
        else:
            self.firewall_pattern = "random"
        print(f"Firewall pattern detected: {self.firewall_pattern}")

    def is_chest_unopened(self, position: Vector) -> bool:
        """Check if chest hasn't been opened"""
        return position not in self.opened_chests

    def get_cell_type(self, position: Vector) -> Cell:
        """Get cell type from memory"""
        return self.known_map.get(position, Cell.groundPlane)

    def is_position_reachable(self, position: Vector) -> bool:
        """Check if position is pathable"""
        if not self.last_player_position:
            return False
        path = self.pathfinder.find_path(self.last_player_position, position, self)
        return len(path) > 0

    def get_direction_toward(self, target: Vector) -> Vector:
        """Get movement vector toward target"""
        if not self.last_player_position:
            return Vector(0, 0)
        path = self.pathfinder.find_path(self.last_player_position, target, self)
        return path[1] - self.last_player_position if len(path) > 1 else Vector(0, 0)

    def get_safest_direction(self) -> Vector:
        """Get direction away from closest firewall"""
        if not self.firewall_positions or not self.last_player_position:
            return Vector(1, 0)  # Default right
            
        closest = min(self.firewall_positions,
                     key=lambda p: abs(p.x-self.last_player_position.x) + abs(p.y-self.last_player_position.y))
        
        dx = self.last_player_position.x - closest.x
        dy = self.last_player_position.y - closest.y
        
        return Vector(1 if dx < 0 else -1, 0) if abs(dx) > abs(dy) else Vector(0, 1 if dy < 0 else -1)

    def get_firewall_distance(self, position: Vector) -> int:
        """Get distance to nearest firewall"""
        if not self.firewall_positions:
            return float('inf')
        return min(abs(p.x-position.x) + abs(p.y-position.y) for p in self.firewall_positions)

    def get_next_explore_position(self) -> Vector:
        """Get optimal exploration target"""
        # 1. Check frontier for reachable positions
        for pos in sorted(self.exploration_frontier,
                        key=lambda p: abs(p.x-self.last_player_position.x) + abs(p.y-self.last_player_position.y)):
            if self.is_position_reachable(pos):
                return pos
        
        # 2. Fallback to map center if no frontier
        center_x = (self.map_boundaries['min_x'] + self.map_boundaries['max_x']) // 2
        center_y = (self.map_boundaries['min_y'] + self.map_boundaries['max_y']) // 2
        return Vector(center_x, center_y)