import pathlib
import random
import typing as tp
import abc
from copy import deepcopy
import time

import pygame
from pygame.locals import *

Cell = tp.Tuple[int, int]
Cells = tp.List[int]
Grid = tp.List[Cells]


class GameOfLife:
    def __init__(
        self,
        size: tp.Tuple[int, int],
        randomize: bool = True,
        max_generations: tp.Optional[float] = float("inf"),
    ) -> None:
        # Размер клеточного поля
        self.rows, self.cols = size
        # Предыдущее поколение клеток
        self.prev_generation = self.create_grid()
        # Текущее поколение клеток
        self.curr_generation = self.create_grid(randomize=randomize)
        # Максимальное число поколений
        self.max_generations = max_generations
        # Текущее число поколений
        self.generations = 1

    def create_grid(self, randomize: bool = False) -> Grid:
        grid = [[0] * self.rows for i in range(self.cols)]
        if randomize:
            for x in range(self.cols):
                for y in range(self.rows):
                    grid[x][y] = random.randint(0, 1)
        return grid
        pass

    def get_neighbours(self, cell: Cell) -> Cells:
        neighbours = []
        x, y = cell
        for i in range(3):
            for j in range(3):
                nbcols = y -1 + i
                nbrows = x - 1 + j
                if nbcols in range(0, self.cols) and nbrows in range(0, self.rows) and (nbrows != x or nbcols != y):
                    neighbours.append(self.curr_generation[nbrows][nbcols])
        return neighbours
        pass

    def get_next_generation(self) -> Grid:
        ng = deepcopy(self.curr_generation)
        for x in range(self.rows):
            for y in range(self.cols):
                if sum(self.get_neighbours((x,y))) < 2 or sum(self.get_neighbours((x,y))) > 3:
                    ng[x][y] = 0
                elif sum(self.get_neighbours((x,y))) == 3:
                    ng[x][y] = 1
        self.curr_generation = ng
        return self.curr_generation
        pass

    def step(self) -> None:
        self.prev_generation = deepcopy(self.curr_generation)
        self.curr_generation = deepcopy(self.get_next_generation())
        self.generations += 1
        pass

    @property
    def is_max_generations_exceeded(self) -> bool:
        k = 0
        for x in range(self.rows):
            for y in range(self.cols):
                if self.curr_generation[x][y] == 1:
                    k += 1
        if k > self.max_generations:
            return True
        else:
            return False
        pass

    @property
    def is_changing(self) -> bool:
        if self.prev_generation == self.curr_generation:
            return False
        else:
            return True
        pass

    @staticmethod
    def from_file(filename: pathlib.Path) -> "GameOfLife":
        """
        Прочитать состояние клеток из указанного файла.
        """
        grid_file = open(filename)
        grid = grid_file.readlines()
        for i in range(len(grid)):
            grid[i] = list(map(int, list(grid[i][0:len(grid[i])-1])))
        life = GameOfLife((len(grid), len(grid[i])))
        life.curr_generation = grid
        grid_file.close()
        return life
        pass

    def save(self, filename: pathlib.Path) -> None:
        """
        Сохранить текущее состояние клеток в указанный файл.
        """
        file = open(filename, 'w')
        for i in range(len(self.curr_generation)):
            file.write("".join(map(str, self.curr_generation[i])) + '\n')
        file.close()
        pass
