# snake_ai_survival_fixed.py
import pygame
import random
import time
from collections import deque

CELL = 20
GRID = 25
PLAY_SIZE = GRID * CELL
STATS_HEIGHT = 120
WINDOW_SIZE = (PLAY_SIZE, PLAY_SIZE + STATS_HEIGHT)

pygame.init()
pygame.font.init()
screen = pygame.display.set_mode(WINDOW_SIZE)
clock = pygame.time.Clock()

# safe font fallback
try:
    font = pygame.font.SysFont("consolas", 22)
    if font is None:
        raise Exception()
except Exception:
    font = pygame.font.Font(None, 22)

def bfs(start, goal, snake_body):
    queue = deque([start])
    visited = {start: None}

    while queue:
        x, y = queue.popleft()
        if (x, y) == goal:
            path = []
            while (x, y) != start:
                path.append((x, y))
                x, y = visited[(x, y)]
            path.reverse()
            return path

        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
            nx, ny = x+dx, y+dy
            if 0 <= nx < GRID and 0 <= ny < GRID:
                if (nx, ny) not in visited and (nx, ny) not in snake_body:
                    visited[(nx, ny)] = (x, y)
                    queue.append((nx, ny))
    return None

snake = [(5,5),(4,5),(3,5)]
direction = (1,0)
food = (random.randint(0, GRID-1), random.randint(0, GRID-1))

start_time = time.time()
total_moves = 0
moves_since_food = 0
move_history = []
food_count = 0
alive = True

def place_food():
    # If snake fills board, game over / victory (no food to place)
    if len(snake) >= GRID * GRID:
        return None
    attempts = 0
    while True:
        attempts += 1
        f = (random.randint(0, GRID-1), random.randint(0, GRID-1))
        if f not in snake:
            return f
        # fallback guard (shouldn't be reached normally)
        if attempts > 10000:
            return None

def draw_grid():
    for x in range(0, PLAY_SIZE, CELL):
        pygame.draw.line(screen, (40,40,40), (x, 0), (x, PLAY_SIZE))
    for y in range(0, PLAY_SIZE, CELL):
        pygame.draw.line(screen, (40,40,40), (0, y), (PLAY_SIZE, y))

def draw_border():
    pygame.draw.rect(screen, (200,200,200), (0,0,PLAY_SIZE,PLAY_SIZE), 3)

def draw_stats():
    elapsed = int(time.time() - start_time)
    avg = (sum(move_history) / len(move_history)) if move_history else 0.0
    texts = [
        f"Time: {elapsed}s",
        f"Total Moves: {total_moves}",
        f"Moves Since Food: {moves_since_food}",
        f"Food Eaten: {food_count}",
        f"Avg Moves per Food: {avg:.1f}"
    ]
    y = PLAY_SIZE + 10
    for t in texts:
        img = font.render(t, True, (240,240,240))
        screen.blit(img, (10, y))
        y += 26

def draw():
    screen.fill((10,10,10))
    draw_grid()
    draw_border()
    # snake
    for x,y in snake:
        pygame.draw.rect(screen, (0,200,0), (x*CELL, y*CELL, CELL, CELL))
    # food
    if food is not None:
        fx, fy = food
        pygame.draw.rect(screen, (200,0,0), (fx*CELL, fy*CELL, CELL, CELL))
    draw_stats()
    pygame.display.flip()

# MAIN LOOP
while alive:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            alive = False
            break

    head = snake[0]

    # find path to food if exists
    if food is not None:
        path = bfs(head, food, snake)
    else:
        path = None

    if path is None:
        # fallback: try any safe direction
        moved = False
        for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
            nx, ny = head[0]+dx, head[1]+dy
            if 0 <= nx < GRID and 0 <= ny < GRID and (nx,ny) not in snake:
                direction = (dx,dy)
                moved = True
                break
        if not moved:
            alive = False
            break
    else:
        next_step = path[0]
        direction = (next_step[0]-head[0], next_step[1]-head[1])

    new_head = (head[0]+direction[0], head[1]+direction[1])

    # collision check
    if (new_head in snake or
        new_head[0] < 0 or new_head[0] >= GRID or
        new_head[1] < 0 or new_head[1] >= GRID):
        alive = False
        break

    snake.insert(0, new_head)
    total_moves += 1
    moves_since_food += 1

    if food is not None and new_head == food:
        food_count += 1
        move_history.append(moves_since_food)
        moves_since_food = 0
        food = place_food()
        if food is None:
            # no place to put food (board full) -> end game as victory
            alive = False
            break
    else:
        snake.pop()

    draw()
    clock.tick(12)

# DEATH / END SCREEN (pump events while showing message)
end_start = time.time()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit()

    screen.fill((10,10,10))
    dead_msg = font.render("DEAD" if len(snake) < GRID*GRID else "ALL CELLS FILLED - VICTORY", True, (255,50,50))
    moves_msg = font.render(f"Total Moves: {total_moves}", True, (255,255,255))
    eaten_msg = font.render(f"Food Eaten: {food_count}", True, (255,255,255))
    avg = (sum(move_history) / len(move_history)) if move_history else 0.0
    avg_msg = font.render(f"Avg Moves/Food: {avg:.1f}", True, (255,255,255))

    screen.blit(dead_msg, (PLAY_SIZE//2 - 160, PLAY_SIZE//2 - 30))
    screen.blit(moves_msg, (PLAY_SIZE//2 - 160, PLAY_SIZE//2 + 0))
    screen.blit(eaten_msg, (PLAY_SIZE//2 - 160, PLAY_SIZE//2 + 30))
    screen.blit(avg_msg, (PLAY_SIZE//2 - 160, PLAY_SIZE//2 + 60))
    pygame.display.flip()

    if time.time() - end_start > 3:
        break
    clock.tick(30)

pygame.quit()