from ctypes import windll
import pygame
import random
import math

enemies = []
points = []
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
PLAYER_RADIUS = 15
BULLET_RADIUS = 5
BULLET_SPEED = 7
SHRINK_AMOUNT = 30
SHRINK_INTERVAL = 75
ENEMY_RADIUS = 20
ENEMY_COLOR = (0, 255, 0)
POINT_COLOR = (128, 0, 128)
SPAWN_INTERVAL = 2000
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
HEALTH_BAR_COLOR = (0, 128, 0)

COUNT_OF_POINTS = 0

pygame.init()
font = pygame.font.SysFont('arial', 24)
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Shooting Game")
clock = pygame.time.Clock()
pygame.event.set_grab(True)


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = PLAYER_RADIUS
        self.bullets = []
        self.shoot_cooldown = 500
        self.last_shot_time = pygame.time.get_ticks()
        self.health = 100

    def draw(self):
        """Отрисовка персонажа на холсте. {screen} -- объект экрана(холст)"""
        pygame.draw.circle(screen, WHITE, (self.x, self.y), self.radius)
        for bullet in self.bullets:
            bullet.draw(screen)

    def draw_health_bar(self):
        """Отрисовка полоски здоровья игрока."""
        bar_width = 200
        bar_height = 20
        health_ratio = self.health / 100
        current_width = int(bar_width * health_ratio)
        pygame.draw.rect(screen, HEALTH_BAR_COLOR, (10, 10, current_width, bar_height))
        pygame.draw.rect(screen, WHITE, (10, 10, bar_width, bar_height), 2)

    def move(self, dx, dy):
        """изменение координат. выполняет перемещение персонажа по экрану."""
        self.x += dx
        self.y += dy

    def shoot(self):
        """Создание и отрисовка пули.
        пуля летит по прямой траектори по направлению к курсору от персонажа."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time >= self.shoot_cooldown:
            bullet = Bullet(self.x, self.y)
            cursor_x, cursor_y = pygame.mouse.get_pos()
            bullet.set_velocity_towards_cursor(cursor_x, cursor_y)
            self.bullets.append(bullet)
            self.last_shot_time = current_time

    def update_bullets(self):
        """обработка соприкосновения пули с границей экрана.
        при соприкоснавении экран отодвигается от пули."""
        global WINDOW_WIDTH, WINDOW_HEIGHT, screen
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
                    for enemy in enemies:
                        enemy.x += SHRINK_AMOUNT
                    for point in points:
                        point.x += SHRINK_AMOUNT
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
                    for enemy in enemies:
                        enemy.y += SHRINK_AMOUNT
                    for point in points:
                        point.y += SHRINK_AMOUNT
                    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

                # Расширение окна вниз
                elif bullet.y >= WINDOW_HEIGHT:
                    WINDOW_HEIGHT += SHRINK_AMOUNT
                    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    def take_damage(self, amount):
        """Уменьшение здоровья игрока."""
        self.health -= amount
        if self.health <= 0:
            game_over()


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


class Enemy:
    def __init__(self, x, y, health):
        self.x = x
        self.y = y
        self.radius = ENEMY_RADIUS
        self.health = health
        self.mass = health

    def draw(self, screen):
        pygame.draw.circle(screen, ENEMY_COLOR, (self.x, self.y), self.radius)
        self.draw_health_bar(screen)

    def draw_health_bar(self, screen):
        """Отображение полоски здоровья врага."""
        bar_width = 40
        bar_height = 5
        health_ratio = self.health / self.mass
        current_width = int(bar_width * health_ratio)
        bar_x = self.x - bar_width // 2
        bar_y = self.y - self.radius - 10
        pygame.draw.rect(screen, RED, (bar_x, bar_y, current_width, bar_height))
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)

    def update(self):
        pass

    def is_hit(self, bullet):
        """Check if the enemy is hit by a bullet."""
        distance = math.sqrt((self.x - bullet.x) ** 2 + (self.y - bullet.y) ** 2)
        return distance < self.radius + bullet.radius

    def is_colliding_with_player(self, player):
        """Check if the enemy collides with the player."""
        distance = math.sqrt((self.x - player.x) ** 2 + (self.y - player.y) ** 2)
        return distance < self.radius + player.radius


class Point:
    def __init__(self, mass, x, y):
        """Создание нового поинта. вычисление его размера по поличеству добавляемых очков"""
        self.mass = mass
        self.x = x
        self.y = y

        if self.mass == 1:
            self.radius = 2
        if 1 < self.mass < 5:
            self.radius = 5
        else:
            self.radius = 7

    def draw(self):
        pygame.draw.circle(screen, POINT_COLOR, (self.x, self.y), self.radius)

    def is_hit(self, player):
        """Check if the enemy is hit by a bullet."""
        distance = math.sqrt((self.x - player.x) ** 2 + (self.y - player.y) ** 2)
        return distance < self.radius + player.radius

    def update(self):
        pass


def move_win(coordinates):
    hwnd = pygame.display.get_wm_info()['window']
    w, h = pygame.display.get_surface().get_size()
    windll.user32.MoveWindow(hwnd, -coordinates[0], -coordinates[1], w, h, False)


def perks_menu():
    showing_perks = True
    double_bullet_speed = False

    while showing_perks:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        screen.fill(BLACK)

        perks_text = font.render("Perks Menu", True, WHITE)
        double_speed_text = font.render("Нажмите 1: Двойная скорость", True, WHITE)
        back_text = font.render("Нажмите B для возвращения", True, WHITE)

        screen.blit(perks_text, (WINDOW_WIDTH // 2 - perks_text.get_width() // 2, WINDOW_HEIGHT // 2 - 100))
        screen.blit(double_speed_text,
                    (WINDOW_WIDTH // 2 - double_speed_text.get_width() // 2, WINDOW_HEIGHT // 2 - 50))
        screen.blit(back_text, (WINDOW_WIDTH // 2 - back_text.get_width() // 2, WINDOW_HEIGHT // 2 + 50))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_b]:
            showing_perks = False
        if keys[pygame.K_1]:
            global BULLET_SPEED
            BULLET_SPEED *= 2
            showing_perks = False

        pygame.display.update()
        clock.tick(15)


def game_loop():
    """Главный цикл программы со всеми обработчиками."""
    global points, COUNT_OF_POINTS
    global enemies
    global WINDOW_WIDTH, WINDOW_HEIGHT, screen
    player = Player(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
    last_spawn_time = pygame.time.get_ticks()
    last_shrink_time = pygame.time.get_ticks()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        if pygame.mouse.get_pressed()[0]:
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
        if keys[pygame.K_SPACE]:
            perks_menu()

        counter_x = WINDOW_WIDTH - 100
        counter_y = 10

        # уменьшение экрана
        current_time = pygame.time.get_ticks()
        if current_time - last_shrink_time >= SHRINK_INTERVAL:
            last_shrink_time = current_time
            if WINDOW_WIDTH > 100 and WINDOW_HEIGHT > 100:
                WINDOW_WIDTH -= 1
                WINDOW_HEIGHT -= 1
                screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
                player.x = min(player.x, WINDOW_WIDTH)
                player.y = min(player.y, WINDOW_HEIGHT)

        player.update_bullets()

        counter_text = font.render(f"{COUNT_OF_POINTS}", True, POINT_COLOR)

        player.update_bullets()
        current_time = pygame.time.get_ticks()
        if current_time - last_spawn_time >= SPAWN_INTERVAL:
            spawn_enemy()
            last_spawn_time = current_time

        for bullet in player.bullets[:]:
            for enemy in enemies[:]:
                if enemy.is_hit(bullet):
                    print(f"текущее xp врага - {enemy.health}")
                    if enemy.health - 1 == 0:
                        enemies.remove(enemy)
                        points.append(Point(enemy.mass, enemy.x, enemy.y))
                        player.bullets.remove(bullet)
                        break
                    else:
                        enemy.health -= 1
                        break

        for enemy in enemies:
            if enemy.is_colliding_with_player(player):
                player.take_damage(10)

        for point in points:
            if point.is_hit(player):
                points.remove(point)
                COUNT_OF_POINTS += 1

        screen.fill(BLACK)
        screen.blit(counter_text, (counter_x, counter_y))
        player.draw()
        player.draw_health_bar()
        for enemy in enemies:
            enemy.draw(screen)
        for point in points:
            point.draw()

        pygame.display.update()
        clock.tick(60)


def spawn_enemy():
    side = random.choice(['top', 'bottom', 'left', 'right'])
    if side == 'top':
        x = random.randint(0, WINDOW_WIDTH)
        y = 0
    elif side == 'bottom':
        x = random.randint(0, WINDOW_WIDTH)
        y = WINDOW_HEIGHT
    elif side == 'left':
        x = 0
        y = random.randint(0, WINDOW_HEIGHT)
    else:
        x = WINDOW_WIDTH
        y = random.randint(0, WINDOW_HEIGHT)

    enemies.append(Enemy(x, y, 2))


def game_over():
    print('игра окончена')
    exit()


game_loop()
