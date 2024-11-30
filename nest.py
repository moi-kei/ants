import random

class Nest:
    def __init__(self, rows, cols):
        """Initialize the nest at a random position."""
        self.position = (random.randint(0, rows - 1), random.randint(0, cols - 1))
        self.total_food = 0  # Total food brought to the nest

    def add_food(self):
        """Increase the total food count."""
        self.total_food += 1
