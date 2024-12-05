import asyncio
import random
import math
import time

class Ant_agent:
    """
    class representing an ant within the simulation
    each ant agent is responsibble for thier own decision making and interacctions
    """

    def __init__(self, position, environment, nest, colour):
        """
        intialises the ant agent
        assigning it to the environment and a nest, colour, and position

        Args:
            position (tuple): the strating coordinates of the ant (just now they all start at the nest)
            environment (Environment): the environment that the ant is to act within
            nest (Nest): the nest the ant is assigned to
            colour (tuple): the coour code of the ant
        """

        # initialise properties of the ant
        self.position = position
        self.direction = 0 
        self.carrying_food = False
        self.environment = environment
        self.nest = nest
        self.colour = colour 
        self.sensing_range = 2
        self.following_pheromone = False 
        self.visited_positions = []
        self.ignore_pheromone_until = None
        self.agent_goal = "exploring for food"
        self.sleep_until = 0

    async def act(self):
        """
        function tha contains the decision making logic for the ant agents
        the priorites of the ant agents are basically how they are organised in this function
        roughly summarised as:
        return food to nest > move towards sensed food > look for food > follow pheromones > look for pheromones > explore the environment
        """
        # check if the ant is currently sleeping (picking up or dropping off food)
        if self.sleep_until and time.time() < self.sleep_until:
            # is its still sleeping skip
            return
        
        # check if the ant is currently carrying food
        if self.carrying_food:
            
            # if the ant is at the nest location
            if self.position == self.nest.position:
                # deposit food to the nest
                self.agent_goal = "depositing food"
                self.carrying_food = False
                self.nest.add_food()
                self.sleep_until = time.time() + 3
                print(f"Ant at {self.position} dropped food. Total food at {self.colour} nest: {self.nest.total_food}")
            
            # if its not at the nest
            else:
                # move towards the nst and lay pheromones
                self.agent_goal = "returning to nest with food"
                self.environment.drop_pheromone(self.position, self.colour)
                self.move_towards(self.nest.position)
        
        # if it isnt carrying food
        else:
           
            # check for food in surrounding area
            food_at_position = self.sense_food()
            
            # if food is found in range
            if food_at_position:
               
                # if the ant is at the position of the food
                if food_at_position.position[0] == self.position[0] and food_at_position.position[1] == self.position[1]:
                    # pick up some food
                    self.agent_goal = "picking up food"
                    self.carrying_food = True
                    self.environment.remove_food(food_at_position.position)
                    self.sleep_until = time.time() + 3
                    print(f"Ant at {self.position} picked up {food_at_position.food_type} food.")
                
                # if its not move towards the food
                else:
                    self.move_towards(food_at_position.position)
            
            # if the ant is following a pheromone trail
            elif self.following_pheromone:
                # follow the pheromone trail
                self.agent_goal = "following pheromone trail"
                self.follow_pheromone()
            
            # if the ant is ignoring a pheromone trail then explore
            # this is here to stop the ants getting stuck following a pheromone trail that leads to food that isnt there anymore
            # the agents will still pick up food if found but wont follow the pheromones
            elif self.ignore_pheromone_until and asyncio.get_event_loop().time() < self.ignore_pheromone_until:
                # explore
                self.agent_goal = "exploring for food"
                self.move()
            
            else:
                # look for any phromone trails, if found follow them
                if self.start_following_pheromone():
                    self.agent_goal = "detected pheromone trail"
                    self.following_pheromone = True
                else:
                    # explore if no pheromones are found
                    self.agent_goal = "exploring for food"
                    self.move()

        # give time for the agents to decide and act
        await asyncio.sleep(0.1) 

    def sense_food(self):
        """
        function that checks if there is any food within the sensing range of the ant

        Returns:
            Food: the food that is found or None if none found
        """
        for food in self.environment.food_items:
            # check if the food is within the sensing range using abs so its always positive
            if abs(food.position[0] - self.position[0]) <= self.sensing_range and \
               abs(food.position[1] - self.position[1]) <= self.sensing_range:
                self.ignore_pheromone_until = 0
                return food
        return None

    def start_following_pheromone(self):
        """
        function that checks if there is a pheromone trail within sensing range

        Returns:
            bool: boolean representing if a trial if found
        """
        # check for pheromones on x axis
        for x in range(self.position[0] - self.sensing_range, self.position[0] + self.sensing_range + 1):
            # check for phromones i y axis
            for y in range(self.position[1] - self.sensing_range, self.position[1] + self.sensing_range + 1):
                # check that thje grid square is within bounds
                if 0 <= x < self.environment.rows and 0 <= y < self.environment.cols:
                    # if a trail is found
                    if self.environment.pheromone_grids[self.colour][x][y] > 0:
                        # move towwards it
                        self.move_towards((x, y))
                        return True
        return False

    def follow_pheromone(self):
        """
        function that directs the ant agents to follow the pheromone trail in the direction away from the nest
        the ants will follow in the direction away from the nest only
        this is to stop the ants going backwards and forwards along pheromone trails
        """

        # get surrounding squares of current position
        neighbors = self.environment.get_neighbors(self.position)
        nest_x, nest_y = self.nest.position
        trail = None

        
        max_distance = 0
        # check surrounding squares for the pheromone trail
        for neighbor in neighbors:
            x, y = neighbor
            # stop the ant from returning to the square it was just one
            # mainly used when it reaches the end of a trail and finds no food to stop the ants oscilating
            if neighbor == self.visited_positions[-1] if self.visited_positions else None:
                continue  # Avoid oscillating back to the last visited position
            if self.environment.pheromone_grids[self.colour][x][y] > 0:
                # calculate distance from the nest using pythagoras
                distance_from_nest = (x - nest_x)**2 + (y - nest_y)**2
                # if a trail is found that is further away than the nest assign it
                if distance_from_nest > max_distance:
                    max_distance = distance_from_nest
                    trail = neighbor

        # if there was a trail found
        if trail:
            # add current position to visited positions
            self.visited_positions.append(self.position)
            # limit the ants memory to 50 last locatioins
            if len(self.visited_positions) > 50:
                self.visited_positions.pop(0)

            # move towards the trail
            self.move_towards(trail)
            # check for food at the new position
            food_at_position = self.sense_food()
            # if food is found set the following property to false
            if food_at_position:
                self.following_pheromone = False
        else:
            # ff no trail is found or the trail ends without food stop following
            self.following_pheromone = False
            # and ignore the trails for 5 seconds
            # this gives time for the trail to decay so the ant isnt caught in a loop
            # stops them going: follow trail > explore > detect trail > follow trail > explore on and on
            self.ignore_pheromone_until = asyncio.get_event_loop().time() + 5 

    def move_towards(self, target):
        """
        move towards a specific grid square

        Args:
            target (tuple): coordinate of the sqaure that is being moved to
        """

        # calculate the new direction of the ant
        dx = target[0] - self.position[0]
        dy = target[1] - self.position[1]      
        if dx != 0 or dy != 0:
            self.direction = math.degrees(math.atan2(dy, dx)) 

        # iteratively move towards the target location
        # move towards the correct x axis
        new_x = self.position[0] + (1 if dx > 0 else -1 if dx < 0 else 0)
        # move towards the correct y axis
        new_y = self.position[1] + (1 if dy > 0 else -1 if dy < 0 else 0)
        # check if the square is within bounds
        if 0 <= new_x < self.environment.rows and 0 <= new_y < self.environment.cols:
            # set position to the new position
            self.position = (new_x, new_y)

    def move(self):
        """
        function that allows the ant to move to a neighbouring square
        this function tries to move to a square that the ant has not visited in hte last 50 cycles
        if not then it just picks a random one
        """

        # get the neighbouring squares and check if there is an unvisited one
        neighbors = self.environment.get_neighbors(self.position)
        unvisited_neighbors = [n for n in neighbors if n not in self.visited_positions]

        # if there are unvisited squares choose a random one
        if unvisited_neighbors:
            target = random.choice(unvisited_neighbors) 
        # if there isnt choose a ranxdom neighbouring square
        else:
            target = random.choice(neighbors)

        # calculate direction before moving
        dx = target[0] - self.position[0]
        dy = target[1] - self.position[1]
        if dx != 0 or dy != 0:
            self.direction = math.degrees(math.atan2(dy, dx))

        # add current position to visited locations
        self.visited_positions.append(self.position)
        if len(self.visited_positions) > 50:
            self.visited_positions.pop(0)

        # move to the selected target
        self.position = target