import pygame
import sys
import random
import os

# Инициализация Pygame
pygame.init()

# Настройки окна
WIDTH, HEIGHT = 800, 600
tile_size = 40
cols, rows = WIDTH // tile_size, HEIGHT // tile_size
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pacman")

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Игровые объекты
pacman_pos = [0, 0]  # Начальная позиция Пакмана в клетках
pacman_real_pos = [pacman_pos[0] * tile_size, pacman_pos[1] * tile_size]  # Реальная позиция для плавного перемещения
coin_radius = 10
score = 0
num_coins = 0  # Количество монет будет определено после загрузки уровня
pacman_speed = 5  # Скорость перемещения Пакмана по клеткам (пикселей в секунду)
levels_completed = 0  # Счетчик пройденных уровней

# Путь к папкам
textures_path = 'textures'
levels_path = 'levels'

# Загрузка изображений для анимации
pacman_images = {
    'left': pygame.transform.scale(pygame.image.load(os.path.join(textures_path, 'pacman_left.png')), (tile_size, tile_size)),
    'right': pygame.transform.scale(pygame.image.load(os.path.join(textures_path, 'pacman_right.png')), (tile_size, tile_size)),
    'up': pygame.transform.scale(pygame.image.load(os.path.join(textures_path, 'pacman_up.png')), (tile_size, tile_size)),
    'down': pygame.transform.scale(pygame.image.load(os.path.join(textures_path, 'pacman_down.png')), (tile_size, tile_size)),
}

# Загрузка текстуры стен
wall_texture = pygame.transform.scale(pygame.image.load(os.path.join(textures_path, 'wall_texture.png')), (tile_size, tile_size))

# Клеточная сетка (0 - пусто, 1 - стена, 2 - монетка, 3 - Пакман)
grid = [[0 for _ in range(cols)] for _ in range(rows)]

def load_level(filename):
    global grid, pacman_pos, pacman_real_pos, score, num_coins
    num_coins = 0
    score = 0
    grid = [[0 for _ in range(cols)] for _ in range(rows)]  # Сброс содержимого сетки
    with open(filename, 'r') as file:
        for y, line in enumerate(file):
            for x, char in enumerate(line.strip()):
                if char == '1':
                    grid[y][x] = 1  # Стена
                elif char == '2':
                    grid[y][x] = 2  # Монетка
                    num_coins += 1  # Увеличиваем количество монеток
                elif char == 'P':
                    pacman_pos[:] = [x, y]
                    pacman_real_pos[:] = [x * tile_size, y * tile_size]
                    grid[y][x] = 3  # Пакман
    # Установка Пакмана в левый верхний угол после загрузки уровня
    for y in range(rows):
        for x in range(cols):
            if grid[y][x] == 0:  # Найти первую свободную клетку
                pacman_pos[:] = [x, y]
                pacman_real_pos[:] = [x * tile_size, y * tile_size]
                return

def draw_grid():
    for y in range(rows):
        for x in range(cols):
            if grid[y][x] == 1:
                window.blit(wall_texture, (x * tile_size, y * tile_size))
            elif grid[y][x] == 2:
                pygame.draw.circle(window, WHITE, (x * tile_size + tile_size // 2, y * tile_size + tile_size // 2), coin_radius)

def draw_pacman(direction):
    pacman_image = pacman_images.get(direction)
    if pacman_image:
        window.blit(pacman_image, (pacman_real_pos[0], pacman_real_pos[1]))

def move_pacman(dx, dy):
    global pacman_pos, pacman_real_pos, score
    new_x, new_y = pacman_pos[0] + dx, pacman_pos[1] + dy
    if 0 <= new_x < cols and 0 <= new_y < rows:
        if grid[new_y][new_x] != 1:  # Проверка на стену
            if grid[new_y][new_x] == 2:
                score += 1
                grid[new_y][new_x] = 0  # Убираем монетку после сбора
            grid[pacman_pos[1]][pacman_pos[0]] = 0  # Освобождаем старую клетку
            pacman_pos = [new_x, new_y]
            pacman_real_pos[0] = new_x * tile_size
            pacman_real_pos[1] = new_y * tile_size  # Обновляем реальную позицию

def get_random_level():
    level_files = [f for f in os.listdir(levels_path) if f.startswith('level') and f.endswith('.txt')]
    return os.path.join(levels_path, random.choice(level_files))

def main():
    global pacman_pos, pacman_real_pos, score, levels_completed
    clock = pygame.time.Clock()
    direction = 'right'  # Начальное направление
    dx, dy = 0, 0

    def restart_game():
        global pacman_pos, pacman_real_pos, score, num_coins
        load_level(get_random_level())
        # Пакман устанавливается в левый верхний угол после загрузки уровня
        pacman_real_pos[0] = pacman_pos[0] * tile_size
        pacman_real_pos[1] = pacman_pos[1] * tile_size

    # Загрузка первого уровня
    restart_game()

    while True:
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        # Управление Пакманом
        keys = pygame.key.get_pressed()
        new_dx, new_dy = 0, 0

        if keys[pygame.K_LEFT]:
            new_dx = -1
            direction = 'left'
        elif keys[pygame.K_RIGHT]:
            new_dx = 1
            direction = 'right'
        elif keys[pygame.K_UP]:
            new_dy = -1
            direction = 'up'
        elif keys[pygame.K_DOWN]:
            new_dy = 1
            direction = 'down'

        if new_dx != 0 or new_dy != 0:
            move_pacman(new_dx, new_dy)

        # Заполнение фона
        window.fill(BLACK)

        # Отрисовка сетки, Пакмана и монеток
        draw_grid()
        draw_pacman(direction)

        # Отображение счета
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f'Score: {score}', True, WHITE)
        window.blit(score_text, (10, 10))

        # Отображение количества пройденных уровней
        levels_text = font.render(f'Levels: {levels_completed}', True, WHITE)
        window.blit(levels_text, (WIDTH - 150, 10))

        # Выход из игры при сборе всех монеток
        if score == num_coins:
            font = pygame.font.SysFont(None, 72)
            win_text = font.render('You Win!', True, WHITE)
            text_rect = win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))  # Центрирование текста
            window.blit(win_text, text_rect.topleft)
            pygame.display.flip()
            pygame.time.wait(2000)  # Задержка для отображения сообщения
            levels_completed += 1  # Увеличиваем счетчик пройденных уровней
            restart_game()  # Перезагрузка уровня

        # Обновление экрана
        pygame.display.flip()

        # Ограничение частоты кадров
        clock.tick(20)  # Частота кадров установлена на 20

if __name__ == "__main__":
    main()
