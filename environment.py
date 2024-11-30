import asyncio
import random
from food import Food
from nest import Nest  # Import the Nest class

class Environment:
    def __init__(self, rows, cols, food_items):
        self.rows = rows
        self.cols = cols
        self.food_items = food_items  # List of Food objects
        self.pheromone_grid = [[0 for _ in range(cols)] for _ in range(rows)]
        self.nest = Nest(rows, cols)  # Create a nest at a random position

    def drop_pheromone(self, position):
        """Set the pheromone level at the given position to 10."""
        x, y = position
        self.pheromone_grid[x][y] = 10


    def remove_food_at(self, position):
        """Remove food at the given position if hp is 0."""
        for food in self.food_items:
            if food.position == position:
                if food.reduce_hp():
                    self.food_items.remove(food)
                break

    def get_neighbors(self, position):
        """Get all neighbors, including diagonals."""
        x, y = position
        neighbors = [
            ((x - 1), y),      # Up
            ((x + 1), y),      # Down
            (x, (y - 1)),      # Left
            (x, (y + 1)),      # Right
            ((x - 1), y - 1),  # Top-left
            ((x - 1), y + 1),  # Top-right
            ((x + 1), y - 1),  # Bottom-left
            ((x + 1), y + 1),  # Bottom-right
        ]
        # Filter neighbors to ensure they are within bounds
        return [(nx, ny) for nx, ny in neighbors if 0 <= nx < self.rows and 0 <= ny < self.cols]


    async def decay_pheromones(self):
        while True:
            for x in range(self.rows):
                for y in range(self.cols):
                    if self.pheromone_grid[x][y] > 0:
                        self.pheromone_grid[x][y] -= 1
            await asyncio.sleep(0.5)  # Decay pheromones every 0.5 seconds

    async def spawn_random_food(self, spawn_interval=10):
        """Spawn a random food item at a random location at random intervals."""
        from food import FOOD_TYPES  # Import FOOD_TYPES directly from the food module
        while True:
            await asyncio.sleep(random.randint(5, spawn_interval))  # Wait for a random time between 5 and `spawn_interval` seconds
            # Generate a random position
            while True:
                x = random.randint(0, self.rows - 1)
                y = random.randint(0, self.cols - 1)
                if (x, y) != self.nest.position:  # Ensure food doesn't spawn at the nest
                    break
            # Select a random food type and HP
            food_type = random.choice(list(FOOD_TYPES.keys()))
            hp_range = FOOD_TYPES[food_type]
            hp = random.randint(hp_range[0], hp_range[1])
            # Add the new food item to the environment
            self.food_items.append(Food((x, y), food_type, hp))
            print(f"Spawned {food_type} at ({x}, {y}) with HP: {hp}")



