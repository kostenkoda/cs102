import pygame
from pygame.locals import *
import random
from copy import deepcopy


class GameOfLife:

    def __init__(self, width: int = 640, height: int = 480, cell_size: int = 10, speed: int = 10) -> None:
        self.width = width
        self.height = height
        self.cell_size = cell_size

        # Устанавливаем размер окна
        self.screen_size = width, height
        # Создание нового окна
        self.screen = pygame.display.set_mode(self.screen_size)

        # Вычисляем количество ячеек по вертикали и горизонтали
        self.cell_width = self.width // self.cell_size
        self.cell_height = self.height // self.cell_size

        # Скорость протекания игры
        self.speed = speed

    def draw_lines(self) -> None:
        for x in range(0, self.width, self.cell_size):
            pygame.draw.line(self.screen, pygame.Color('black'),
                             (x, 0), (x, self.height))
        for y in range(0, self.height, self.cell_size):
            pygame.draw.line(self.screen, pygame.Color('black'),
                             (0, y), (self.width, y))

    def run(self) -> None:
        pygame.init()
        clock = pygame.time.Clock()
        self.grid = self.create_grid()
        pygame.display.set_caption('Game of Life')
        self.screen.fill(pygame.Color('white'))
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
            self.draw_lines()
            self.draw_grid()
            self.get_next_generation()
            pygame.display.flip()
            clock.tick(self.speed)
        pygame.quit()

    def create_grid(self, randomize: bool = True) -> list:
        grid = [[0] * self.cell_width for i in range(self.cell_height)]
        if randomize:
            for x in range(self.cell_height):
                for y in range(self.cell_width):
                    grid[x][y] = random.randint(0, 1)
        return grid


    def draw_grid(self) -> None:
        for x in range(self.cell_height):
            for y in range(self.cell_height):
                if self.grid[x][y] == 1:
                    c = pygame.Color('green')
                else:
                    c = pygame.Color('white')
                pygame.draw.rect(self.screen, c, (y * self.cell_width + 1, x * self.cell_height + 1, self.cell_size - 1, self.cell_size - 1))


    def get_neighbours(self, cell: tuple) -> list:
        neighbours = []
        x, y = cell
        for i in range(x - 1, x + 2):
            for j in range(y - 1, y + 2):
                if i in range(0, self.cell_height) and j in range(0, self.cell_width) and (i != x or j != y):
                    neighbours.append(self.grid[i][j])
        return neighbours

    def get_next_generation(self) -> list:
        ngrid = deepcopy(self.grid)
        for x in range(self.cell_height):
            for y in range(self.cell_width):
                if sum(self.get_neighbours((x,y))) < 2 or sum(self.get_neighbours((x,y))) > 3:
                    ngrid[x][y] = 0
                elif sum(self.get_neighbours((x,y))) == 3:
                    ngrid[x][y] = 1
        self.grid = ngrid
        return self.grid


if __name__ == '__main__':
    game = GameOfLife(400, 400, 20)
    game.run()
