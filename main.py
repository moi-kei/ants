import asyncio
import pygame
from ant_agent import Ant
from environment import Environment
from food import generate_random_food
from nest import Nest

# Initialize constants
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 20
ROWS, COLS = HEIGHT // GRID_SIZE, WIDTH // GRID_SIZE

colours = {
    "black": (0, 0, 0),
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
}
# Reverse the `colours` dictionary
REVERSE_COLOURS = {v: k for k, v in colours.items()}


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


def render(SCREEN, environment, ants, nests, paused, hovered_nest=None, hovered_food=None, hovered_ant=None):
    # Clear the screen
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
        food_color = (0, 128, 0)  # Dark green for food
        pygame.draw.rect(
            SCREEN,
            food_color,
            (food_y * GRID_SIZE, food_x * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        )

    # Draw nests
    for nest in nests:
        nest_x, nest_y = nest.position
        pygame.draw.rect(
            SCREEN,
            nest.color,
            (nest_y * GRID_SIZE, nest_x * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        )

    # Draw ants
    for idx, ant in enumerate(ants):
        ant_x, ant_y = ant.position
        pygame.draw.circle(
            SCREEN,
            ant.color,
            (ant_y * GRID_SIZE + GRID_SIZE // 2, ant_x * GRID_SIZE + GRID_SIZE // 2),
            GRID_SIZE // 3
        )

    # If paused, display the paused message and hovered item info
    if paused:
        font = pygame.font.Font(None, 50)
        pause_surface = font.render("Press SPACE to Start/Stop", True, (0, 0, 0))
        SCREEN.blit(pause_surface, (WIDTH // 2 - pause_surface.get_width() // 2, HEIGHT // 2 - pause_surface.get_height() // 2))

        def draw_popup(text, mouse_x, mouse_y):
            popup_font = pygame.font.Font(None, 30)
            popup_surfaces = [popup_font.render(line, True, (0, 0, 0)) for line in text.split("\n")]
            popup_width = max(surface.get_width() for surface in popup_surfaces) + 10
            popup_height = sum(surface.get_height() for surface in popup_surfaces) + 10
            popup_rect = pygame.Rect(mouse_x + 10, mouse_y + 10, popup_width, popup_height)

            # Ensure the popup fits within the screen bounds
            if popup_rect.right > WIDTH:
                popup_rect.right = WIDTH - 10
                popup_rect.topleft = (popup_rect.right - popup_width, popup_rect.top)
            if popup_rect.bottom > HEIGHT:
                popup_rect.bottom = HEIGHT - 10
                popup_rect.topleft = (popup_rect.left, popup_rect.bottom - popup_height)

            # Draw background and border
            pygame.draw.rect(SCREEN, (255, 255, 255), popup_rect, border_radius=10)
            pygame.draw.rect(SCREEN, (0, 0, 0), popup_rect, width=2, border_radius=10)

            # Blit each line of the popup text
            y_offset = popup_rect.top + 5
            for surface in popup_surfaces:
                SCREEN.blit(surface, (popup_rect.left + 5, y_offset))
                y_offset += surface.get_height()

        if hovered_nest:
            draw_popup(f"Food Stored: {hovered_nest.total_food}", *pygame.mouse.get_pos())

        if hovered_food:
            draw_popup(f"Type: {hovered_food.food_type}\nHP: {hovered_food.hp}", *pygame.mouse.get_pos())

        if hovered_ant:
            color_name = REVERSE_COLOURS.get(hovered_ant.color, "Unknown")
            ant_index = hovered_ant.nest.ants.index(hovered_ant) + 1
            draw_popup(f"{color_name} Ant {ant_index}\n{hovered_ant.agent_goal}", *pygame.mouse.get_pos())

    pygame.display.flip()


async def run_simulation(environment, ants, nests):
    asyncio.create_task(environment.decay_pheromones())  # Start pheromone decay
    asyncio.create_task(environment.spawn_random_food(spawn_interval=15))  # Spawn random food every 5-15 seconds

    clock = pygame.time.Clock()
    running = True
    paused = True  # Start paused

    while running:
        hovered_nest = None
        hovered_food = None
        hovered_ant = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                paused = not paused  # Toggle pause

        if paused:
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

        render(SCREEN, environment, ants, nests, paused, hovered_nest, hovered_food, hovered_ant)
        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    pygame.init()
    SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Virtual Ant Farm")

    environment, ants, nests = setup_simulation()

    try:
        asyncio.run(run_simulation(environment, ants, nests))
    except KeyboardInterrupt:
        print("Simulation stopped.")
