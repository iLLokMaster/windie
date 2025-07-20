import os
import pygame
import random
import math

# константы
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
SHRINK_INTERVAL = 75
ENEMY_RADIUS = 20
ENEMY_COLOR = (0, 255, 0)
POINT_COLOR = (128, 0, 128)
SPAWN_INTERVAL = 6000
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
HEALTH_BAR_COLOR = (0, 128, 0)
show_health_bar = False
first_random_chose = True
COUNT_OF_POINTS = 0
TOTAL_ENEMIES = 0
Chance_to_spawn_a_shooting_enemy = 0.25
Chance_to_spawn_a_fast_enemy = 0.2
Chance_to_break_through = 0

# настройка pygame и окна
os.environ['SDL_VIDEO_WINDOW_POS'] = "20, 50"
pygame.mixer.pre_init()
pygame.mixer.init()
pygame.init()
font = pygame.font.SysFont('arial', 24)
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), )
pygame.display.set_caption("Shooting Game")
clock = pygame.time.Clock()
pygame.event.set_grab(True)

sprite_image_main = pygame.image.load('data/pic/1_rang_enemy.png')
sprite_image_main = pygame.transform.scale(sprite_image_main, (50, 50))
sprite_image_shoot = pygame.image.load('data/pic/3_rang_enemy.png')
sprite_image_shoot = pygame.transform.scale(sprite_image_shoot, (50, 50))
sprite_image_fast = pygame.image.load('data/pic/2_rang_enemy.png')
sprite_image_fast = pygame.transform.scale(sprite_image_fast, (50, 50))
sprite_image_player = pygame.image.load('data/pic/player1.png')
sprite_image_player = pygame.transform.scale(sprite_image_player, (PLAYER_SCALE, PLAYER_SCALE))
sprite_image_enemy_bullet = pygame.image.load('data/pic/bullet_for_enemy.png')
sprite_image_enemy_bullet = pygame.transform.scale(sprite_image_enemy_bullet, (100, 100))


class Player:
    """сам персонаж и прикладные к нему ментоды"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = PLAYER_RADIUS
        self.bullets = []
        self.shoot_cooldown = 500
        self.last_shot_time = pygame.time.get_ticks()
        self.health = 10
        self.max_health = 10  # Добавлено: максимальное здоровье
        self.invulnerable_time = 0  # Время бессмертия
        self.invulnerable_duration = 1000  # 1 секунда бессмертия
        self.show_health_bar = False  # По умолчанию полоска здоровья скрыта
        self.damage = 1  # урон
        self.SHRINK_AMOUNT = 50  # на сколько пикселей увеличивать окно

    def draw_health_bar(self):
        """Отрисовка полоски здоровья игрока."""
        if not self.show_health_bar:
            return
        bar_width = 200
        bar_height = 20
        health_ratio = self.health / self.max_health  # Используем max_health
        current_width = int(bar_width * health_ratio)
        pygame.draw.rect(screen, HEALTH_BAR_COLOR, (10, 10, current_width, bar_height))
        pygame.draw.rect(screen, WHITE, (10, 10, bar_width, bar_height), 2)

    def draw(self, counter_text, counter_x, counter_y):
        """Отрисовка персонажа на холсте."""
        if self.invulnerable_time > 0:
            # Мигаем игрока, когда он бессмертен
            if (pygame.time.get_ticks() // 100) % 2 == 0:
                return  # Не отрисовываем игрока
        screen.blit(sprite_image_player, (self.x - PLAYER_SCALE // 2, self.y - PLAYER_SCALE // 2))
        screen.blit(counter_text, (counter_x, counter_y))
        for bullet in self.bullets:
            bullet.draw()

    def move(self, dx, dy):
        """Изменение координат. Выполняет перемещение персонажа по экрану."""
        self.x += dx
        self.y += dy

        # Ограничение движения в пределах окна
        self.x = max(self.radius, min(self.x, WINDOW_WIDTH - self.radius))
        self.y = max(self.radius, min(self.y, WINDOW_HEIGHT - self.radius))

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

                # Расширение окна вправо
                if bullet.x >= WINDOW_WIDTH:
                    WINDOW_WIDTH += self.SHRINK_AMOUNT
                    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

                # Расширение окна вниз
                elif bullet.y >= WINDOW_HEIGHT:
                    WINDOW_HEIGHT += self.SHRINK_AMOUNT
                    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    def take_damage(self, amount):
        """Уменьшение здоровья игрока при получении урона от врага"""
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
    """пуля игрока"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = BULLET_RADIUS
        self.dx = 0
        self.dy = -BULLET_SPEED

    def draw(self):
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
        """расчёт направления движения пули"""
        dx = cursor_x - self.x
        dy = cursor_y - self.y
        angle = math.atan2(dy, dx)
        self.dx = math.cos(angle) * BULLET_SPEED
        self.dy = math.sin(angle) * BULLET_SPEED


