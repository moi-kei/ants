import asyncio
import random
from food import Food, generate_random_food, FOOD_TYPES

class Environment:
    """
    class representing the environment that the simulation uses
    """

    def __init__(self, rows: int, cols: int, food_items: list, nests: list):
        """
        initialises the environment

        args:
            rows (int): the number of rows in the simulation
            cols (int): the number of columns in the simulation
            food_items (list): the list of food items to be placed in the environment
            nests (list): the list of ant nests that are to be placed in the environment
        """

        # set values and lists
        self.rows = rows
        self.cols = cols
        self.food_items = food_items
        self.nests = nests
        # initialises a pheromone grid for each colour of nest contained in a dict using the colour of the nest as a key
        # pheromone grids is the same size as the sim grid
        self.pheromone_grids = {nest.colour: [[0 for _ in range(cols)] for _ in range(rows)] for nest in nests}

    def drop_pheromone(self, position, colour):
        """
        functions that drops pheromones onto a location in the simulation
        uses the position of the ant that is dropping it and the colout of the ant

        args:
            position (tuple): coordinates that the pheromone will be paced
            colour (tuple): colour code of the pheromone
        """

        # set pos
        x, y = position
        # set the pheromone level to 10 in the correct pos and colour
        self.pheromone_grids[colour][x][y] = 10

    def remove_food(self, position):
        """
        function that removes food item from the environment if it has no hp left

        args:
            position (tuple): coordinates of the food item
        """

        # find food item with correct position
        for food in self.food_items:
            if food.position == position:
                # if the item has no hp left remove it from the list of food items and environment
                if food.reduce_hp():
                    self.food_items.remove(food)
                break

    def get_neighbors(self, position):
        """
        get the surrounding grid positions from a position

        args:
            position (tuple): the coordinates of the position that you want to get the surrounding squares

        returns:
            list: the list of neighbouring locations
        """

        # get neighbouring squares based on position
        x, y = position
        neighbors = [
            ((x - 1), y),    
            ((x + 1), y),    
            (x, (y - 1)),    
            (x, (y + 1)),    
            ((x - 1), y - 1),
            ((x - 1), y + 1),
            ((x + 1), y - 1),
            ((x + 1), y + 1),
        ]
        # only return positions that are within the bounds of the simulation
        return [(nx, ny) for nx, ny in neighbors if 0 <= nx < self.rows and 0 <= ny < self.cols]

    async def decay_pheromones(self):
        """
        function that simulates the decay of pheromones in the environment
        reduces the intensity of the pheromone over time
        """

        while True:
            # reduce all pheromones on the map by an amount
            for colour, grid in self.pheromone_grids.items():
                for x in range(self.rows):
                    for y in range(self.cols):
                        if grid[x][y] > 0:
                            grid[x][y] -= 0.1
            # reduce pheromone every 0.1 seconds 
            # this means pheromone lasts 10 seconds total (10 - 0.1, every 0.1 seconds)
            await asyncio.sleep(0.1)

    async def spawn_food(self):
        """
        spawns a food item on the environment at set intervals
        simulates food dropping on the ground for the ants to pick up
        """

        # set the max an min intervals for food spawing
        # these can be changed depending of screen size and number of ants
        min_interval = 5
        max_interval = 10

        while True:
            # sleep for a random amount of time between the intervals set
            await asyncio.sleep(random.randint(min_interval, max_interval)) 

            # generate a random food item
            food_item = generate_random_food(self.rows, self.cols, 1)
            new_food = food_item[0] 

            # add the food item to the environment
            self.food_items.append(new_food)
            print(f"Spawned {new_food.food_type} at ({new_food.position[0]}, {new_food.position[1]}) with HP: {new_food.hp}")
