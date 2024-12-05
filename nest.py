import random

class Nest:
    """
    class representing a nest in the ant simulation
    """

    def __init__(self, row_start, row_end, col_start, col_end, colour):
        """
        initialises the nest in a given quadrant of the simulation
        to make the visualisation better the sim puts each nest in a random place in each quarter of the screen

        Args:
            row_start (int): the starting row of the quadrant
            row_end (int): the end row of the quadrant
            col_start (int): the starting column of the quadrant
            col_end (int): the end column of the quadrant
            colour (tuple): colour code of the nest
        """

        # randomise a position for the nest in the quadrant
        self.position = (
            random.randint(row_start, row_end - 1),
            random.randint(col_start, col_end - 1)
        )
        # set colour
        self.colour = colour
        # start food total at 0
        self.total_food = 0

    def add_food(self):
        """
        function for adding food to the nest
        """
        
        # increase total food by 1
        self.total_food += 1