import pygame
import time
import datetime as datetime
from random import randint

WIDTH = 600
HEIGHT = 600
PIXEL_WIDTH = 25
PIXEL_HEIGHT = 25
SCALED_WIDTH = WIDTH / PIXEL_WIDTH
SCALED_HEIGHT = HEIGHT / PIXEL_HEIGHT
BLACK = (0, 0, 0)
WHITE = (200, 200, 200)
GREEN = (51, 255, 153)
YELLOW = (255, 255, 51)
RED = (255, 51, 51)
PINK = (255, 51, 255)
BLOCK_SIZE = 20
direction = {"UP": [-1, 0], "DOWN": [1, 0], "LEFT": [0, -1], "RIGHT": [0, 1]}
DELAY = 0.1
BUTTON_DELAY_MILLISECONDS = 110
FOOD_EATEN_SOUND = './sounds/coin.wav'
GAME_OVER_SOUND = './sounds/game_over.mp3'
THEME_SOUND_ONE = './sounds/theme.mp3'
THEME_SOUND_TWO = './sounds/06 - Level Theme 2.mp3'
THEME_SOUND_THREE = './sounds/13 - Super Mario Rap.mp3'
mixer = pygame.mixer
mixer.init()


class Game:

    def __init__(self):
        self._running = True
        self._display_surf = None
        self.size = self.weight, self.height = WIDTH, HEIGHT
        self.snake = Snake()
        self.board = Board()
        self.food = Food(get_random_color())
        self.board.add_food(self.food)
        self.board.add_snake(self.snake)
        self.previous_keystroke_time = datetime.datetime.now()
        self.current_keystroke_time = datetime.datetime.now()

    def on_init(self):
        pygame.init()
        pygame.display.set_caption("Snake Game")
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
            return

    def on_keystroke(self, event):
        self.current_keystroke_time = datetime.datetime.now()
        diff_in_milliseconds = millis_interval(self.previous_keystroke_time, self.current_keystroke_time)
        if diff_in_milliseconds < BUTTON_DELAY_MILLISECONDS:
            return
        pressed = pygame.key.get_pressed()
        negated_direction = [coord * -1 for coord in self.snake.get_head().get_direction()]
        if event.key == ord('w') and not (pressed[pygame.K_d]) and not (pressed[pygame.K_a]) and not (
        pressed[pygame.K_s]):
            if negated_direction != direction.get("UP"):
                self.snake.get_head().set_direction(direction.get("UP"))
        elif event.key == ord('a') and not (pressed[pygame.K_s]) and not (pressed[pygame.K_d]) and not (
        pressed[pygame.K_w]):
            if negated_direction != direction.get("LEFT"):
                self.snake.get_head().set_direction(direction.get("LEFT"))
        elif event.key == ord('s') and not (pressed[pygame.K_d]) and not (pressed[pygame.K_a]) and not (
        pressed[pygame.K_w]):
            if negated_direction != direction.get("DOWN"):
                self.snake.get_head().set_direction(direction.get("DOWN"))
        elif event.key == ord('d') and not (pressed[pygame.K_w]) and not (pressed[pygame.K_s]) and not (
        pressed[pygame.K_a]):
            if negated_direction != direction.get("RIGHT"):
                self.snake.get_head().set_direction(direction.get("RIGHT"))
        self.previous_keystroke_time = datetime.datetime.now()

    def on_loop(self):
        if self.board.check_border(self.snake):
            print('Direction before rotation --> ', self.snake.get_head().get_direction())
            self.snake.rotate_body()
            print('Direction after rotation --> ', self.snake.get_head().get_direction())
        self.snake.update_locations(self.board)
        self.snake.update_directions()
        if self.snake.check_body_collision():
            # Play game over sound
            mixer.stop()
            game_over = mixer.Sound(GAME_OVER_SOUND)
            channel = game_over.play()
            while channel.get_busy() == True:
                continue

            pygame.mixer.music.load(GAME_OVER_SOUND)
            pygame.mixer.music.play(0)
            self._running = False
            return
        if self.board.check_food_eaten(self.snake):
            self.food = Food(get_random_color())
        self.board.add_snake(self.snake)
        self.board.add_food(self.food)

    def on_render(self):
        self.draw_grid()
        self.draw_board()
        pygame.display.update()

    def on_cleanup(self):
        pygame.quit()

    def draw_grid(self):
        for i in range(0, PIXEL_HEIGHT, 1):
            for j in range(0, PIXEL_WIDTH, 1):
                rect = pygame.Rect(i * SCALED_WIDTH, j * SCALED_HEIGHT,
                                   SCALED_WIDTH, SCALED_HEIGHT)
                pygame.draw.rect(self._display_surf, BLACK, rect)
                pygame.draw.rect(self._display_surf, WHITE, rect, 1)

    def draw_board(self):
        for i in range(0, len(self.board.get_grid()), 1):
            for j in range(0,
                           len(self.board.get_grid().__getitem__(i)), 1):

                board_val = self.board.get_grid()[j][i]
                if board_val == 1:
                    rect = pygame.Rect(i * SCALED_WIDTH, j * SCALED_HEIGHT,
                                       SCALED_WIDTH, SCALED_HEIGHT)
                    pygame.draw.rect(self._display_surf, RED, rect)
                elif board_val == -1:
                    rect = pygame.Rect(i * SCALED_WIDTH, j * SCALED_HEIGHT,
                                       SCALED_WIDTH, SCALED_HEIGHT)
                    pygame.draw.rect(self._display_surf, self.food.get_color(), rect)

    def on_execute(self):
        if self.on_init() == False:
            self._running = False

        theme_one = mixer.Sound(THEME_SOUND_ONE)
        theme_two = mixer.Sound(THEME_SOUND_TWO)
        theme_three = mixer.Sound(THEME_SOUND_THREE)
        playlist = [theme_two, theme_three, theme_one]
        channel = playlist.pop().play()
        while self._running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    self.on_keystroke(event)
                else:
                    self.on_event(event)
            self.on_loop()
            self.on_render()
            time.sleep(DELAY)
            if not channel.get_busy():
                playlist.pop().play()
        self.on_cleanup()


