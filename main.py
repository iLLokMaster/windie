import os
from ctypes import windll
import pygame
import random
import math

enemies = []
points = []
enemy_bullets = []
PLAYER_SCALE = 50
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
PLAYER_RADIUS = 25
BULLET_RADIUS = 5
BULLET_SPEED = 10
BULLET_COLOR = (255, 255, 255)
SHRINK_AMOUNT = 30
SHRINK_INTERVAL = 75
ENEMY_RADIUS = 20
ENEMY_COLOR = (0, 255, 0)
POINT_COLOR = (128, 0, 128)
SPAWN_INTERVAL = 6000
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
HEALTH_BAR_COLOR = (0, 128, 0)

COUNT_OF_POINTS = 0
TOTAL_ENEMIES = 0

os.environ['SDL_VIDEO_WINDOW_POS'] = "20, 50"
pygame.mixer.pre_init()
pygame.mixer.init()
pygame.init()
font = pygame.font.SysFont('arial', 24)
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), )
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
        self.invulnerable_time = 0  # Время бессмертия
        self.invulnerable_duration = 1000  # 1 секунда бессмертия

    def draw(self, counter_text, counter_x, counter_y):
        """Отрисовка персонажа на холсте."""
        if self.invulnerable_time > 0:
            # Мигаем игрока, когда он бессмертен
            if (pygame.time.get_ticks() // 100) % 2 == 0:
                return  # Не отрисовываем игрока
        sprite_image = pygame.image.load('data/pic/player1.png')
        sprite_image = pygame.transform.scale(sprite_image, (PLAYER_SCALE, PLAYER_SCALE))
        screen.blit(sprite_image, (self.x - PLAYER_SCALE // 2, self.y - PLAYER_SCALE // 2))
        screen.blit(counter_text, (counter_x, counter_y))
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
        """Изменение координат. Выполняет перемещение персонажа по экрану."""
        self.x += dx
        self.y += dy

    def shoot(self):
        """Создание и отрисовка пули."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time >= self.shoot_cooldown:
            bullet = Bullet(self.x, self.y)
            cursor_x, cursor_y = pygame.mouse.get_pos()
            bullet.set_velocity_towards_cursor(cursor_x, cursor_y)
            self.bullets.append(bullet)
            self.last_shot_time = current_time

    def update_bullets(self):
        """Обработка соприкосновения пули с границей экрана."""
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
        if self.invulnerable_time <= 0:  # Проверка на бессмертие
            self.health -= amount
            if self.health <= 0:
                game_over()
            self.invulnerable_time = self.invulnerable_duration  # Установка времени бессмертия

    def update(self):
        """Обновление состояния игрока."""
        if self.invulnerable_time > 0:
            self.invulnerable_time -= clock.get_time()  # Уменьшение времени бессмертия


class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = BULLET_RADIUS
        self.dx = 0
        self.dy = -BULLET_SPEED

    def draw(self, screen):
        """Отрисовка пули на холсте."""
        pygame.draw.circle(screen, BULLET_COLOR, (self.x, self.y), self.radius)

    def update(self):
        """Обновление положения пули на экране."""
        self.x += self.dx
        self.y += self.dy

    def is_outside_screen(self):
        """Проверка, вышла ли пуля за границы экрана."""
        return self.x < 0 or self.x > WINDOW_WIDTH or self.y < 0 or self.y > WINDOW_HEIGHT

    def set_velocity_towards_cursor(self, cursor_x, cursor_y):
        dx = cursor_x - self.x
        dy = cursor_y - self.y
        angle = math.atan2(dy, dx)
        self.dx = math.cos(angle) * BULLET_SPEED
        self.dy = math.sin(angle) * BULLET_SPEED


class EnemyBullet(Bullet):
    def __init__(self, x, y):
        super().__init__(x, y)

    def draw(self, screen):
        """Отрисовка пули на холсте."""
        sprite_image = pygame.image.load('data/pic/bullet_for_enemy.png')
        sprite_image = pygame.transform.scale(sprite_image, (100, 100))
        screen.blit(sprite_image, (self.x - 50, self.y - 50))


class Enemy:
    def __init__(self, x, y, health, type_en):
        self.x = x
        self.y = y
        self.type = type_en
        self.radius = ENEMY_RADIUS
        self.health = health
        self.mass = health
        self.speed = 2  # Скорость обычного врага

    def draw(self, screen, enemy):
        sprite_image = pygame.image.load('data/pic/1_rang_enemy.png')
        sprite_image = pygame.transform.scale(sprite_image, (50, 50))
        screen.blit(sprite_image, (self.x - 25, self.y - 25))
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

    def update(self, player):
        """Движение врага к игроку."""
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        if distance > 0:
            dx /= distance  # Нормализация вектора
            dy /= distance
            self.x += dx * self.speed
            self.y += dy * self.speed

    def is_hit(self, bullet):
        """Проверка, попал ли враг в пулю."""
        distance = math.sqrt((self.x - bullet.x) ** 2 + (self.y - bullet.y) ** 2)
        return distance < self.radius + bullet.radius

    def is_colliding_with_player(self, player):
        """Проверка, столкнулся ли враг с игроком."""
        distance = math.sqrt((self.x - player.x) ** 2 + (self.y - player.y) ** 2)
        return distance < self.radius + player.radius


class ShootingEnemy(Enemy):
    def __init__(self, x, y, health, type_en):
        super().__init__(x, y, health, type)
        self.shoot_cooldown = 1000  # Время между выстрелами
        self.type = type_en
        self.last_shot_time = pygame.time.get_ticks()
        self.speed = 1  # Уменьшенная скорость стреляющего врага

    def update(self, player):
        """Движение врага к игроку."""
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        if distance > 0:
            dx /= distance  # Нормализация вектора
            dy /= distance
            self.x += dx * self.speed
            self.y += dy * self.speed

    def draw(self, screen, enemy):
        sprite_image = pygame.image.load('data/pic/3_rang_enemy.png')
        sprite_image = pygame.transform.scale(sprite_image, (50, 50))
        screen.blit(sprite_image, (self.x - 25, self.y - 25))
        self.draw_health_bar(screen)

    def update(self, player):
        super().update(player)  # Движение к игроку
        self.shoot(player)  # Попытка стрельбы

    def shoot(self, player):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time >= self.shoot_cooldown:
            bullet = EnemyBullet(self.x, self.y)
            bullet.set_velocity_towards_cursor(player.x, player.y)
            enemy_bullets.append(bullet)  # Добавление пули в список пуль врагов
            self.last_shot_time = current_time


class Point:
    def __init__(self, mass, x, y):
        """Создание нового поинта. вычисление его размера по количеству добавляемых очков"""
        self.mass = mass
        self.x = x
        self.y = y

        if self.mass == 1:
            self.radius = 2
        elif 1 < self.mass < 5:
            self.radius = 5
        else:
            self.radius = 7

    def draw(self):
        pygame.draw.circle(screen, POINT_COLOR, (self.x, self.y), self.radius)

    def is_hit(self, player):
        """Проверка, попал ли игрок в поинт."""
        distance = math.sqrt((self.x - player.x) ** 2 + (self.y - player.y) ** 2)
        return distance < self.radius + player.radius

    def update(self):
        pass


def perks_menu():
    showing_perks = True

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


crosshair_image = pygame.Surface((20, 20), pygame.SRCALPHA)  # Создаем поверхность для перекрестия
pygame.draw.line(crosshair_image, WHITE, (10, 0), (10, 20), 2)  # Вертикальная линия
pygame.draw.line(crosshair_image, WHITE, (0, 10), (20, 10), 2)  # Горизонтальная линия
pygame.mouse.set_visible(False)


def game_loop():
    """Главный цикл программы со всеми обработчиками."""
    global points, COUNT_OF_POINTS
    global enemies, enemy_bullets  # Добавьте enemy_bullets в глобальные переменные
    global WINDOW_WIDTH, WINDOW_HEIGHT, screen
    global player, TOTAL_ENEMIES, SHRINK_INTERVAL, SPAWN_INTERVAL
    player = Player(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
    last_spawn_time = pygame.time.get_ticks()
    last_shrink_time = pygame.time.get_ticks()
    first_one = True

    if random.randint(1, 3) == 1:
        pygame.mixer.music.load('data/music/01. Windowkiller.mp3')
    elif random.randint(1, 3) == 2:
        pygame.mixer.music.load('data/music/02. Windowframe.mp3')
    else:
        pygame.mixer.music.load('data/music/03. Windowchill.mp3')
    pygame.mixer.music.play(loops=-1)

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
        if TOTAL_ENEMIES % 10 == 0:
            if TOTAL_ENEMIES != 0:
                if first_one:
                    SHRINK_INTERVAL -= 5
                    SPAWN_INTERVAL -= 100
                    first_one = False
        if TOTAL_ENEMIES == 1:
            SHRINK_INTERVAL = 75
        elif TOTAL_ENEMIES == 0:
            SHRINK_INTERVAL -= 5

        counter_x = WINDOW_WIDTH - 100
        counter_y = 10

        # Уменьшение экрана
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
        player.update()  # Обновление состояния игрока

        counter_text = font.render(f"{COUNT_OF_POINTS}", True, POINT_COLOR)
        current_time = pygame.time.get_ticks()
        if current_time - last_spawn_time >= SPAWN_INTERVAL + random.randint(-200, 200):
            spawn_enemy()
            last_spawn_time = current_time

        # Обработка столкновений пуль игрока с врагами
        for bullet in player.bullets[:]:
            for enemy in enemies[:]:
                if enemy.is_hit(bullet):
                    if enemy.health - 1 == 0:
                        enemies.remove(enemy)
                        TOTAL_ENEMIES += 1
                        first_one = True
                        if TOTAL_ENEMIES == 1:
                            SPAWN_INTERVAL = 2000
                        points.append(Point(enemy.mass, enemy.x, enemy.y))
                        player.bullets.remove(bullet)
                        break
                    else:
                        enemy.health -= 1
                        break

        # Обновление и проверка столкновений врагов
        for enemy in enemies:
            enemy.update(player)  # Обновляем врагов, чтобы они двигались к игроку
            if enemy.is_colliding_with_player(player):
                player.take_damage(10)

        # Обработка столкновений пуль врагов с игроком
        for bullet in enemy_bullets[:]:
            bullet.update()
            if bullet.is_outside_screen():
                enemy_bullets.remove(bullet)
            if (player.x + PLAYER_RADIUS > bullet.x > player.x - PLAYER_RADIUS
                    and player.y + PLAYER_RADIUS > bullet.y > player.y - PLAYER_RADIUS):
                player.take_damage(5)
                enemy_bullets.remove(bullet)

        for point in points:
            if point.is_hit(player):
                points.remove(point)
                COUNT_OF_POINTS += 1

        screen.fill(BLACK)
        player.draw(counter_text, counter_x, counter_y)
        player.draw_health_bar()
        for enemy in enemies:
            enemy.draw(screen, enemy)
        for bullet in enemy_bullets:  # Отрисовка пуль врагов
            bullet.draw(screen)  # Используем метод draw для пуль врагов
        for point in points:
            point.draw()

        # Получаем позицию курсора мыши
        cursor_x, cursor_y = pygame.mouse.get_pos()
        # Отрисовываем перекрестие прицела
        screen.blit(crosshair_image, (cursor_x - 10, cursor_y - 10))  # Центрируем перекрестие

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
    else:  # 'right'
        x = WINDOW_WIDTH
        y = random.randint(0, WINDOW_HEIGHT)

    # Случайный выбор типа врага (обычный или стреляющий)
    if TOTAL_ENEMIES >= 25 + random.randint(0, 5):
        if random.random() < 0.5:  # 50% шанс на создание стреляющего врага
            enemies.append(ShootingEnemy(x, y, 2, 3))
        else:
            enemies.append(Enemy(x, y, 2, 1))
    else:
        enemies.append(Enemy(x, y, 2, 1))


def game_over():
    showing_window = True
    game_over_text = font.render("игра окончена", True, WHITE)
    press_f_to_respect = font.render("Нажмите [пробел] для завершения", True, WHITE)
    score = font.render(f"Ваш счёт: {TOTAL_ENEMIES * pygame.time.get_ticks() // 10000}", True, WHITE)
    pygame.mixer_music.stop()
    pygame.mixer.music.load('data/music/mixkit-game-level-music-689.wav')
    pygame.mixer.music.play(loops = -1)
    while showing_window:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        screen.fill(BLACK)
        screen.blit(game_over_text, (WINDOW_WIDTH // 2 - game_over_text.get_width() // 2, WINDOW_HEIGHT // 2 - 50))
        screen.blit(press_f_to_respect, (WINDOW_WIDTH // 2 - press_f_to_respect.get_width()
                                         // 2, WINDOW_HEIGHT // 2 + 50))
        screen.blit(score, (WINDOW_WIDTH // 2 - score.get_width() // 2, WINDOW_HEIGHT // 2 + 100))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            exit()
        if keys[pygame.K_f]:
            game_over_text = font.render("спасибо за респект", True, WHITE)
        pygame.display.update()


game_loop()
