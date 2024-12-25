import pygame
import math

# Initialize pygame
pygame.init()

# Set the window size
window_size = (1000, 1000)
screen = pygame.display.set_mode(window_size)

# Set the circle's starting position and size
circle_pos = [500, 500]
circle_radius = 20

# Set the movement speed and projectile properties
move_speed = 0.2
projectile_radius = 5
projectile_speed = 1

# Main game loop
running = True
projectiles = []
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if circle_radius >= 10:
                # Get the mouse position
                mouse_pos = pygame.mouse.get_pos()
                # Calculate the direction vector
                direction = (mouse_pos[0] - circle_pos[0], mouse_pos[1] - circle_pos[1])
                length = math.hypot(*direction)
                direction = (direction[0] / length, direction[1] / length)
                # Create a new projectile
                projectiles.append({'pos': circle_pos.copy(), 'dir': direction})

    # Get the pressed keys
    keys = pygame.key.get_pressed()

    # Update the circle's position based on the pressed keys
    if keys[pygame.K_w]:
        circle_pos[1] -= move_speed
    if keys[pygame.K_s]:
        circle_pos[1] += move_speed
    if keys[pygame.K_a]:
        circle_pos[0] -= move_speed
    if keys[pygame.K_d]:
        circle_pos[0] += move_speed

    # Update projectile positions
    for projectile in projectiles:
        projectile['pos'][0] += projectile['dir'][0] * projectile_speed
        projectile['pos'][1] += projectile['dir'][1] * projectile_speed

    # Clear the screen
    screen.fill((0, 0, 0))
    # Draw the circle
    pygame.draw.circle(screen, (255, 255, 255), circle_pos, circle_radius)
    # Draw projectiles
    for projectile in projectiles:
        pygame.draw.circle(screen, (255, 0, 0), projectile['pos'], projectile_radius)

    pygame.display.update()

# Quit pygame
pygame.quit()