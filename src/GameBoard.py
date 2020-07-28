import numpy as np
from copy import copy
import pygame
import sys
import math
from random import randrange


# DEPTH FOR MINIMAX TREE
DEPTH = 3

SIZE = 30
STEP = SIZE + 35

SCREEN_WIDTH, SCREEN_HEIGHT = 460, 390

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255,255, 0)

EMPTY = 0
PLAYER_1 = 1
PLAYER_2 = 2

ITERS_PLAYER_1 = 0
ITERS_PLAYER_2 = 0

ROW_COUNT = 6
COLUMN_COUNT = 7
PARTITION = 4

WIN_VALUE = 1000000

# temporary solution
# diagonal format (column start point, row start point, length, type)
    # if type = 1 then in every move row(n + 1) = row(n) + 1
    # if type = 2 then in every move row(n + 1) = row(n) - 1
    # 12 diagonals
diagonals = [(0, 2, 4, 1), (0, 1, 5, 1), (0, 0, 6, 1), (1, 0, 6, 1), (2, 0, 5, 1), (3, 0, 4, 1),
                  (0, 3, 4, 0), (0, 4, 5, 0), (0, 5, 6, 0), (1, 5, 6, 0), (2, 5, 5, 0), (3, 5, 4, 0)]


def remaining_moves(board):
    counter = 0
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r, c] == EMPTY:
                counter += 1
    return counter

def possible_moves(board):
    moves = []
    for c in range(COLUMN_COUNT):
        if check_move_correct(board, c):
            moves.append(c)
    return moves

# check move correctness
def check_move_correct(board, c):
    return board[0, c] == 0


# columns [0 - 6] (c)
def make_move(board, player, c):
    r = ROW_COUNT - 1 # max i

    while r >= 0:
        if board[r, c] == EMPTY:
            board[r, c] = player
            return r, c
        r -= 1

    # columns already full (already checked) redundant (TODO)
    return False

def score_partition(partition, player, opponent):

    opp_points = partition.count(opponent)
    player_points = partition.count(player)


    if opp_points == 0 and player_points == 4:
        return 1000

    elif opp_points == 0 and player_points == 3:
        return 8

    elif opp_points == 0 and player_points == 2:
        return 3

    elif opp_points == 3 and player_points == 0:
        return -100

    elif opp_points == 2 and player_points == 0:
        return -3
    
    else:
        return 0


def score_move(board, player, opponent):

    total_score = 0

    # horizontal
    for r in range(ROW_COUNT):
        for c in range(COLUMN_COUNT-3):
            partition = list(board[r, c:c+PARTITION])
            total_score += score_partition(partition, player, opponent)

    # vertical
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT-3):
            partition = list(board[r:r+PARTITION, c])
            total_score += score_partition(partition, player, opponent)

    for diag in diagonals:
        c, r, l, type = diag

        iters = l - PARTITION + 1
        for ix in range(iters):

            # negative slope
            if type == 1:
                partition = [board[r + i, c + i] for i in range(PARTITION)]
                total_score += score_partition(partition, player, opponent)

            # positive slope
            if type == 0:
                partition = [board[r - i, c + i] for i in range(PARTITION)]
                total_score += score_partition(partition, player, opponent)

            # move to next partition in same diag
            c += 1
            r = r + 1 if type == 1 else r - 1

    # center
    c = 3
    for num in list(board[:, c]):
        if num == player:
            total_score += 3
        if num == opponent:
            total_score -= 3

    #for r in range(ROW_COUNT-3):
        #col_part = list(board[r:r+PARTITION, c])
        #total_score += score_partition(col_part, player, center=True)


    return total_score


