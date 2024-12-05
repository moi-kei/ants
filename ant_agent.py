import asyncio
import random
import math
import time

class Ant:
    def __init__(self, position, environment, nest, color, sensing_range=2):
        self.position = position
        self.previous_position = position  # Track the previous position for direction
        self.direction = 0  # Default direction angle (upwards)
        self.carrying_food = False
        self.environment = environment
        self.nest = nest
        self.color = color  # Color of the ant (matching its nest)
        self.sensing_range = sensing_range  # The range in which the ant can sense food
        self.target_food = None  # To store the target food the ant is moving towards
        self.following_pheromone = False  # To track if the ant is following a pheromone trail
        self.visited_positions = []  # Track the last position to prevent oscillation
        self.ignore_pheromone_until = None  # Time until which the ant will ignore pheromone trails
        self.agent_goal = "exploring for food"
        self.sleep_until = 0

    def update_direction(self):
        """Update the direction angle based on the current and previous position."""
        dx = self.position[0] - self.previous_position[0]
        dy = self.position[1] - self.previous_position[1]
        if dx != 0 or dy != 0:
            # Calculate angle using atan2 and convert to degrees
            self.direction_angle = math.degrees(math.atan2(-dy, dx))  # Negative dy to align with screen coords
        self.previous_position = self.position

    async def decide_and_act(self):
        # Check if the ant is currently sleeping
        if self.sleep_until and time.time() < self.sleep_until:
            # Ant is still sleeping; skip this action cycle
            return
        if self.carrying_food:
            # Returning to the nest with food
            if self.position == self.nest.position:
                self.agent_goal = "depositing food"
                self.carrying_food = False
                self.nest.add_food()
                self.sleep_until = time.time() + 3
                print(f"Ant at {self.position} dropped food. Total food at {self.color} nest: {self.nest.total_food}")
            else:
                # Move towards the nest (lay pheromones if returning)
                self.agent_goal = "returning to nest with food"
                self.environment.drop_pheromone(self.position, self.color)
                self.move_towards(self.nest.position)
        else:
            food_at_position = self.check_for_food_in_range()
            if food_at_position:
                # Prioritize food even if ignoring pheromones
                if food_at_position.position[0] == self.position[0] and food_at_position.position[1] == self.position[1]:
                    self.agent_goal = "picking up food"
                    self.carrying_food = True
                    self.target_food = None
                    self.environment.remove_food_at(food_at_position.position)
                    self.sleep_until = time.time() + 3
                    print(f"Ant at {self.position} picked up {food_at_position.food_type} food.")
                else:
                    self.move_towards(food_at_position.position)
            elif self.following_pheromone:
                # Follow the pheromone trail
                self.agent_goal = "following pheromone trail"
                self.follow_pheromone_trail()
            elif self.ignore_pheromone_until and asyncio.get_event_loop().time() < self.ignore_pheromone_until:
                # Continue exploring if currently ignoring pheromone trails
                self.agent_goal = "exploring for food"
                self.random_move()
            else:
                # Search for food or pheromones
                if self.start_following_pheromone():
                    self.agent_goal = "detected pheromone trail"
                    self.following_pheromone = True
                else:
                    # Move randomly if no food or pheromone is found
                    self.agent_goal = "exploring for food"
                    self.random_move()

        self.update_direction()  # Update direction after action
        await asyncio.sleep(0.1)  # Simulate time taken for action

    def check_for_food_in_range(self):
        """Check if food exists within the sensing range."""
        for food in self.environment.food_items:
            # Check if the food is within the sensing range
            if abs(food.position[0] - self.position[0]) <= self.sensing_range and \
               abs(food.position[1] - self.position[1]) <= self.sensing_range:
                self.ignore_pheromone_until = 0
                return food
        return None

    def start_following_pheromone(self):
        """Start following the pheromone trail if one is found."""
        neighbors = self.environment.get_neighbors(self.position)
        for neighbor in neighbors:
            x, y = neighbor
            if self.environment.pheromone_grids[self.color][x][y] > 0:
                self.move_towards(neighbor)
                return True
        return False

    def follow_pheromone_trail(self):
        """Follow the pheromone trail in the direction away from the nest."""
        neighbors = self.environment.get_neighbors(self.position)
        nest_x, nest_y = self.nest.position
        target = None

        # Determine the direction away from the nest
        max_distance = 0
        for neighbor in neighbors:
            x, y = neighbor
            if neighbor == self.visited_positions[-1] if self.visited_positions else None:
                continue  # Avoid oscillating back to the last visited position
            if self.environment.pheromone_grids[self.color][x][y] > 0:
                # Calculate distance from the nest
                distance_from_nest = (x - nest_x)**2 + (y - nest_y)**2
                if distance_from_nest > max_distance:
                    max_distance = distance_from_nest
                    target = neighbor

        if target:
            # Add current position to visited positions
            self.visited_positions.append(self.position)
            if len(self.visited_positions) > 50:
                self.visited_positions.pop(0)

            self.move_towards(target)
            # Check for food at the new position
            food_at_position = self.check_for_food_in_range()
            if food_at_position:
                self.following_pheromone = False
        else:
            # If no trail is found or the trail ends without food
            self.following_pheromone = False
            self.ignore_pheromone_until = asyncio.get_event_loop().time() + 5  # Ignore pheromones for 5 seconds

    def move_towards(self, target):
        """Move towards the target position (either nest, food, or pheromone)."""
        dx = target[0] - self.position[0]
        dy = target[1] - self.position[1]
        if dx != 0 or dy != 0:
            self.direction = math.degrees(math.atan2(-dy, dx))  # Negative dy to align with screen coordinates

        new_x = self.position[0] + (1 if dx > 0 else -1 if dx < 0 else 0)
        new_y = self.position[1] + (1 if dy > 0 else -1 if dy < 0 else 0)
        if 0 <= new_x < self.environment.rows and 0 <= new_y < self.environment.cols:
            self.position = (new_x, new_y)

    def random_move(self):
        """Move randomly in the grid, prioritizing unvisited locations."""
        neighbors = self.environment.get_neighbors(self.position)
        unvisited_neighbors = [n for n in neighbors if n not in self.visited_positions]

        if unvisited_neighbors:
            target = random.choice(unvisited_neighbors)  # Choose a random unvisited location
        else:
            target = random.choice(neighbors)  # Fall back to any neighbor if all are visited

        # Calculate direction before moving
        dx = target[0] - self.position[0]
        dy = target[1] - self.position[1]
        if dx != 0 or dy != 0:
            self.direction = math.degrees(math.atan2(-dy, dx))  # Negative dy to align with screen coordinates

        # Add current position to visited locations
        self.visited_positions.append(self.position)
        if len(self.visited_positions) > 50:
            self.visited_positions.pop(0)  # Limit visited positions to the last 50

        # Move to the selected target
        self.position = target