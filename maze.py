import argparse
import numpy as np
import os

parser = argparse.ArgumentParser()
parser.add_argument('maze')
parser.add_argument('-n', '--num', type=int, default=10)
parser.add_argument('-r', '--rows', type=int, default=9)
parser.add_argument('-c', '--columns', type=int, default=9)

WALL_TYPE = np.int8
WALL = 0
EMPTY = 1


class Maze:
    def __init__(self, rows, columns):
        assert rows >= 1 and columns >= 1

        self.nrows = rows
        self.ncolumns = columns
        self.board = np.zeros((rows, columns), dtype=WALL_TYPE)
        self.board.fill(EMPTY)

    def __str__(self):
        return os.linesep.join(''.join('X' if self.is_wall(i, j) else ' '
                                       for j in range(self.ncolumns))
                               for i in range(self.nrows))

    def __hash__(self):
        return hash(self.board.tostring())

    def __eq__(self, other):
        return np.array_equal(self.board, other.board)

    def set_borders(self):
        self.board[0, :] = self.board[-1, :] = WALL
        self.board[:, 0] = self.board[:, -1] = WALL

    def is_wall(self, x, y):
        assert self.in_maze(x, y)
        return self.board[x][y] == WALL

    def set_wall(self, x, y):
        assert self.in_maze(x, y)
        self.board[x][y] = WALL

    def remove_wall(self, x, y):
        assert self.in_maze(x, y)
        self.board[x][y] = EMPTY

    def in_maze(self, x, y):
        return 0 <= x < self.nrows and 0 <= y < self.ncolumns

    def write_to_file(self, filename):
        f = open(filename, 'w')
        f.write(str(self))
        f.close()

    @staticmethod
    def create_maze(rows, columns, seed=None, complexity=.5, density=.2):
        rows = (rows // 2) * 2 + 1
        columns = (columns // 2) * 2 + 1

        if seed is not None:
            np.random.seed(seed)

        # Adjust complexity and density relative to maze size
        complexity = int(complexity * (5 * (rows + columns)))
        density = int(density * ((rows // 2) * (columns // 2)))

        maze = Maze(rows, columns)
        maze.set_borders()

        # Make aisles
        for i in range(density):
            x = np.random.random_integers(0, rows // 2) * 2
            y = np.random.random_integers(0, columns // 2) * 2
            maze.set_wall(x, y)

            for j in range(complexity):
                neighbours = []

                if maze.in_maze(x - 2, y):
                    neighbours.append((x - 2, y))

                if maze.in_maze(x + 2, y):
                    neighbours.append((x + 2, y))

                if maze.in_maze(x, y - 2):
                    neighbours.append((x, y - 2))

                if maze.in_maze(x, y + 2):
                    neighbours.append((x, y + 2))

                if len(neighbours):
                    next_x, next_y = neighbours[np.random.random_integers(0, len(neighbours) - 1)]

                    if not maze.is_wall(next_x, next_y):
                        maze.set_wall(next_x, next_y)
                        maze.set_wall(next_x + (x - next_x) // 2, next_y + (y - next_y) // 2)
                        x, y = next_x, next_y

        return maze


if __name__ == '__main__':
    FLAGS = parser.parse_args()

    mazes = set()
    while len(mazes) < FLAGS.num:
        mazes.add(Maze.create_maze(FLAGS.columns + 1, FLAGS.rows + 1))

    for idx, maze in enumerate(mazes):
        maze.write_to_file("{}_{}.txt".format(FLAGS.maze, idx))