import pygame
import random
import math

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
PLAYER_RADIUS = 15
BULLET_RADIUS = 5
BULLET_SPEED = 10
SHRINK_AMOUNT = 5
SHRINK_INTERVAL = 1000

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Shooting Game")
clock = pygame.time.Clock()

clock = pygame.time.Clock()
pygame.event.set_grab(True)


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = PLAYER_RADIUS
        self.bullets = []

    def draw(self, screen):
        f"""Отрисовка персонажа на холсте. {screen} -- объект экрана(холст)"""
        pygame.draw.circle(screen, WHITE, (self.x, self.y), self.radius)
        for bullet in self.bullets:
            bullet.draw(screen)

    def move(self, dx, dy):
        """изменение координат. выполняет перемещение персонажа по экрану."""
        self.x += dx
        self.y += dy

    def shoot(self):
        """Создание и отрисовка пули.
        пуля летит по прямой траектори по направлению к курсору от персонажа."""
        bullet = Bullet(self.x, self.y)
        cursor_x, cursor_y = pygame.mouse.get_pos()
        bullet.set_velocity_towards_cursor(cursor_x, cursor_y)
        self.bullets.append(bullet)

    def update_bullets(self):
        """Обработка соприкосновения пули с границей экрана.
        При соприкосновении экран корректно расширяется."""
        global WINDOW_WIDTH, WINDOW_HEIGHT
        for bullet in self.bullets:
            bullet.update()
            if bullet.is_outside_screen():
                self.bullets.remove(bullet)

                # Расширение окна влево
                if bullet.x <= 0:
                    WINDOW_WIDTH += SHRINK_AMOUNT
                    self.x += SHRINK_AMOUNT  # Сдвиг игрока вправо
                    for other_bullet in self.bullets:
                        other_bullet.x += SHRINK_AMOUNT  # Сдвиг всех пуль вправо
                    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

                # Расширение окна вправо
                elif bullet.x >= WINDOW_WIDTH:
                    WINDOW_WIDTH += SHRINK_AMOUNT
                    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

                # Расширение окна вверх
                if bullet.y <= 0:
                    WINDOW_HEIGHT += SHRINK_AMOUNT
                    self.y += SHRINK_AMOUNT  # Сдвиг игрока вниз
                    for other_bullet in self.bullets:
                        other_bullet.y += SHRINK_AMOUNT  # Сдвиг всех пуль вниз
                    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

                # Расширение окна вниз
                elif bullet.y >= WINDOW_HEIGHT:
                    WINDOW_HEIGHT += SHRINK_AMOUNT
                    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))


class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = BULLET_RADIUS
        self.dx = 0
        self.dy = -BULLET_SPEED

    def draw(self, screen):
        f"""Отрисовка пули на холсте. принимает параметр {screen} -- холст"""
        pygame.draw.circle(screen, RED, (self.x, self.y), self.radius)

    def update(self):
        """Обновление положения пули на экране.
        нужно, чтобы пуля постоянно летела, каждый кадр."""
        self.x += self.dx
        self.y += self.dy

    def is_outside_screen(self):
        """"это вообще волшебная функция. я хз как она работает, но явно не без божьей помощи.
        не совветую её трогать!"""
        return self.x < 0 or self.x > WINDOW_WIDTH or self.y < 0 or self.y > WINDOW_HEIGHT

    def set_velocity_towards_cursor(self, cursor_x, cursor_y):
        dx = cursor_x - self.x
        dy = cursor_y - self.y
        angle = math.atan2(dy, dx)
        self.dx = math.cos(angle) * BULLET_SPEED
        self.dy = math.sin(angle) * BULLET_SPEED


def game_loop():
    """Главный цикл программы со всеми обработчиками."""
    global WINDOW_WIDTH, WINDOW_HEIGHT, screen

    player = Player(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
    last_shrink_time = pygame.time.get_ticks()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    player.shoot()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            player.move(0, -5)
        if keys[pygame.K_s]:
            player.move(0, 5)
        if keys[pygame.K_a]:
            player.move(-5, 0)
        if keys[pygame.K_d]:
            player.move(5, 0)

        current_time = pygame.time.get_ticks()
        if current_time - last_shrink_time >= SHRINK_INTERVAL:
            last_shrink_time = current_time
            if WINDOW_WIDTH > 100 and WINDOW_HEIGHT > 100:
                WINDOW_WIDTH -= SHRINK_AMOUNT
                WINDOW_HEIGHT -= SHRINK_AMOUNT
                screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
                player.x = min(player.x, WINDOW_WIDTH)
                player.y = min(player.y, WINDOW_HEIGHT)

        player.update_bullets()

        screen.fill(BLACK)
        player.draw(screen)
        pygame.display.update()

        clock.tick(60)


game_loop()
