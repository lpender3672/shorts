import pygame
import numpy as np
import numba

# conways game of life

# constants
WIDTH = 800
HEIGHT = 600
subdivision_size = 10
FPS = 5

BLACK =     (0, 0, 0)
WHITE =     (255, 255, 255)

# initialize pygame and create window
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Conway's Game of Life")
clock = pygame.time.Clock()

screen_array = np.zeros((WIDTH // subdivision_size, HEIGHT // subdivision_size), dtype=np.int8)

def draw_conway_glider_right(x, y):
    screen_array[x, y] = 1
    screen_array[x + 1, y] = 1
    screen_array[x + 2, y] = 1
    screen_array[x + 2, y + 1] = 1
    screen_array[x + 1, y + 2] = 1

def draw_conway_glider_left(x, y):
    screen_array[x, y] = 1
    screen_array[x + 1, y] = 1
    screen_array[x + 2, y] = 1
    screen_array[x, y + 1] = 1
    screen_array[x + 1, y + 2] = 1


@numba.njit
def apply_rules(screen_array):
    new_screen_array = np.zeros((WIDTH // subdivision_size, HEIGHT // subdivision_size), dtype=np.int8)
    
    for x in range(1, WIDTH // subdivision_size - 1):
        for y in range(1, HEIGHT // subdivision_size - 1):
            neighbors = screen_array[x - 1, y - 1] + screen_array[x, y - 1] + screen_array[x + 1, y - 1] + screen_array[x - 1, y] + screen_array[x + 1, y] + screen_array[x - 1, y + 1] + screen_array[x, y + 1] + screen_array[x + 1, y + 1]
            if screen_array[x, y] == 1:
                if neighbors < 2:
                    new_screen_array[x, y] = 0
                elif neighbors == 2 or neighbors == 3:
                    new_screen_array[x, y] = 1
                elif neighbors > 3:
                    new_screen_array[x, y] = 0
            elif screen_array[x, y] == 0:
                if neighbors == 3:
                    new_screen_array[x, y] = 1
    
    return new_screen_array

# game loop
running = True
while running:
    # keep loop running at the right speed
    clock.tick(FPS)
    # process input (events)
    for event in pygame.event.get():
        # check for closing window
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            x = x // subdivision_size
            y = y // subdivision_size
            if event.button == 1:
                draw_conway_glider_left(x, y)
            elif event.button == 3:
                draw_conway_glider_right(x, y)
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    # update
    screen_array = apply_rules(screen_array)

    # draw / render
    screen.fill(BLACK)
    # create surface from array
    surf = pygame.surfarray.make_surface(screen_array * 255)
    # scale surface
    surf = pygame.transform.scale(surf, (WIDTH, HEIGHT))
    # draw surface
    screen.blit(surf, (0, 0))
    # *after* drawing everything, flip the display
    pygame.display.flip()
