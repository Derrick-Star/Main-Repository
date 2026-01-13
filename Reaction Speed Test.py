import pygame
import random
import time
import sys

# Init
pygame.init()
WIDTH, HEIGHT = 400, 300
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Reaction Time Test")
font = pygame.font.SysFont(None, 40)

# States
waiting = True
ready = False
reaction_time = None
start_time = 0

# Countdown wait (random between 2–5s)
wait_time = random.uniform(2, 5)
countdown_start = time.time()

while True:
    screen.fill((0, 0, 0))  # black background
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            if ready:  # valid reaction
                reaction_time = (time.time() - start_time) * 1000
                ready = False
            elif waiting:  # clicked too early
                reaction_time = "Too soon!"
                waiting = False

    # State logic
    if waiting:
        screen.fill((200, 0, 0))  # red
        text = font.render("Wait for green...", True, (255, 255, 255))
        screen.blit(text, (80, 130))
        if time.time() - countdown_start >= wait_time:
            waiting = False
            ready = True
            start_time = time.time()
    elif ready:
        screen.fill((0, 200, 0))  # green
        text = font.render("PRESS NOW!", True, (0, 0, 0))
        screen.blit(text, (120, 130))
    elif reaction_time is not None:
        screen.fill((0, 0, 50))
        if isinstance(reaction_time, str):
            text = font.render(reaction_time, True, (255, 50, 50))
        else:
            text = font.render(f"{reaction_time:.0f} ms", True, (255, 255, 255))
        screen.blit(text, (130, 130))

    pygame.display.flip()