class EnemyBullet(Bullet):
    """специальная пуля для врага."""

    def __init__(self, x, y):
        super().__init__(x, y)

    def draw(self):
        """Отрисовка пули на холсте."""
        screen.blit(sprite_image_enemy_bullet, (self.x - 50, self.y - 50))


class Enemy:
    """классический враг.
    просто двигается на игрока и наносит урон после сопрокосновения"""

    def __init__(self, x, y, health):
        self.x = x
        self.y = y
        self.radius = ENEMY_RADIUS
        self.health = health
        self.mass = (health // 2) + (health % 2)
        self.speed = 2  # Скорость обычного врага

    def draw(self, enemy):
        """отрисовка"""
        screen.blit(sprite_image_main, (self.x - 25, self.y - 25))
        self.draw_health_bar()

    def draw_health_bar(self):
        """Отображение полоски здоровья врага."""
        if show_health_bar:
            bar_width = 40
            bar_height = 5
            health_ratio = self.health / self.mass
            current_width = int(bar_width * health_ratio)
            bar_x = self.x - bar_width // 2
            bar_y = self.y - self.radius - 10
            pygame.draw.rect(screen, RED, (bar_x, bar_y, current_width, bar_height))
            pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)

    def update(self):
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

    def is_colliding_with_player(self):
        """Проверка, столкнулся ли враг с игроком."""
        distance = math.sqrt((self.x - player.x) ** 2 + (self.y - player.y) ** 2)
        return distance < self.radius + player.radius


