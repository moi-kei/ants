import asyncio
import pygame
from ant_agent import Ant
from environment import Environment
from food import generate_random_food

# Initialize constants
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 20
ROWS, COLS = HEIGHT // GRID_SIZE, WIDTH // GRID_SIZE

def setup_simulation():
    food_items = generate_random_food(ROWS, COLS, num_food_items=10)  # 10 random food items

    # Create environment
    environment = Environment(ROWS, COLS, food_items)

    # Create ants
    ants = [Ant(environment.nest.position, environment) for _ in range(10)]

    return environment, ants

def render(SCREEN, environment, ants):
    # Clear the screen
    SCREEN.fill((255, 255, 255))

    # Draw pheromones
    for x in range(environment.rows):
        for y in range(environment.cols):
            intensity = environment.pheromone_grid[x][y]
            if intensity > 0:
                color = (255, 255, min(255, intensity))  # Light yellow for pheromones
                pygame.draw.rect(
                    SCREEN,
                    color,
                    (y * GRID_SIZE, x * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                )

    # Draw food
    for food in environment.food_items:
        food_x, food_y = food.position
        food_color = (0, 128, 0)  # Dark green for food
        pygame.draw.rect(
            SCREEN,
            food_color,
            (food_y * GRID_SIZE, food_x * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        )

    # Draw nest
    nest_x, nest_y = environment.nest.position
    pygame.draw.rect(
        SCREEN,
        (255, 0, 0),  # Red for nest
        (nest_y * GRID_SIZE, nest_x * GRID_SIZE, GRID_SIZE, GRID_SIZE)
    )

    # Draw ants
    for ant in ants:
        ant_x, ant_y = ant.position
        pygame.draw.circle(
            SCREEN,
            (0, 0, 0),  # Black for ants
            (ant_y * GRID_SIZE + GRID_SIZE // 2, ant_x * GRID_SIZE + GRID_SIZE // 2),
            GRID_SIZE // 3
        )

    # Update the display
    pygame.display.flip()

async def run_simulation(environment, ants):
    asyncio.create_task(environment.decay_pheromones())  # Start pheromone decay
    asyncio.create_task(environment.spawn_random_food(spawn_interval=15))  # Spawn random food every 5-15 seconds

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

        tasks = [ant.decide_and_act() for ant in ants]
        await asyncio.gather(*tasks)
        render(SCREEN, environment, ants)
        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    pygame.init()
    SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Virtual Ant Farm")

    environment, ants = setup_simulation()

    try:
        asyncio.run(run_simulation(environment, ants))
    except KeyboardInterrupt:
        print("Simulation stopped.")