class Board:
    def __init__(self):
        self.grid = [[0] * PIXEL_HEIGHT for _ in range(PIXEL_WIDTH)]

    def get_grid(self):
        return self.grid

    def set_grid(self, grid):
        self.grid = grid

    def add_snake(self, snake):
        for piece in snake.get_pieces():
            x_coord = piece.get_x()
            y_coord = piece.get_y()
            self.grid[y_coord][x_coord] = 1

    def add_food(self, food):
        x_coord = food.get_x()
        y_coord = food.get_y()
        self.grid[y_coord][x_coord] = -1

    def check_food_eaten(self, snake):
        # Get the head of the snakes coordinates
        x_coord = snake.get_head().get_x()
        y_coord = snake.get_head().get_y()
        if not self.check_border(snake):
            if self.grid[y_coord][x_coord] == -1:
                # Food has been eaten
                snake.add_piece()
                pygame.mixer.music.load(FOOD_EATEN_SOUND)
                pygame.mixer.music.play(0)
                return True
        return False

    def check_border(self, snake):
        x_coord = snake.get_head().get_x()
        y_coord = snake.get_head().get_y()
        current_direction = snake.get_head().get_direction()
        if x_coord == 0 and y_coord == 0 and set(current_direction) == set(direction.get("UP")):
            snake.get_head().set_direction(direction.get("RIGHT"))
        elif x_coord == 0 and y_coord == 0 and set(current_direction) == set(direction.get("LEFT")):
            snake.get_head().set_direction(direction.get("DOWN"))
        elif y_coord == 0 and x_coord == PIXEL_WIDTH - 1 and set(current_direction) == set(direction.get("RIGHT")):
            snake.get_head().set_direction(direction.get("DOWN"))
        elif x_coord == PIXEL_WIDTH - 1 and y_coord == PIXEL_HEIGHT - 1 and set(current_direction) == set(direction.get("DOWN")):
            snake.get_head().set_direction(direction.get("LEFT"))
        elif x_coord == 0 and y_coord == PIXEL_HEIGHT - 1 and set(current_direction) == set(direction.get("LEFT")):
            snake.get_head().set_direction(direction.get("UP"))
        elif x_coord == 0 and set(current_direction) == set(direction.get("LEFT")):
            snake.get_head().set_direction(direction.get("UP"))
        elif y_coord == 0 and set(current_direction) == set(direction.get("UP")):
            snake.get_head().set_direction(direction.get("RIGHT"))
        elif x_coord == PIXEL_WIDTH - 1 and set(current_direction) == set(direction.get("RIGHT")):
            snake.get_head().set_direction(direction.get("DOWN"))
        elif y_coord == PIXEL_HEIGHT - 1 and set(current_direction) == set(direction.get("DOWN")):
            snake.get_head().set_direction(direction.get("LEFT"))


class Piece:
    def __init__(self, x, y, default_direction):
        self.x = x
        self.y = y
        self.direction = default_direction

    def get_direction(self):
        return self.direction

    def set_direction(self, direction):
        self.direction = direction

    def get_x(self):
        return self.x

    def set_x(self, newX):
        self.x = newX

    def get_y(self):
        return self.y

    def set_y(self, newY):
        self.y = newY