class ShootingEnemy(Enemy):
    """одна из разновидностей врагов.
    умеет стрелять"""

    def __init__(self, x, y, health):
        super().__init__(x, y, health)
        self.shoot_cooldown = 2000  # Время между выстрелами
        self.last_shot_time = pygame.time.get_ticks()
        self.speed = 1  # скорость врага

    def update(self):
        # Если атрибут направления ещё не задан, определяем его по положению врага.
        if not hasattr(self, 'direction'):
            if self.y <= 0:
                self.direction = 'right'
            elif self.x >= WINDOW_WIDTH:
                self.direction = 'down'
            elif self.y >= WINDOW_HEIGHT:
                self.direction = 'left'
            elif self.x <= 0:
                self.direction = 'up'
            else:
                self.direction = 'right'

        # Движение по периметру окна
        if self.direction == 'right':
            self.x += self.speed
            if self.x >= WINDOW_WIDTH:
                self.x = WINDOW_WIDTH
                self.direction = 'down'
        elif self.direction == 'down':
            self.y += self.speed
            if self.y >= WINDOW_HEIGHT:
                self.y = WINDOW_HEIGHT
                self.direction = 'left'
        elif self.direction == 'left':
            self.x -= self.speed
            if self.x <= 0:
                self.x = 0
                self.direction = 'up'
        elif self.direction == 'up':
            self.y -= self.speed
            if self.y <= 0:
                self.y = 0
                self.direction = 'right'

        self.shoot()

    def draw(self, enemy):
        """отрисовка"""
        screen.blit(sprite_image_shoot, (self.x - 25, self.y - 25))
        self.draw_health_bar()

    def shoot(self):
        """Стрельба врагов. создаётся пуля, летящая по прямой"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time >= self.shoot_cooldown:
            bullet = EnemyBullet(self.x, self.y)
            bullet.set_velocity_towards_cursor(player.x, player.y)
            enemy_bullets.append(bullet)  # Добавление пули в список пуль врагов
            self.last_shot_time = current_time


class FastEnemy(Enemy):
    def __init__(self, x, y, health):
        super().__init__(x, y, health)
        self.ticks = 0
        self.dx = player.x - self.x + random.randint(-40, 40)
        self.dy = player.y - self.y + random.randint(-40, 40)
        self.speed = 3

    def update(self):
        """Движение врага к игроку."""
        if self.ticks < 100:
            self.dx = player.x - self.x + random.randint(-40, 40)
            self.dy = player.y - self.y + random.randint(-40, 40)
            distance = math.sqrt(self.dx ** 2 + self.dy ** 2)
            if distance > 0:
                self.dx /= distance  # Нормализация вектора
                self.dy /= distance
        if self.ticks >= 100:
            self.x += self.dx * self.speed
            self.y += self.dy * self.speed
            if self.ticks == 200:
                self.ticks = 0
        self.ticks += 1

    def draw(self, enemy):
        """отрисовка"""
        screen.blit(sprite_image_fast, (self.x - 25, self.y - 25))
        self.draw_health_bar()


class Point:
    """объект, выпадающий после нейтрализации врага.
    при соприконовении с игроком пропадает и зачисляется на счёт"""

    def __init__(self, mass, x, y):
        """Создание нового поинта. вычисление его размера по количеству добавляемых очков"""
        self.speed = 1.1
        self.radius = mass + 2
        self.x = x
        self.y = y

    def draw(self):
        """отрисовка."""
        pygame.draw.circle(screen, POINT_COLOR, (self.x, self.y), self.radius)

    def is_hit(self):
        """Проверка, попал ли игрок в поинт."""
        distance = math.sqrt((self.x - player.x) ** 2 + (self.y - player.y) ** 2)
        return distance < self.radius + player.radius

    def update(self):
        """Обновление движения поинтов.
        Если расстояние до игрока меньше порога, скорость притяжения увеличивается."""
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        if distance > 0:
            dx_norm = dx / distance
            dy_norm = dy / distance
            # Если поинт находится на небольшом расстоянии от игрока,
            # увеличиваем скорость притяжения (коэффициент можно настроить, например, 3)
            if distance < 100:
                attraction_speed = self.speed * 3
            else:
                attraction_speed = self.speed
            self.x += dx_norm * attraction_speed
            self.y += dy_norm * attraction_speed


class Perk:
    def __init__(self, name, base_cost, effect, pic):
        self.name = name
        self.base_cost = base_cost  # стоимость перка
        self.cost = base_cost  # текущая стоимость
        self.effect = effect
        self.purchased = 0
        self.player = Player
        self.picture = pic

    def purchase(self):
        """Применяет эффект перка, увеличивает счётчик покупок и пересчитывает стоимость."""
        self.effect()
        self.purchased += 1
        self.cost = int(self.base_cost * (1.5 ** self.purchased))  # цена увеличивается в 1,5 раза после покупки перка


def health_plus():
    player.health = min(player.health + 20, player.max_health)


def health_limit():
    player.max_health += 20
    player.health += 20


def health_bar():
    global show_health_bar
    show_health_bar = True
    player.show_health_bar = True
    perks.remove(Perk("Полоска здоровья", 50, health_bar, show_health_bar_pic))


def chance_to_spawn_a_shooting_enemy():
    global Chance_to_spawn_a_shooting_enemy
    if Chance_to_spawn_a_shooting_enemy > 0.02:
        Chance_to_spawn_a_shooting_enemy -= 0.02


def reset_win_scale():
    global WINDOW_WIDTH, WINDOW_HEIGHT
    WINDOW_WIDTH += 500
    WINDOW_HEIGHT += 500


def kill_all_enemies():
    enemies.clear()


def bust_speed():
    global BULLET_SPEED
    BULLET_SPEED += 2


def bust_shrink_amount():
    if player.SHRINK_AMOUNT < 200:
        player.SHRINK_AMOUNT += 5
    else:
        perks.remove(Perk("Сдвиг окна", 20, bust_shrink_amount, shrink_up_pic), )


def bust_damage():
    player.damage += 1


def bust_shoot_cooldown():
    if player.shoot_cooldown > 100:
        player.shoot_cooldown -= 20
    else:
        perks.remove(Perk("Частота выстрелов", 15, bust_shoot_cooldown, fire_rate_up_pic))


def chance_to_break_through():
    global Chance_to_break_through
    if Chance_to_break_through != 1:
        Chance_to_break_through += 0.1


speed_up_pic = pygame.transform.scale(pygame.image.load('data/pic/bust speed.png'), (200, 300))
health_up_pic = pygame.transform.scale(pygame.image.load('data/pic/add health.png'), (200, 300))
max_health_pic = pygame.transform.scale(pygame.image.load('data/pic/max health.png'), (200, 300))
show_health_bar_pic = pygame.transform.scale(pygame.image.load('data/pic/show heath bar.png'), (200, 300))
chance_to_spawn_a_shooting_enemy_pic = pygame.transform.scale(pygame.image.load('data/pic/chance shoot.png'),
                                                              (200, 300))
shrink_up_pic = pygame.transform.scale(pygame.image.load('data/pic/wall push.png'), (200, 300))
moment_push_pic = pygame.transform.scale(pygame.image.load('data/pic/moment push.png'), (200, 300))
damaged_up_pic = pygame.transform.scale(pygame.image.load('data/pic/damage.png'), (200, 300))
fire_rate_up_pic = pygame.transform.scale(pygame.image.load('data/pic/fire rate.png'), (200, 300))
shoot_through_pic = pygame.transform.scale(pygame.image.load('data/pic/shot throught.png'), (200, 300))
kill_all_enemies_pic = pygame.transform.scale(pygame.image.load('data/pic/kill all.png'), (200, 300))
perks = [
    Perk("Cкорость пули", 10, bust_speed, speed_up_pic),
    Perk("Востановление", 15, health_plus, health_up_pic),
    Perk("Лимит здоровья", 20, health_limit, max_health_pic),
    Perk("Полоска здоровья", 50, health_bar, show_health_bar_pic),
    Perk("Меньше стрелков", 10, chance_to_spawn_a_shooting_enemy, chance_to_spawn_a_shooting_enemy_pic),
    Perk("Сдвиг окна", 20, bust_shrink_amount, shrink_up_pic),
    Perk("Увеличить окно", 50, reset_win_scale, moment_push_pic),
    Perk("увеличение урона", 15, bust_damage, damaged_up_pic),
    Perk("Частота выстрелов", 15, bust_shoot_cooldown, fire_rate_up_pic),
    Perk("Пробить насквозь", 20, chance_to_break_through, shoot_through_pic),
    Perk("Убить всех врагов", 50, kill_all_enemies, kill_all_enemies_pic)]


class PerksMenu:
    """Меню перков. При запуске случайным образом предлагается 3 перка.
    Каждый перк имеет свою стоимость, и при повторной покупке его цена увеличивается."""

    def __init__(self):
        global first_random_chose
        self.screen = screen
        self.font = font
        self.font_perks = pygame.font.SysFont('arial', 16)
        # Случайным образом выбираем 3 различных перка из общего списка
        self.options = random.sample(perks, 3)

    def run(self):
        global COUNT_OF_POINTS  # счёт поинтов игрока
        menu_active = True
        message = ""  # на случай если поинтов не хватит
        first_press_time = pygame.time.get_ticks()
        pygame.display.set_mode((800, 800), pygame.RESIZABLE)
        crosshair_image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.line(crosshair_image, WHITE, (10, 0), (10, 20), 2)
        pygame.draw.line(crosshair_image, WHITE, (0, 10), (20, 10), 2)
        pygame.mouse.set_visible(False)

        while menu_active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

            self.screen.fill(BLACK)
            pygame.display.set_mode((800, 800), pygame.RESIZABLE)
            # Заголовок меню и инструкция
            title_text = self.font.render("Меню перков", True, WHITE)
            self.screen.blit(title_text, (800 // 2 - title_text.get_width() // 2, 800 // 2 - 350))
            back_text = self.font.render("Нажмите [пробел] для выхода", True, WHITE)
            self.screen.blit(back_text, (800 // 2 - back_text.get_width() // 2, 800 // 2 + 375))
            restock_text = self.font.render("Нажмите [r], чтобы сменить перки (10)", True, WHITE)
            self.screen.blit(restock_text, (800 // 2 - restock_text.get_width() // 2, 800 // 2 + 350))

            for i, perk in enumerate(self.options):  # Отображаем варианты перков
                option_text = self.font_perks.render(f"{i + 1}. {perk.name} - {perk.cost}", True, WHITE)
                self.screen.blit(option_text,
                                 (800 // 2 - perk.picture.get_width() // 2 + 200 * (i - 1), 400))
                self.screen.blit(perk.picture,
                                 (800 // 2 - perk.picture.get_width() // 2 + 200 * (i - 1), 100))

            # Вывод сообщения
            if message:
                msg_text = self.font.render(message, True, RED)
                self.screen.blit(msg_text, (800 // 2 - msg_text.get_width() // 2, 800 // 2 + 250))
            pygame.display.update()
            clock.tick(15)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                last_press_time = pygame.time.get_ticks()
                if last_press_time - first_press_time > 400:
                    menu_active = False
            if keys[pygame.K_r]:
                if COUNT_OF_POINTS >= 10:
                    COUNT_OF_POINTS -= 10
                    self.options = random.sample(perks, 3)
                else:
                    message = "Недостаточно поинтов для покупки!"

            # Обработка покупки перка
            for key_val, index in zip([pygame.K_1, pygame.K_2, pygame.K_3], range(3)):
                if keys[key_val]:
                    selected_perk = self.options[index]
                    if COUNT_OF_POINTS >= selected_perk.cost:
                        COUNT_OF_POINTS -= selected_perk.cost
                        selected_perk.purchase()
                        self.options[index] = random.choice(perks)
                    else:
                        message = "Недостаточно поинтов для покупки!"
                    pygame.time.delay(300)


def game_loop():
    """Главный цикл программы со всеми обработчиками."""
    global points, COUNT_OF_POINTS
    global enemies, enemy_bullets  # Добавьте enemy_bullets в глобальные переменные
    global WINDOW_WIDTH, WINDOW_HEIGHT, screen
    global player, TOTAL_ENEMIES, SHRINK_INTERVAL, SPAWN_INTERVAL
    global show_health_bar
    player = Player(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
    last_spawn_time = pygame.time.get_ticks()
    last_shrink_time = pygame.time.get_ticks()
    first_one = True

    # курсор(перекрестье)
    crosshair_image = pygame.Surface((20, 20), pygame.SRCALPHA)
    pygame.draw.line(crosshair_image, WHITE, (10, 0), (10, 20), 2)
    pygame.draw.line(crosshair_image, WHITE, (0, 10), (20, 10), 2)
    pygame.mouse.set_visible(False)

    # музыка в игре
    list_of_music = ['data/music/01. Windowkiller.mp3',
                     'data/music/02. Windowframe.mp3',
                     'data/music/Nitro_Fun_-_Cheat_Codes_VIP_64603577.mp3',
                     'data/music/Le_Castle_Vania_-_Infinite_Ammo_64572038.mp3',
                     'data/music/Styline_Tommie_Sunshine_-_BLACKOUT_Original_Mix_Original_Mix_66664034.mp3',
                     'data/music/PRXSXNT_FXTURE_KXRAIN_-_CRUEL_78404168.mp3',
                     'data/music/03. Windowchill.mp3'
                     ]
    rand_misic = random.choice(list_of_music)
    pygame.mixer.music.load(rand_misic)
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(loops = -1)
    first_press_time = pygame.time.get_ticks()
    perks_menu = PerksMenu()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        # обработка ввода
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
            last_press_time = pygame.time.get_ticks()
            if last_press_time - first_press_time > 400:
                perks_menu.run()
                first_press_time = pygame.time.get_ticks()
        if keys[pygame.K_ESCAPE]:
            exit()

        # постепенное усложнение игры
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

        screen.fill(BLACK)

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

        # обновление состояний
        player.update_bullets()
        player.update()

        # счётчик поинтов
        counter_text = font.render(f"{COUNT_OF_POINTS}", True, POINT_COLOR)
        current_time = pygame.time.get_ticks()
        if current_time - last_spawn_time >= SPAWN_INTERVAL + random.randint(-200, 200):
            spawn_enemy()
            last_spawn_time = current_time

        # Обработка столкновений пуль игрока с врагами
        for enemy in enemies[:]:
            for bullet in player.bullets[:]:
                if enemy.is_hit(bullet):
                    if random.random() > Chance_to_break_through:
                        player.bullets.remove(bullet)
                    if enemy.health - player.damage <= 0:
                        enemies.remove(enemy)
                        TOTAL_ENEMIES += 1
                        first_one = True
                        if TOTAL_ENEMIES == 1:
                            SPAWN_INTERVAL = 2000
                        points.append(Point(enemy.mass + random.randint(0, 1), enemy.x, enemy.y))
                        break
                    else:
                        enemy.health -= player.damage
                        break
            enemy.draw(enemy)

            enemy.update()  # Обновляем врагов, чтобы они двигались к игроку
            if enemy.is_colliding_with_player():
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
            bullet.draw()

        # обработка подбора поинта
        for point in points[:]:
            if point.is_hit():
                points.remove(point)
                COUNT_OF_POINTS += point.radius - 2
                continue  # переходим к следующему поинту, чтобы не обновлять уже удалённый объект
            point.update()
            point.draw()

        counter_x = WINDOW_WIDTH - 100
        counter_y = 10
        player.draw(counter_text, counter_x, counter_y)
        cursor_x, cursor_y = pygame.mouse.get_pos()  # Получаем позицию курсора мыши
        screen.blit(crosshair_image,
                    (cursor_x - 10, cursor_y - 10))  # Отрисовываем перекрестие прицела и Центрируем перекрестие

        if show_health_bar:
            player.draw_health_bar()
        pygame.display.update()
        clock.tick(30)


def spawn_enemy():
    """функция для спавна врагов"""
    # рандомный выбор места спавна врага
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
        if TOTAL_ENEMIES >= 50 + random.randint(0, 5):
            if random.random() < Chance_to_spawn_a_fast_enemy:  # 50% шанс на создание стреляющего врага
                enemies.append(FastEnemy(x, y, 3))
            else:
                if random.random() < Chance_to_spawn_a_shooting_enemy:  # 50% шанс на создание стреляющего врага
                    enemies.append(ShootingEnemy(x, y, 3))
                else:
                    enemies.append(Enemy(x, y, 2))
        else:
            if random.random() < Chance_to_spawn_a_shooting_enemy:  # 50% шанс на создание стреляющего врага
                enemies.append(ShootingEnemy(x, y, 3))
            else:
                enemies.append(Enemy(x, y, 2))
    else:
        enemies.append(Enemy(x, y, 2))


def game_over():
    # наполнение окна окончания игры
    showing_window = True
    game_over_text = font.render("игра окончена", True, WHITE)
    press_f_to_respect = font.render("Нажмите [пробел] для завершения", True, WHITE)
    score = font.render(f"Ваш счёт: {TOTAL_ENEMIES * pygame.time.get_ticks() // 10000}", True, WHITE)
    pygame.mixer_music.stop()
    pygame.mixer.music.load('data/music/mixkit-game-level-music-689.wav')
    pygame.mixer.music.play(loops = -1)
    screen = pygame.display.set_mode((800, 800), pygame.RESIZABLE)

    while showing_window:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # отображение
        screen.fill(BLACK)
        screen.blit(game_over_text, (800 // 2 - game_over_text.get_width() // 2, 800 // 2 - 50))
        screen.blit(press_f_to_respect, (800 // 2 - press_f_to_respect.get_width()
                                         // 2, 800 // 2 + 50))
        screen.blit(score, (800 // 2 - score.get_width() // 2, 800 // 2 + 100))

        # обработка ввода
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            exit()
        if keys[pygame.K_f]:
            game_over_text = font.render("спасибо за респект", True, WHITE)
        pygame.display.update()


game_loop()