def minimax(board, depth, maximizingPlayer, player, opponent, enableAlphaBeta = False, alpha=float('-inf'), beta=float('+inf')):
    global ITERS_PLAYER_1, ITERS_PLAYER_2
    if player == PLAYER_1:
        ITERS_PLAYER_1 += 1
    if player == PLAYER_2:
        ITERS_PLAYER_2 += 1

    checkWin = check_win(board)
    if depth == 0 or remaining_moves(board) == 0 or checkWin != None:

        if checkWin != None:

            if checkWin[0] == player:
                return 1000000

            if checkWin[0] == opponent:
                return -1000000

        if remaining_moves(board) == 0:
            print("No more valid moves!")
            return 0

        return score_move(board, player, opponent)

    else:
        if maximizingPlayer:
            value = float('-inf')
            for move in possible_moves(board):
                cboard = copy(board)
                make_move(cboard, opponent, move)
                score = minimax(cboard, depth - 1, False, player, opponent, enableAlphaBeta, alpha, beta)
                value = max(value, score)
                alpha = max(alpha, value)

                if alpha >= beta and enableAlphaBeta:
                    break
            return value

        else:
            value = float('+inf')
            for move in possible_moves(board):
                cboard = copy(board)
                make_move(cboard, player, move)
                score = minimax(cboard, depth - 1, True, player, opponent, enableAlphaBeta, alpha, beta)
                value = min(value, score)
                beta = min(value, beta)

                if alpha >= beta and enableAlphaBeta:
                    break
            return value


def ai_move(board, player, opponent, alphabeta=False):
    pos_moves = possible_moves(board)
    moves = []

    for move in pos_moves:
        cboard = copy(board)
        make_move(cboard, player, move)
        score = minimax(cboard, DEPTH, True, player, opponent, alphabeta)
        moves.append((move, score))

    moves = sorted(moves, key=lambda x : x[1], reverse=True)
    #print("moves: ", end='')
    #print(moves)
    return moves

def check_win(board):

    player1 = 0
    player2 = 0

    # check columns
    for c in range(COLUMN_COUNT):
        player1 = 0
        player2 = 0
        for r in range(ROW_COUNT):
            if board[r, c] == PLAYER_1:
                player1 += 1
                player2 = 0

            if board[r, c] == PLAYER_2:
                player2 += 1
                player1 = 0

            if board[r, c] == EMPTY:
                player1 = 0
                player2 = 0

            if player1 == 4:
                return PLAYER_1, (r, c)

            if player2 == 4:
                return PLAYER_2, (r, c)


    # check rows
    for r in range(ROW_COUNT):
        player1 = 0
        player2 = 0
        for c in range(COLUMN_COUNT):
            if board[r, c] == PLAYER_1:
                player1 += 1
                player2 = 0

            if board[r, c] == PLAYER_2:
                player2 += 1
                player1 = 0

            if board[r, c] == EMPTY:
                player1 = 0
                player2 = 0

            if player1 == 4:
                return PLAYER_1, (r, c)

            if player2 == 4:
                return PLAYER_2, (r, c)

    # check diagonals
    # diagonal format (column start point, row start point, length, type)
    # if type = 1 then in every move row(n + 1) = row(n) + 1
    # if type = 2 then in every move row(n + 1) = row(n) - 1
    # 12 diagonals

    for diag in diagonals:
        c, r, l, type = diag
        player1 = 0
        player2 = 0

        for ix in range(l):
            if board[r, c] == PLAYER_1:
                player1 += 1
                player2 = 0

            if board[r, c] == PLAYER_2:
                player2 += 1
                player1 = 0

            if board[r, c] == EMPTY:
                player1 = 0
                player2 = 0

            if player1 == 4:
                return PLAYER_1, (r, c)

            if player2 == 4:
                return PLAYER_2, (r, c)

            if type == 1:
                r += 1

            if type == 0:
                r -= 1

            c += 1

    # no win
    return None



def play_with_ai(game):

    board = np.zeros((ROW_COUNT, COLUMN_COUNT))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                x = event.pos[0]
                p1move = int(math.floor(x/(STEP)))
                r, c = make_move(board, PLAYER_1, p1move)
                game.updateSlot((r,c), RED)
                res = check_win(board)
                if res != None:
                    print(res)
                    print("Game finished!")
                    draw_win(game,res)
                    return

                moves = ai_move(board, PLAYER_2, PLAYER_1)
                if len(moves) == 0:
                    print("ERROR")
                    return
                r, c = make_move(board, PLAYER_2, moves[0][0])
                game.updateSlot((r, c), YELLOW)
                res = check_win(board)
                if res != None:
                    print(res)
                    print("Game finished!")
                    draw_win(game, res)
                    return