class Snake:
    def __init__(self):
        self.pieces = []
        self.pieces.append(self.get_appropriate_default_head())
        self.add_piece()
        self.add_piece()

    def get_appropriate_default_head(self):
        default_x_coord = randint(0, PIXEL_WIDTH - 1)
        default_y_coord = randint(0, PIXEL_HEIGHT - 1)
        quadrant = 0
        if default_x_coord >= PIXEL_WIDTH / 2 and default_y_coord <= PIXEL_HEIGHT / 2:
            quadrant = 1
        elif default_x_coord <= PIXEL_WIDTH / 2 and default_y_coord <= PIXEL_HEIGHT / 2:
            quadrant = 2
        elif default_x_coord <= PIXEL_WIDTH / 2 and default_y_coord >= PIXEL_HEIGHT / 2:
            quadrant = 3
        else:
            quadrant = 4
        find_appropriate_direction = False
        default_head_direction = get_random_direction()
        while not find_appropriate_direction:
            if quadrant == 1:
                if (set(default_head_direction) == set(direction.get("UP")) or
                        set(default_head_direction) == set(direction.get("RIGHT"))):
                    default_head_direction = get_random_direction()
                else:
                    find_appropriate_direction = True
            elif quadrant == 2:
                if (set(default_head_direction) == set(direction.get("UP")) or
                        set(default_head_direction) == set(direction.get("LEFT"))):
                    default_head_direction = get_random_direction()
                else:
                    find_appropriate_direction = True
            elif quadrant == 3:
                if (set(default_head_direction) == set(direction.get("LEFT")) or
                        set(default_head_direction) == set(direction.get("DOWN"))):
                    default_head_direction = get_random_direction()
                else:
                    find_appropriate_direction = True
            else:
                if (set(default_head_direction) == set(direction.get("RIGHT")) or
                        set(default_head_direction) == set(direction.get("DOWN"))):
                    default_head_direction = get_random_direction()
                else:
                    find_appropriate_direction = True
            return Piece(default_x_coord, default_y_coord, default_head_direction)

    def update_directions(self):
        # Start at the piece connected to the head
        index = 1
        while index < len(self.get_pieces()):
            piece = self.get_pieces().__getitem__(index)
            parent_piece = self.get_pieces().__getitem__(index - 1)
            if parent_piece.get_direction() != piece.get_direction():
                if index != len(self.get_pieces()) - 1:
                    child_piece = self.get_pieces().__getitem__(index + 1)
                    child_piece.set_direction(piece.get_direction())
                piece.set_direction(parent_piece.get_direction())
                index += 2
            else:
                index += 1

    def update_locations(self, board):
        grid = board.get_grid()
        for piece in self.get_pieces():
            current_x_coord = piece.get_x()
            current_y_coord = piece.get_y()
            delta_x = current_x_coord + piece.get_direction().__getitem__(1)
            delta_y = current_y_coord + piece.get_direction().__getitem__(0)
            piece.set_x(delta_x)
            piece.set_y(delta_y)
            grid[current_y_coord][current_x_coord] = 0


    def check_body_collision(self):
        result = False
        head_x_coord = self.get_head().get_x()
        head_y_coord = self.get_head().get_y()
        for index in range(1, len(self.get_pieces()) - 1, 1):
            body_x_coord = self.get_pieces().__getitem__(index).get_x()
            body_y_coord = self.get_pieces().__getitem__(index).get_y()
            if body_x_coord == head_x_coord and body_y_coord == head_y_coord:
                result = True
        return result

    def rotate_body(self):
        head_direction = self.get_head().get_direction()
        if head_direction == direction.get("UP"):
            self.get_head().set_direction(direction.get("RIGHT"))
        elif head_direction == direction.get("LEFT"):
            self.get_head().set_direction(direction.get("UP"))
        elif head_direction == direction.get("RIGHT"):
            self.get_head().set_direction(direction.get("DOWN"))
        else:
            self.get_head().set_direction(direction.get("LEFT"))


    def get_head(self):
        return self.pieces.__getitem__(0)

    def get_tail(self):
        return self.pieces.__getitem__(len(self.pieces) - 1)

    def get_pieces(self):
        return self.pieces

    def add_piece(self):
        tail_piece = self.get_tail()
        tail_piece_direction = tail_piece.get_direction()

        # Location needs to be shifted opposite of the direction
        direction_shift = [x * -1 for x in tail_piece_direction]
        delta_x = tail_piece.get_x() + direction_shift.__getitem__(1)
        delta_y = tail_piece.get_y() + direction_shift.__getitem__(0)
        new_tail_piece = Piece(delta_x, delta_y, tail_piece_direction)
        new_tail_piece.set_direction(tail_piece_direction)
        self.pieces.append(new_tail_piece)


class Food:
    def __init__(self, default_color):
        self.x = randint(1, PIXEL_WIDTH - 2)
        self.y = randint(1, PIXEL_WIDTH - 2)
        self.color = default_color

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_color(self):
        return self.color


def millis_interval(start, end):
    """start and end are datetime instances"""
    diff = end - start
    millis = diff.days * 24 * 60 * 60 * 1000
    millis += diff.seconds * 1000
    millis += diff.microseconds / 1000
    return millis


def get_random_direction():
    rand_val = randint(1, 4)
    if rand_val == 1:
        return direction.get("UP")
    elif rand_val == 2:
        return direction.get("DOWN")
    elif rand_val == 3:
        return direction.get("LEFT")
    else:
        return direction.get("RIGHT")


def get_random_color():
    red = randint(51, 255)
    blue = randint(51,255)
    green = randint(51, 255)
    return red, blue, green

if __name__ == "__main__":
    # call the main function
    game = Game()
    game.on_execute()
