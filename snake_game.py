import pygame
import sys
import random

# Initialize pygame
pygame.init()

# Screen dimensions
CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 20
WIDTH = CELL_SIZE * GRID_WIDTH
HEIGHT = CELL_SIZE * GRID_HEIGHT

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


def draw_rect(position, color):
    rect = pygame.Rect(position[0] * CELL_SIZE, position[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(screen, color, rect)


def main():
    snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
    direction = RIGHT
    food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and direction != DOWN:
                    direction = UP
                elif event.key == pygame.K_DOWN and direction != UP:
                    direction = DOWN
                elif event.key == pygame.K_LEFT and direction != RIGHT:
                    direction = LEFT
                elif event.key == pygame.K_RIGHT and direction != LEFT:
                    direction = RIGHT
        
        # Move snake
        head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
        if head in snake or not (0 <= head[0] < GRID_WIDTH and 0 <= head[1] < GRID_HEIGHT):
            break  # Game over
        snake.insert(0, head)
        if head == food:
            while food in snake:
                food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        else:
            snake.pop()
        
        screen.fill(BLACK)
        draw_rect(food, RED)
        for block in snake:
            draw_rect(block, GREEN)
        pygame.display.update()
        clock.tick(10)
    
    pygame.quit()


if __name__ == "__main__":
    main()
