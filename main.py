import asyncio
import pygame
from ant_agent import Ant
from environment import Environment
from food import generate_random_food
from nest import Nest

# Initialize constants
WIDTH, HEIGHT = 1840, 1000
GRID_SIZE = 30
ROWS, COLS = HEIGHT // GRID_SIZE, WIDTH // GRID_SIZE

# Colors for nests and ants
colours = {
    "black": (0, 0, 0),
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
}
# Reverse the colors dictionary
REVERSE_COLOURS = {v: k for k, v in colours.items()}

# Load images later to avoid pygame.display initialization error
food_images = {}
ant_images = {}
nest_images = {}

def load_images():
    """Load all images after pygame is initialized."""
    global food_images, ant_images, nest_images
    food_images = {
        "Leaf": pygame.image.load("images/leaf.png").convert_alpha(),
        "Bug": pygame.image.load("images/bug.png").convert_alpha(),
        "Berry": pygame.image.load("images/berry.png").convert_alpha(),
        "Nut": pygame.image.load("images/nut.png").convert_alpha(),
    }
    ant_images = {
        (0, 0, 0): pygame.image.load("images/black_ant.png").convert_alpha(),
        (255, 0, 0): pygame.image.load("images/red_ant.png").convert_alpha(),
        (0, 255, 0): pygame.image.load("images/green_ant.png").convert_alpha(),
        (0, 0, 255): pygame.image.load("images/blue_ant.png").convert_alpha(),
    }
    # Load nest images
    nest_images = {
        (0, 0, 0): pygame.image.load("images/black_ant_nest.png").convert_alpha(),
        (255, 0, 0): pygame.image.load("images/red_ant_nest.png").convert_alpha(),
        (0, 255, 0): pygame.image.load("images/green_ant_nest.png").convert_alpha(),
        (0, 0, 255): pygame.image.load("images/blue_ant_nest.png").convert_alpha(),
    }

