from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from .types import *

class Pathfinder:
    """Handles pathfinding using python-pathfinding library"""
    
    def __init__(self):
        self.finder = AStarFinder(diagonal_movement=DiagonalMovement.never)
    
    def find_path(self, start: Vector, end: Vector, memory) -> list[Vector]:
        """Find path from start to end considering known obstacles"""
        print(f"\n=== PATHFINDING REQUEST ===")
        print(f"Start: {start.x},{start.y} | Target: {end.x},{end.y}")
        
        # Create a grid from memory (1 = walkable, 0 = blocked)
        width = 125  # Full map size
        height = 125
        grid_matrix = [[1 for _ in range(width)] for _ in range(height)]
        
        # Mark obstacles
        for pos, cell in memory.known_map.items():
            if cell in [Cell.firewall, Cell.via, Cell.resistance]:
                if 0 <= pos.x < width and 0 <= pos.y < height:
                    grid_matrix[pos.y][pos.x] = 0
        
        grid = Grid(matrix=grid_matrix)
        start_node = grid.node(start.x, start.y)
        end_node = grid.node(end.x, end.y)
        
        print(f"Calculating path from {start.x},{start.y} to {end.x},{end.y}...")
        
        # Find path
        path, runs = self.finder.find_path(start_node, end_node, grid)
        
        print(f"Pathfinding completed in {runs} steps")
        print(f"Path length: {len(path)} steps")
        
        # Convert to Vector objects
        vector_path = [Vector(x, y) for x, y in path]
        
        if len(vector_path) > 1:
            print(f"Next step: {vector_path[1].x},{vector_path[1].y}")
        else:
            print("No valid path found!")
        
        return vector_path
    
    def get_next_move(self, start: Vector, end: Vector, memory) -> Vector:
        """Get the next step toward the target"""
        path = self.find_path(start, end, memory)
        if len(path) > 1:
            return path[1]  # Next step after current position
        return None