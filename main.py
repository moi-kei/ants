import asyncio
import pygame
from ant_agent import Ant_agent
from environment import Environment
from food import generate_random_food
from nest import Nest

# intialise simulation constants
# size in pixels
WIDTH, HEIGHT = 1840, 1000
# size of grid squares inpixels
GRID_SIZE = 30
# get number of grid squares based on the size of the sim using integer division
ROWS, COLS = HEIGHT // GRID_SIZE, WIDTH // GRID_SIZE

# colour codes dict for nests and ants
colours = {
    "black": (0, 0, 0),
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
}
# reverse the colours dictionary to so colour values can be mapped back to language for tooltips in visualisation
REVERSE_COLOURS = {v: k for k, v in colours.items()}

# initialise dictionaries for images
food_images = {}
ant_images = {}
nest_images = {}

def load_images():
    """
    this function loads the images for the simulation into the dictionaries
    loads the ants, nests, and food to be used later
    """
    global food_images, ant_images, nest_images
    # food items
    food_images = {
        "Leaf": pygame.image.load("images/leaf.png"),
        "Bug": pygame.image.load("images/bug.png"),
        "Berry": pygame.image.load("images/berry.png"),
        "Nut": pygame.image.load("images/nut.png"),
    }
    # ants
    ant_images = {
        (0, 0, 0): pygame.image.load("images/black_ant.png"),
        (255, 0, 0): pygame.image.load("images/red_ant.png"),
        (0, 255, 0): pygame.image.load("images/green_ant.png"),
        (0, 0, 255): pygame.image.load("images/blue_ant.png"),
    }
    # nests
    nest_images = {
        (0, 0, 0): pygame.image.load("images/black_ant_nest.png"),
        (255, 0, 0): pygame.image.load("images/red_ant_nest.png"),
        (0, 255, 0): pygame.image.load("images/green_ant_nest.png"),
        (0, 0, 255): pygame.image.load("images/blue_ant_nest.png"),
    }