def setup_simulation():
    food_items = generate_random_food(ROWS, COLS, num_food_items=20)  # 20 random food items

    # Define quadrants for the nests
    quadrants = {
        "top_left": (0, ROWS // 2, 0, COLS // 2),
        "top_right": (0, ROWS // 2, COLS // 2, COLS),
        "bottom_left": (ROWS // 2, ROWS, 0, COLS // 2),
        "bottom_right": (ROWS // 2, ROWS, COLS // 2, COLS),
    }

    # Create nests with their colors and positions in designated quadrants
    nests = [
        Nest(*quadrants["top_left"], colours["red"]),       # Red nest in top-left quadrant
        Nest(*quadrants["top_right"], colours["black"]),   # Black nest in top-right quadrant
        Nest(*quadrants["bottom_left"], colours["green"]), # Green nest in bottom-left quadrant
        Nest(*quadrants["bottom_right"], colours["blue"]), # Blue nest in bottom-right quadrant
    ]

    # Create environment
    environment = Environment(ROWS, COLS, food_items, nests)

    # Create ants and assign them to respective nests
    ants = []
    for nest in nests:
        nest_ants = [Ant(nest.position, environment, nest, nest.color) for _ in range(5)]  # 5 ants per nest
        nest.ants.extend(nest_ants)  # Add these ants to the nest's list
        ants.extend(nest_ants)  # Add these ants to the overall list

    return environment, ants, nests

def render(SCREEN, environment, ants, nests, paused, game_over, winner=None, hovered_nest=None, hovered_food=None, hovered_ant=None):
    # Clear the screen
    if game_over:
        # If game is over, display a white screen with the winning message and images
        SCREEN.fill((255, 255, 255))
        if winner:
            font = pygame.font.Font(None, 50)
            winner_surface = font.render(f"{winner} Ants Win!", True, (0, 0, 0))
            SCREEN.blit(winner_surface, (WIDTH // 2 - winner_surface.get_width() // 2, HEIGHT // 2 - winner_surface.get_height() // 2))
            restart_surface = font.render("Press SPACE to Restart or ESC to Quit", True, (0, 0, 0))
            SCREEN.blit(restart_surface, (WIDTH // 2 - restart_surface.get_width() // 2, HEIGHT // 2 - restart_surface.get_height() // 2 + 50))

            # Display the winning color nest image above the text
            nest_image = nest_images[tuple(colours[winner])]
            resized_nest_image = pygame.transform.scale(nest_image, (200, 200))
            SCREEN.blit(resized_nest_image, (WIDTH // 2 - resized_nest_image.get_width() // 2, HEIGHT // 2 - resized_nest_image.get_height() // 2 - 150))

            # Display the winning color ant image below the text
            ant_image = ant_images[tuple(colours[winner])]
            resized_ant_image = pygame.transform.scale(ant_image, (100, 100))
            SCREEN.blit(resized_ant_image, (WIDTH // 2 - resized_ant_image.get_width() // 2, HEIGHT // 2 - resized_ant_image.get_height() // 2 + 150))
    else:
        SCREEN.fill((255, 255, 255))

        # Create a separate layer for pheromones
        pheromone_surface = pygame.Surface(SCREEN.get_size(), pygame.SRCALPHA)

        # Draw pheromones
        for color, grid in environment.pheromone_grids.items():
            for x in range(environment.rows):
                for y in range(environment.cols):
                    intensity = grid[x][y]
                    if intensity > 0:
                        r, g, b = color
                        alpha = max(20, min(100, intensity * 10))  # Transparency level
                        pygame.draw.rect(
                            pheromone_surface,
                            (r, g, b, alpha),  # RGBA with alpha for transparency
                            (y * GRID_SIZE, x * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                        )

        # Blit the pheromone surface onto the main screen
        SCREEN.blit(pheromone_surface, (0, 0))

        # Draw food
        for food in environment.food_items:
            food_x, food_y = food.position
            food_image = food_images[food.food_type]

            # Set size for each food type
            if food.food_type == "Nut":
                size = (GRID_SIZE * 2, GRID_SIZE * 2)  # 2x2 size
            elif food.food_type == "Berry":
                size = (GRID_SIZE * 2, GRID_SIZE * 3)  # 4x4 size
            elif food.food_type == "Leaf":
                size = (GRID_SIZE * 4, GRID_SIZE * 4)  # 4x4 size
            elif food.food_type == "Bug":
                size = (GRID_SIZE * 6, GRID_SIZE * 3)  # 3x6 size
            else:
                size = (GRID_SIZE, GRID_SIZE)  # Default size (if needed)

            # Resize the image
            resized_image = pygame.transform.scale(food_image, size)

            # Render the food
            SCREEN.blit(
                resized_image,
                (
                    food_y * GRID_SIZE - size[0] // 2 + GRID_SIZE // 2,  # Adjust x to center
                    food_x * GRID_SIZE - size[1] // 2 + GRID_SIZE // 2,  # Adjust y to center
                ),
            )

        for nest in nests:
            nest_x, nest_y = nest.position
        
            # Normalize the color tuple
            nest_color_key = tuple(map(int, nest.color))
        
            # Access the corresponding image
            if nest_color_key not in nest_images:
                raise ValueError(f"Nest image not found for color {nest_color_key}. Available keys: {list(nest_images.keys())}")
            
            nest_image = nest_images[nest_color_key]
        
            # Scale the image to 2x2 grid size
            size = (GRID_SIZE * 2, GRID_SIZE * 2)
            resized_nest_image = pygame.transform.scale(nest_image, size)
        
            # Calculate position to center the image over the 2x2 grid
            center_x = nest_y * GRID_SIZE - size[0] // 2 + GRID_SIZE
            center_y = nest_x * GRID_SIZE - size[1] // 2 + GRID_SIZE
        
            # Render the nest image
            SCREEN.blit(resized_nest_image, (center_x, center_y))

        for ant in ants:
            ant_x, ant_y = ant.position
            direction = ant.direction  # Get the direction in degrees
            ant_image = ant_images[ant.color]

            # Scale the ant image to 1x1 grid size
            resized_ant_image = pygame.transform.scale(ant_image, (GRID_SIZE, GRID_SIZE))

            # Rotate the image based on direction
            rotated_image = pygame.transform.rotate(resized_ant_image, -(direction + 180))

            # Get the dimensions of the rotated image
            rotated_rect = rotated_image.get_rect()

            # Calculate position to center the image in the grid cell
            center_x = ant_y * GRID_SIZE + GRID_SIZE // 2 - rotated_rect.width // 2
            center_y = ant_x * GRID_SIZE + GRID_SIZE // 2 - rotated_rect.height // 2

            # Render the ant at the centered position
            SCREEN.blit(rotated_image, (center_x, center_y))

        # If paused, display the paused message and hovered item info
        if paused:
            font = pygame.font.Font(None, 50)
            pause_surface = font.render("Press SPACE to Start/Stop", True, (0, 0, 0))
            SCREEN.blit(pause_surface, (WIDTH // 2 - pause_surface.get_width() // 2, HEIGHT // 2 - pause_surface.get_height() // 2))

            # Display nest info if hovering over a nest
            if hovered_nest:
                render_popup(SCREEN, f"{REVERSE_COLOURS.get(hovered_nest.color, 'Unknown')} Ant Nest\nFood Collected: {hovered_nest.total_food}")

            # Display food info if hovering over food
            if hovered_food:
                render_popup(SCREEN, f"Type: {hovered_food.food_type}, HP: {hovered_food.hp}")

            # Display ant info if hovering over an ant
            if hovered_ant:
                render_popup(SCREEN, f"{REVERSE_COLOURS.get(hovered_ant.color, 'Unknown')} Ant\n{hovered_ant.agent_goal}")

    # Update the display
    pygame.display.flip()

def render_popup(screen, text):
    """Render a popup with text at the mouse position."""
    popup_font = pygame.font.Font(None, 30)
    lines = text.split("\n")
    surfaces = [popup_font.render(line, True, (0, 0, 0)) for line in lines]
    width = max(surface.get_width() for surface in surfaces) + 10
    height = sum(surface.get_height() for surface in surfaces) + 10

    mouse_x, mouse_y = pygame.mouse.get_pos()
    popup_rect = pygame.Rect(mouse_x + 10, mouse_y + 10, width, height)

    if popup_rect.right > WIDTH:
        popup_rect.right = WIDTH - 10
    if popup_rect.bottom > HEIGHT:
        popup_rect.bottom = HEIGHT - 10
    popup_rect.topleft = (popup_rect.right - width, popup_rect.bottom - height)

    pygame.draw.rect(screen, (255, 255, 255), popup_rect)
    pygame.draw.rect(screen, (0, 0, 0), popup_rect, 2)

    y_offset = popup_rect.top + 5
    for surface in surfaces:
        screen.blit(surface, (popup_rect.left + 5, y_offset))
        y_offset += surface.get_height()

async def run_simulation(environment, ants, nests):
    asyncio.create_task(environment.decay_pheromones())  # Start pheromone decay
    asyncio.create_task(environment.spawn_random_food(spawn_interval=15))  # Spawn random food every 5-15 seconds

    clock = pygame.time.Clock()
    running = True
    paused = True  # Start paused
    game_over = False
    winner = None

    while running:
        hovered_nest = None
        hovered_food = None
        hovered_ant = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game_over:
                        # Restart the simulation
                        return True
                    paused = not paused  # Toggle pause if not game over
                elif event.key == pygame.K_ESCAPE:
                    running = False

        if game_over:
            paused = True  # Pause the game if it's over

        if paused and not game_over:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            grid_x, grid_y = mouse_y // GRID_SIZE, mouse_x // GRID_SIZE

            # Check for hovered nest
            for nest in nests:
                if nest.position == (grid_x, grid_y):
                    hovered_nest = nest
                    break

            # Check for hovered food
            for food in environment.food_items:
                if food.position == (grid_x, grid_y):
                    hovered_food = food
                    break

            # Check for hovered ant
            for ant in ants:
                if ant.position == (grid_x, grid_y):
                    hovered_ant = ant
                    break

        if not paused:
            tasks = [ant.decide_and_act() for ant in ants]
            await asyncio.gather(*tasks)

        for nest in nests:
            if nest.total_food >= 50:
                game_over = True
                winner = REVERSE_COLOURS.get(nest.color, "Unknown")
                paused = True

        render(SCREEN, environment, ants, nests, paused, game_over, winner, hovered_nest, hovered_food, hovered_ant)
        clock.tick(30)

    pygame.quit()
    return False

def main():
    pygame.init()
    global SCREEN
    SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ant Simulation")

    load_images()

    while True:
        environment, ants, nests = setup_simulation()
        try:
            if not asyncio.run(run_simulation(environment, ants, nests)):
                break
        except KeyboardInterrupt:
            print("Simulation stopped.")
            break

if __name__ == "__main__":
    main()