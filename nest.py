import random

class Nest:
    def __init__(self, row_start, row_end, col_start, col_end, color):
        """Initialize the nest at a random position within a specific range with a specific color."""
        self.position = (
            random.randint(row_start, row_end - 1),
            random.randint(col_start, col_end - 1)
        )
        self.color = color  # Color of the nest
        self.total_food = 0  # Total food brought to the nest
        self.ants = []

    def add_food(self):
        """Increase the total food count."""
        self.total_food += 1