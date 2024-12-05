import random

class Food:
    """
    class representing an item of food in the simulation
    """

    def __init__(self, position, food_type, hp):
        """
        initialises an item of food at a poistions in the sim
        each food item has a type and a HP total

        Args:
            position (tuple): coordinate position of the food
            food_type (str): the type of food
            hp (int): the total HP of the food
        """

        # set the values
        self.position = position
        self.food_type = food_type
        self.hp = hp

    def reduce_hp(self):
        """
        function for reducing the food items HP
        reduces the hp of the food item by 1
        returns a boolean which tells the sim if the food item has to be removed or not

        Returns:
            bool: retuirs true if the HP is <= 0 else returns flase
        """

        self.hp -= 1
        return self.hp <= 0

# list of food types
FOOD_TYPES = {
    "Berry": (5, 10), 
    "Leaf": (10, 15),  
    "Nut": (2, 5),
    "Bug": (15, 20) 
}

def generate_random_food(rows, cols, num_food_items):
    """
    generates a list of food types
    a list of a given number of food types is randomly generated and returned

    Args:
        rows (int): the number of rows in the simulation
        cols (_type_): the number of columns in the simulation
        num_food_items (int): the number of food items to generate

    Returns:
        list: the list of generated food items
    """
    
    # initialise list for returning
    food_list = []
    
    # define the food types to use in the sim and the probabilities odf them being generated
    food_types = ["Berry", "Nut", "Leaf", "Bug"]
    # higher weights for berry and nuts and lower for leaves and bugs
    weights = [5, 5, 3, 2] 

    # generate the specified number of items
    for _ in range(num_food_items):
        # random position
        position = (random.randint(0, rows - 1), random.randint(0, cols - 1))
        # choose 1 item of food based on value of weights
        food_type = random.choices(food_types, weights=weights, k=1)[0]
        # random hp value between the specified range
        hp_range = FOOD_TYPES[food_type]
        hp = random.randint(hp_range[0], hp_range[1])
        # initialise and add to list
        food_list.append(Food(position, food_type, hp))
    
    return food_list
