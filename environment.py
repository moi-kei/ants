import asyncio
import random
from food import Food
from nest import Nest

class Environment:
    def __init__(self, rows, cols, food_items, nests):
        self.rows = rows
        self.cols = cols
        self.food_items = food_items  # List of Food objects
        self.nests = nests  # List of Nest objects
        # Separate pheromone grids for each nest, keyed by their color
        self.pheromone_grids = {nest.color: [[0 for _ in range(cols)] for _ in range(rows)] for nest in nests}

    def drop_pheromone(self, position, color):
        """Set the pheromone level at the given position to 10 for the specified nest color."""
        x, y = position
        self.pheromone_grids[color][x][y] = 10

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
            for color, grid in self.pheromone_grids.items():
                for x in range(self.rows):
                    for y in range(self.cols):
                        if grid[x][y] > 0:
                            grid[x][y] -= 1
            await asyncio.sleep(1)  # Decay pheromones every 0.5 seconds

    async def spawn_random_food(self, spawn_interval=10):
        """Spawn a random food item at a random location at random intervals."""
        from food import FOOD_TYPES  # Import FOOD_TYPES directly from the food module

        # Define sizes for each food type (width, height)
        FOOD_SIZES = {
            "Berry": (2, 3),  # 2x2
            "Nut": (2, 2),    # 2x2
            "Leaf": (4, 4),   # 4x4
            "Bug": (8, 3),    # 3x6
        }

        while True:
            await asyncio.sleep(random.randint(5, spawn_interval))  # Wait for a random time

            max_attempts = 100  # Prevent infinite loops
            for _ in range(max_attempts):
                x = random.randint(0, self.rows - 1)
                y = random.randint(0, self.cols - 1)

                # Select a random food type
                food_type = random.choices(
                    list(FOOD_TYPES.keys()),
                    weights=[50, 50, 30, 20],  # Adjust the probabilities
                    k=1
                )[0]
                food_width, food_height = FOOD_SIZES[food_type]

                # Check for overlap with existing food items
                overlaps = False
                for food in self.food_items:
                    fx, fy = food.position
                    fwidth, fheight = FOOD_SIZES[food.food_type]
                    if (x < fx + fwidth and x + food_width > fx and
                            y < fy + fheight and y + food_height > fy):
                        overlaps = True
                        break

                if overlaps:
                    continue

                # Check for overlap with nests
                overlaps_with_nest = any(
                    x < nx + 1 and x + food_width > nx and
                    y < ny + 1 and y + food_height > ny
                    for nest in self.nests for nx, ny in [nest.position]
                )

                if overlaps_with_nest:
                    continue

                # Valid position found, break loop
                break
            else:
                # Skip spawning if no valid position is found
                print("Failed to find a valid position for food.")
                continue

            # Select HP for the food
            hp_range = FOOD_TYPES[food_type]
            hp = random.randint(hp_range[0], hp_range[1])

            # Add the new food item to the environment
            new_food = Food((x, y), food_type, hp)
            self.food_items.append(new_food)
            print(f"Spawned {food_type} at ({x}, {y}) with HP: {hp}")