def setup_simulation():
    """
    this function sets up the simulation environment
    initialises all the agents and components of the simulation

    Returns:
        _type_: _description_
    """
    food_items = generate_random_food(ROWS, COLS, num_food_items=20)  # 20 random food items

    # define quadrants for the nests
    # this splts the sim into 4 quarters so a nest can be placed into each so they are better sporead out
    # also moves the nest away from the edge a bit
    quadrants = {
        "top_left": (2, ROWS // 2, 2, COLS // 2),
        "top_right": (2, ROWS // 2, COLS // 2, COLS - 2),
        "bottom_left": (ROWS // 2, ROWS -2, 2, COLS // 2),
        "bottom_right": (ROWS // 2, ROWS - 2, COLS // 2, COLS - 2),
    }

    # initialise a nest in each of the quadrants into a list of nests
    nests = [
        Nest(*quadrants["top_left"], colours["red"]),
        Nest(*quadrants["top_right"], colours["black"]),
        Nest(*quadrants["bottom_left"], colours["green"]),
        Nest(*quadrants["bottom_right"], colours["blue"]),
    ]

    # initialise the environment with the correct size
    environment = Environment(ROWS, COLS, food_items, nests)

    # initialise the ants for each nest and add them to a list of ants
    ants = []

    # for each nest
    for nest in nests:
        # create 5 ants for each nest
        for _ in range(5):
            # create an ant
            ant = Ant_agent(nest.position, environment, nest, nest.colour)
            # add the ant to the list
            ants.append(ant)

    return environment, ants, nests

def render(screen, environment, ants, nests, paused, game_over, winner=None, hovered_nest=None, hovered_food=None, hovered_ant=None):
    """
    function for rendering the simulation using PyGame
    renders the simulation every frame
    also renders the tooltips for displaying information when the simulation is paused

    Args:
        SCREEN (pygame.Surface): the window the simulation is being displayed
        environment (Environment): the environment created for the simulation to be rendered
        ants (list): list of all ants in the simulation
        nests (list): list of all nests
        paused (bool): boolean representing if the simulation is paused
        game_over (bool): boolean whether the simulation has ended
        winner (str, optional): the colour of the winning ants. Defaults to None.
        hovered_nest (Nest, optional): the nest that the mouse is currently hovering over. Defaults to None.
        hovered_food (Food, optional): the food that the mouse is currently hovering over. Defaults to None.
        hovered_ant (Ant_agent, optional): the ant that the mouse is currently hovering over. Defaults to None.
    """
    # check if the simulation has reached the end (a colony has collected enough food)
    if game_over:
        # Iif the sim has ended, display a white screen with the winning message and images
        screen.fill((255, 255, 255))
        if winner:
            # show message displaying winning ant colour and instructions to restart or quit
            font = pygame.font.Font(None, 50)
            winner_surface = font.render(f"{winner} Ants Win!", True, (0, 0, 0))
            screen.blit(winner_surface, (WIDTH // 2 - winner_surface.get_width() // 2, HEIGHT // 2 - winner_surface.get_height() // 2))
            restart_surface = font.render("Press SPACE to Restart or ESC to Quit", True, (0, 0, 0))
            screen.blit(restart_surface, (WIDTH // 2 - restart_surface.get_width() // 2, HEIGHT // 2 - restart_surface.get_height() // 2 + 50))

            # show the winning nest
            nest_image = nest_images[tuple(colours[winner])]
            resized_nest_image = pygame.transform.scale(nest_image, (200, 200))
            screen.blit(resized_nest_image, (WIDTH // 2 - resized_nest_image.get_width() // 2, HEIGHT // 2 - resized_nest_image.get_height() // 2 - 150))

            # show the winning ant image
            ant_image = ant_images[tuple(colours[winner])]
            resized_ant_image = pygame.transform.scale(ant_image, (100, 100))
            screen.blit(resized_ant_image, (WIDTH // 2 - resized_ant_image.get_width() // 2, HEIGHT // 2 - resized_ant_image.get_height() // 2 + 150))
    else:
        # white background
        screen.fill((255, 255, 255))

        # layer for showing pheromones
        pheromone_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

        # render pheromones in see though version of ant colour
        # check valuse in all pheromone grids
        for colour, grid in environment.pheromone_grids.items():
            for x in range(environment.rows):
                for y in range(environment.cols):
                    intensity = grid[x][y]
                    # if there is a pheromone in the grid
                    if intensity > 0:
                        # get the colour
                        r, g, b = colour
                        # calculate the inalpha value based on the intensity of the pheromone (how recently it was placed)
                        alpha = max(20, min(100, intensity * 10)) 
                        # draw the pheromone using the colour and calculated intesnity
                        pygame.draw.rect(
                            pheromone_surface,
                            (r, g, b, alpha), 
                            (y * GRID_SIZE, x * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                        )

        # add the pheromone surface onto the main surface
        screen.blit(pheromone_surface, (0, 0))

        # draw food items
        for food in environment.food_items:
            # get position of food and image for food
            food_x, food_y = food.position
            food_image = food_images[food.food_type]

            # set size for each food
            if food.food_type == "Nut":
                size = (GRID_SIZE * 2, GRID_SIZE * 2) 
            elif food.food_type == "Berry":
                size = (GRID_SIZE * 2, GRID_SIZE * 3)
            elif food.food_type == "Leaf":
                size = (GRID_SIZE * 4, GRID_SIZE * 4)
            elif food.food_type == "Bug":
                size = (GRID_SIZE * 6, GRID_SIZE * 3)

            # resize the images
            resized_image = pygame.transform.scale(food_image, size)

            # calculate the position
            centre_x = food_y * GRID_SIZE - size[0] // 2 + GRID_SIZE
            centre_y = food_x * GRID_SIZE - size[1] // 2 + GRID_SIZE

            # render the food onto main surface
            screen.blit(resized_image, (centre_x, centre_y))

        # draw nests
        for nest in nests:
            # get position
            nest_x, nest_y = nest.position      
            # get the colour
            nest_colour_key = nest.colour
            # get the image for nest
            nest_image = nest_images[nest_colour_key]       
            # scale the image to 2x2 grid size
            size = (GRID_SIZE * 2, GRID_SIZE * 2)
            resized_nest_image = pygame.transform.scale(nest_image, size)
        
            # calculate position
            centre_x = nest_y * GRID_SIZE - size[0] // 2 + GRID_SIZE
            centre_y = nest_x * GRID_SIZE - size[1] // 2 + GRID_SIZE
        
            # render the nest image onto main surface
            screen.blit(resized_nest_image, (centre_x, centre_y))

        # draw ants
        for ant in ants:
            # get the needed values
            ant_x, ant_y = ant.position
            direction = ant.direction
            ant_image = ant_images[ant.colour]

            # scale image
            resized_ant_image = pygame.transform.scale(ant_image, (GRID_SIZE, GRID_SIZE))

            # rotate image (needs an extra 180 degrees)
            rotated_image = pygame.transform.rotate(resized_ant_image, (direction + 180))

            # get new dimensions of rotated image
            rotated_rect = rotated_image.get_rect()

            # calculate position and centre them to a grid square
            centre_x = ant_y * GRID_SIZE + GRID_SIZE // 2 - rotated_rect.width // 2
            centre_y = ant_x * GRID_SIZE + GRID_SIZE // 2 - rotated_rect.height // 2

            # render the ant onto main surface
            screen.blit(rotated_image, (centre_x, centre_y))

        # if paused display the paused message and hovered item info
        if paused:
            # font and size
            font = pygame.font.Font(None, 50)
            pause_surface = font.render("Press SPACE to Start/Stop", True, (0, 0, 0))
            screen.blit(pause_surface, (WIDTH // 2 - pause_surface.get_width() // 2, HEIGHT // 2 - pause_surface.get_height() // 2))

            # display nest info if hovering a nest
            if hovered_nest:
                render_popup(screen, f"{REVERSE_COLOURS.get(hovered_nest.colour, 'Unknown')} Ant Nest\nFood Collected: {hovered_nest.total_food}")

            # display food info if hovering food
            if hovered_food:
                render_popup(screen, f"Type: {hovered_food.food_type}\nHP: {hovered_food.hp}")

            # display ant info if hovering ant
            if hovered_ant:
                render_popup(screen, f"{REVERSE_COLOURS.get(hovered_ant.colour, 'Unknown')} Ant\n{hovered_ant.agent_goal}")

    # update the display
    pygame.display.flip()

def render_popup(screen, text):
    """
    function for rendering popups to display information about the simulation
    popus are shown is the simulation is paused and the mouse is hovering over something

    Args:
        screen (pygame.surface): the surface to render popus onto
        text (str): the text to be displayed on the popup
    """

    # font and size
    popup_font = pygame.font.Font(None, 30)
    # split text onto new lines
    lines = text.split("\n")
    # render lines
    surfaces = [popup_font.render(line, True, (0, 0, 0)) for line in lines]
    # calculate the height and width of the popup based on text size
    width = max(surface.get_width() for surface in surfaces) + 10
    height = sum(surface.get_height() for surface in surfaces) + 10

    # get the mouse position
    mouse_x, mouse_y = pygame.mouse.get_pos()
    # create rect for popup at mouse location
    popup_rect = pygame.Rect(mouse_x + 10, mouse_y + 10, width, height)

    # make sure the popup stays on the screen
    if popup_rect.right > WIDTH:
        popup_rect.right = WIDTH - 10
    if popup_rect.bottom > HEIGHT:
        popup_rect.bottom = HEIGHT - 10
    popup_rect.topleft = (popup_rect.right - width, popup_rect.bottom - height)

    # draw popup, white for background and black for border
    pygame.draw.rect(screen, (255, 255, 255), popup_rect)
    pygame.draw.rect(screen, (0, 0, 0), popup_rect, 2)

    # place the popup to the bottome left of the mouse pointer
    y_offset = popup_rect.top + 5
    # add the lines of text to the popup
    for surface in surfaces:
        screen.blit(surface, (popup_rect.left + 5, y_offset))
        y_offset += surface.get_height()

async def run_simulation(environment, ants, nests):
    """
    runs the simualation
    controls the main loop of the simulation
    and handles the events

    Args:
        environment (Environment): the environment for the simulation
        ants (list): list of all ants
        nests (list): list of all nests

    Returns:
        bool: whether the simulation is to continue running
    """
    # run the tasks for spawning food and phromone decay asynchronously
    asyncio.create_task(environment.decay_pheromones())
    asyncio.create_task(environment.spawn_food())

    # variables to control the flow of the simulation
    clock = pygame.time.Clock()
    running = True
    paused = True
    game_over = False
    winner = None

    # application loop
    while running:
        # reset any hovered items
        hovered_nest = None
        hovered_food = None
        hovered_ant = None

        # handle events
        for event in pygame.event.get():
            # is quits set running to false
            if event.type == pygame.QUIT:
                running = False
                break
            elif event.type == pygame.KEYDOWN:
                # if space is pressed
                if event.key == pygame.K_SPACE:
                    # restart simulation if the sim has ended
                    if game_over:
                        return True
                    # toggle pause if it hasnt yet
                    paused = not paused
                # exit application if escape is pressed
                elif event.key == pygame.K_ESCAPE:
                    running = False

        # puse sim if the sim ends to stop things continuing to run
        if game_over:
            paused = True

        # handle the showing of popups when paused
        if paused and not game_over:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            grid_x, grid_y = mouse_y // GRID_SIZE, mouse_x // GRID_SIZE

            # check for hovered nest
            for nest in nests:
                if nest.position == (grid_x, grid_y):
                    hovered_nest = nest
                    break

            # check for hovered food
            for food in environment.food_items:
                if food.position == (grid_x, grid_y):
                    hovered_food = food
                    break

            # check for hovered ant
            for ant in ants:
                if ant.position == (grid_x, grid_y):
                    hovered_ant = ant
                    break
        
        # allow the ants to act if the sim is not paused
        if not paused:
            tasks = [ant.act() for ant in ants]
            await asyncio.gather(*tasks)

        # check if win condition has been reached
        # win condition is collecting 50 food for now this can be changed to scale with number of ants or whatever
        for nest in nests:
            if nest.total_food >= 50:
                game_over = True
                winner = REVERSE_COLOURS.get(nest.colour, "Unknown")
                paused = True

        # render everything
        render(screen, environment, ants, nests, paused, game_over, winner, hovered_nest, hovered_food, hovered_ant)
        # frame rate
        clock.tick(60)

    pygame.quit()

def main():
    """
    main function for the ant simulation
    sets up pygame stuff, loads things, and starts the simulation
    """
    # initialise pygame
    pygame.init()

    # set up the display surface
    global screen
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("ants")

    # load images
    load_images()

    while True:
        # set up the simulation
        environment, ants, nests = setup_simulation()
        # run the simulation
        try:
            if not asyncio.run(run_simulation(environment, ants, nests)):
                break
        except KeyboardInterrupt:
            print("Simulation stopped.")
            break

if __name__ == "__main__":
    main()