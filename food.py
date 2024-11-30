import random

# Define different food types with associated hp values
class Food:
    def __init__(self, position, food_type, hp):
        self.position = position
        self.food_type = food_type
        self.hp = hp

    def reduce_hp(self):
        """Reduce the food's hp by 1. Returns True if the food is depleted."""
        self.hp -= 1
        return self.hp <= 0

# Food types with their associated HP ranges
FOOD_TYPES = {
    "Berry": (5, 10),  # Berry food type with HP range between 3 and 7
    "Leaf": (10, 15),  # Leaf food type with HP range between 5 and 10
    "Seed": (2, 5),   # Seed food type with HP range between 2 and 5
    "Insect": (15, 20)  # Insect food type with HP range between 4 and 8
}

def generate_random_food(rows, cols, num_food_items):
    """Generate a list of random food objects."""
    food_list = []
    for _ in range(num_food_items):
        position = (random.randint(0, rows - 1), random.randint(0, cols - 1))
        food_type = random.choice(list(FOOD_TYPES.keys()))
        hp_range = FOOD_TYPES[food_type]
        hp = random.randint(hp_range[0], hp_range[1])  # Randomize food "hp" within the type's range
        food_list.append(Food(position, food_type, hp))
    return food_list