def play_ai_v_ai(game):

    board = np.zeros((ROW_COUNT, COLUMN_COUNT))

    global ITERS_PLAYER_1, ITERS_PLAYER_2
    global DEPTH

    DEPTH = 5

    ITERS_PLAYER_1 = 0
    ITERS_PLAYER_2 = 0

    first_move = True

    while True:
        moves = []
        if not first_move:
            moves = ai_move(board, PLAYER_1, PLAYER_2, alphabeta=True)
        else:
            moves.append((randrange(7), 1))
            first_move = False

        if len(moves) == 0:
            print("ERROR")
            return
        r, c = make_move(board, PLAYER_1, moves[0][0])
        game.updateSlot((r, c), RED)

        res = check_win(board)
        if res != None:
            print(res)
            print("Game finished!")
            draw_win(game, res)
            print("Moves player 1: " + str(ITERS_PLAYER_1))
            print("Moves player 2: " + str(ITERS_PLAYER_2))
            return

        moves = ai_move(board, PLAYER_2, PLAYER_1)
        if len(moves) == 0:
            print("ERROR")
            return
        r, c = make_move(board, PLAYER_2, moves[0][0])
        game.updateSlot((r, c), YELLOW)
        res = check_win(board)
        if res != None:
            print(res)
            print("Game finished!")
            draw_win(game, res)
            print("Moves player 1: " + str(ITERS_PLAYER_1))
            print("Moves player 2: " + str(ITERS_PLAYER_2))
            return

def play():
    board = np.zeros((ROW_COUNT, COLUMN_COUNT))

    print("Column numbers [0 ; 6]")

    while True:
        p1move = input("Player 1 move: ")
        make_move(board, PLAYER_1, int(p1move))
        print("-------Board ------")
        print(board)
        res = check_win(board)
        if res != None:
            print(res)
            print("Game finished!")
            return

        p2move = input("Player 2 move: ")
        make_move(board, PLAYER_2, int(p2move))
        print("-------Board ------")
        print(board)
        res = check_win(board)
        if res != None:
            print(res)
            print("Game finished!")
            return

        print("-------Board ------")
        print(board)

def draw_win(game, res):
    str = "YELLOW PLAYER WON"
    if res[0] == PLAYER_1:
        str = "RED PLAYER WON"

    game.draw_result(str)

class Slots():

    def __init__(self):
        self.slots = {}
        for c in range(COLUMN_COUNT):
            for r in range(ROW_COUNT):
                self.slots[(r, c)] = (SIZE + c*STEP, SIZE + r*STEP), WHITE


class Game():

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
        self.surface = pygame.Surface(self.screen.get_size())
        self.surface = self.surface.convert()
        self.surface.fill(WHITE)
        pygame.font.init()
        self.myfont = pygame.font.SysFont('Comic Sans MS', 50)

        self.slots = Slots()
        self.update()

    def update(self):
        for slot in self.slots.slots.values():
            pygame.draw.circle(self.screen, slot[1], slot[0], SIZE)
        pygame.display.flip()

    def draw_result(self, result):
        txsurface = self.myfont.render(result, False, BLUE)
        self.screen.blit(txsurface, (50, 50))
        pygame.display.flip()
        pygame.time.delay(5000)

    def updateSlot(self, position, color):
        self.slots.slots[position] = self.slots.slots[position][0], color
        self.update()


if __name__ == '__main__':

    while True:
        print("PLAYER vs AI ENTER: 1")
        print("AI vs AI ENTER: 2")
        dec = input("EXIT ENTER: 0\n: ")

        try:
            dec = int(dec)
        except Exception:
            print("wrong number, exiting")

        if dec == 1:
            game = Game()
            play_with_ai(game)
            pygame.time.delay(5000)

        if dec == 2:
            game = Game()
            play_ai_v_ai(game)
            pygame.time.delay(5000)

        else:
            break

