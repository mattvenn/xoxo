from pysmt.shortcuts import FreshSymbol, Symbol, String, LE, GE, Int, Or, And, Equals, Plus, Solver, StrContains
from pysmt.typing import INT, STRING
from enum import Enum
class Cell(Enum):
    x = 1
    o = 4
    s = 0

sq_size = 3
test = 'tests/blank.txt'

# create symbols for the board
board = [[FreshSymbol(INT) for _ in xrange(sq_size)]
    for _ in xrange(sq_size)]

solver = Solver(name="z3")

# setup assertions for board
for row in board:
    for cell in row:
        solver.add_assertion(Or([Equals(cell, Int(i.value))
             for i in Cell]))

# load board
with open(test) as fh:
    for row, line in enumerate(fh.readlines()):
        for col, cell in enumerate(line.strip().split(' ')):
            if cell == Cell.x.name:
                solver.add_assertion(Equals(board[row][col], Int(Cell.x.value)))
            elif cell == Cell.o.name:
                solver.add_assertion(Equals(board[row][col], Int(Cell.o.value)))

def get_win_assertion(player):
    # rows
    return Or(
        Equals(Plus(board[0]), Int(player * sq_size)), 
        Equals(Plus(board[1]), Int(player * sq_size)), 
        Equals(Plus(board[2]), Int(player * sq_size)),
        # cols
        Equals(Plus([row[0] for row in board]), Int(player * sq_size)),
        Equals(Plus([row[1] for row in board]), Int(player * sq_size)),
        Equals(Plus([row[2] for row in board]), Int(player * sq_size)),
        # diags
        Equals(Plus([board[0][0], board[1][1], board[2][2]]), Int(player * sq_size)),
        Equals(Plus([board[0][2], board[1][1], board[2][0]]), Int(player * sq_size)))

# assertions for players to win
o_win_assertions = get_win_assertion(Cell.o.value)
x_win_assertions = get_win_assertion(Cell.x.value)

display_board = [[Cell.s for _ in xrange(sq_size)] for _ in xrange(sq_size)]

print(solver.assertions)

def print_board():
    print("display board")
    for row in display_board:
        for cell in row:
            print cell.name,
        print ""

def print_solver_board():
    print("solver board")
    for row in board:
        for cell in row:
            print Cell(int(solver.get_py_value(cell))).name,
        print ""

def get_a_move(player):
    print("looking for a move for %s" % player)
    for r, row in enumerate(board):
        for c, cell in enumerate(row):
            if display_board[r][c] == Cell.s and Cell(int(solver.get_py_value(cell))) == player:
                return(r,c)

def convert_num_to_indices(num):
    row = int(num/sq_size)
    col = num % sq_size
    return(row,col)

def already_played(row, col):
    if display_board[row][col] == Cell.s:
        return False
    return True

def play_move(player, row, col):
    display_board[row][col] = player
    solver.add_assertion(Equals(board[row][col], Int(player.value)))

while True:
    print_board()
    next_cell = int(raw_input("type a cell (1-9):")) - 1
    row, col = convert_num_to_indices(next_cell)
    if(not already_played(row, col)):
        play_move(Cell.x, row, col)
    else:
        print("that cell is already taken")

    # can x win?
    res = solver.solve([x_win_assertions])
    if res:
        print_solver_board()
        row, col = get_a_move(Cell.x)
        print(row, col)
        play_move(Cell.o, row, col)

