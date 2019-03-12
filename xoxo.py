from pysmt.shortcuts import FreshSymbol, Symbol, String, LE, GE, Int, Not, Or, And, Equals, Plus, Solver, StrContains
from pysmt.typing import INT, STRING
from enum import Enum
class Cell(Enum):
    x = 1
    o = 10
    s = 0

turns = 0
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

display_board = [[Cell.s for _ in xrange(sq_size)] for _ in xrange(sq_size)]

# load board
with open(test) as fh:
    for row, line in enumerate(fh.readlines()):
        for col, cell in enumerate(line.strip().split(' ')):
            if cell == Cell.x.name:
                solver.add_assertion(Equals(board[row][col], Int(Cell.x.value)))
                display_board[row][col] = Cell.x
                turns += 1
            elif cell == Cell.o.name:
                solver.add_assertion(Equals(board[row][col], Int(Cell.o.value)))
                display_board[row][col] = Cell.o

def get_win_assertion(player):
    return [
        # rows
        Equals(Plus(board[0]), Int(player * sq_size)), 
        Equals(Plus(board[1]), Int(player * sq_size)), 
        Equals(Plus(board[2]), Int(player * sq_size)),
        # cols
        Equals(Plus([row[0] for row in board]), Int(player * sq_size)),
        Equals(Plus([row[1] for row in board]), Int(player * sq_size)),
        Equals(Plus([row[2] for row in board]), Int(player * sq_size)),
        # diags
        Equals(Plus([board[0][0], board[1][1], board[2][2]]), Int(player * sq_size)),
        Equals(Plus([board[0][2], board[1][1], board[2][0]]), Int(player * sq_size))
        ]

# assertions for players to win
o_win_assertions = get_win_assertion(Cell.o.value)
x_win_assertions = get_win_assertion(Cell.x.value)


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
    # prioritise center position
    if display_board[1][1] == Cell.s and Cell(int(solver.get_py_value(board[1][1]))) == player:
        return(1,1)
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
    if next_cell < 0 or next_cell > 8:
        continue

    row, col = convert_num_to_indices(next_cell)
    if(not already_played(row, col)):
        play_move(Cell.x, row, col)
    else:
        print("that cell is already taken")
        continue

    turns += 1
    print("turn %d" % turns)

    next_move_assertion = Equals(Int((turns+1)*(Cell.x.value + Cell.o.value)), Plus(Plus(board[0]), Plus(board[1]), Plus(board[2])))
    this_move_assertion = Equals(Int((turns)*(Cell.x.value + Cell.o.value)), Plus(Plus(board[0]), Plus(board[1]), Plus(board[2])))
    o_win_this_turn_assertions = And(Or(o_win_assertions), this_move_assertion)
    x_win_next_turn_assertions = And(Or(x_win_assertions), next_move_assertion)

    # can I win next turn?
    if solver.solve([o_win_this_turn_assertions]):
        print("o can win like this")
        print_solver_board()
        result = get_a_move(Cell.o)
        if result is not None:
            print(result[0], result[1])
            play_move(Cell.o, result[0], result[1])

    elif solver.solve([x_win_next_turn_assertions]):
        # can x win next turn? if so stop
        assertions = And(Or(x_win_assertions), move_assertion)
        print(assertions)
        res = solver.solve([assertions])
        if res:
            print("x can win like this")
            print_solver_board()
            result = get_a_move(Cell.x)
            if result is not None:
                print(result[0], result[1])
                play_move(Cell.o, result[0], result[1])
    # otherwise try and win
    else:
        print("looking for a win")
        for future_turn in range(turns, 4):
            move_assertion = Equals(Int((future_turn)*(Cell.x.value + Cell.o.value)), Plus(Plus(board[0]), Plus(board[1]), Plus(board[2])))
            for assertion in o_win_assertions:
                print("trying %s turn %d" % (assertion, future_turn))
                res = solver.solve([assertion, move_assertion])
                if res:
                    print("found a win on turn %d" % future_turn)
                    print_solver_board()
                    row, col = get_a_move(Cell.o)
                    print(row, col)
                    play_move(Cell.o, row, col)
                    break
#        else:
#            print("I can't win")
#            exit()

    #print(solver.is_sat(Or(o_win_assertions)))
    print("-" * 40)
