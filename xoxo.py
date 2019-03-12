from pysmt.shortcuts import FreshSymbol, Symbol, String, LE, GE, Int, Or, And, Equals, Plus, Solver, StrContains
from pysmt.typing import INT, STRING
from enum import Enum
class Cell(Enum):
    x = 1
    o = 4
    space = 0

sq_size = 3
test = 'tests/test1.txt'

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


# assertions for player 1
solver.add_assertion(Or(
    # rows
    Equals(Plus(board[0]), Int(3)), 
    Equals(Plus(board[1]), Int(3)), 
    Equals(Plus(board[2]), Int(3)),
    # cols
    Equals(Plus([row[0] for row in board]), Int(3)),
    Equals(Plus([row[1] for row in board]), Int(3)),
    Equals(Plus([row[2] for row in board]), Int(3)),
    # diags
    Equals(Plus([board[0][0], board[1][1], board[2][2]]), Int(3)),
    Equals(Plus([board[0][2], board[1][1], board[2][0]]), Int(3))))



print(solver.assertions)
# solve
res = solver.solve()
if res:
    for row in board:
        for cell in row:
            print Cell(int(solver.get_py_value(cell))).name,
        print ""
else:
    print("no result found")
