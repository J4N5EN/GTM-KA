# Almost same code as SimGames.py, except it can simulate games and remove the n last moves.

import csv
import random
import copy
from collections import deque

EMPTY = 0
RED = -1
BLUE = 1

DIRECTIONS = [(-1,0), (1,0), (0,-1), (0,1), (-1,1), (1,-1)]

class HexGame:
    def __init__(self, size=11, swap_rule=False):
        self.size = size
        self.board = [[EMPTY for _ in range(size)] for _ in range(size)]
        self.current_player = random.choice([RED, BLUE])
        self.move_count = 0
        self.swap_rule = swap_rule
        self.swap_used = False

        self.Pot = [[[20000,20000,20000,20000] for _ in range(size)] for __ in range(size)]
        self.Bridge = [[[0,0,0,0] for _ in range(size)] for __ in range(size)]

    def is_valid_move(self, r, c):
        return 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] == EMPTY

    def make_move(self, r, c):
        if not self.is_valid_move(r, c):
            return False
        self.board[r][c] = self.current_player
        self.move_count += 1
        self.current_player = -self.current_player
        return True

    def check_winner(self):
        if self.has_path(RED):
            return RED
        if self.has_path(BLUE):
            return BLUE
        return None

    def has_path(self, player):
        visited = [[False]*self.size for _ in range(self.size)]
        queue = deque()
        if player == RED:
            for col in range(self.size):
                if self.board[0][col] == RED:
                    queue.append((0, col))
                    visited[0][col] = True
            while queue:
                r, c = queue.popleft()
                if r == self.size - 1:
                    return True
                for nr, nc in self.get_neighbors(r, c):
                    if self.board[nr][nc] == RED and not visited[nr][nc]:
                        visited[nr][nc] = True
                        queue.append((nr, nc))
            return False
        else:
            for row in range(self.size):
                if self.board[row][0] == BLUE:
                    queue.append((row, 0))
                    visited[row][0] = True
            while queue:
                r, c = queue.popleft()
                if c == self.size - 1:
                    return True
                for nr, nc in self.get_neighbors(r, c):
                    if self.board[nr][nc] == BLUE and not visited[nr][nc]:
                        visited[nr][nc] = True
                        queue.append((nr, nc))
            return False

    def get_neighbors(self, r, c):
        for dr, dc in DIRECTIONS:
            nr, nc = r+dr, c+dc
            if 0 <= nr < self.size and 0 <= nc < self.size:
                yield nr, nc

    def is_full(self):
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] == EMPTY:
                    return False
        return True

    def compute_potentials(self, level=2):
        for ii in range(self.size):
            for jj in range(self.size):
                self.Pot[ii][jj] = [20000,20000,20000,20000]
                self.Bridge[ii][jj] = [0,0,0,0]

        for ii in range(self.size):
            if self.board[ii][0] == EMPTY:
                self.Pot[ii][0][0] = 128
            elif self.board[ii][0] == BLUE:
                self.Pot[ii][0][0] = 0

            if self.board[ii][self.size-1] == EMPTY:
                self.Pot[ii][self.size-1][1] = 128
            elif self.board[ii][self.size-1] == BLUE:
                self.Pot[ii][self.size-1][1] = 0

        for jj in range(self.size):
            if self.board[0][jj] == EMPTY:
                self.Pot[0][jj][2] = 128
            elif self.board[0][jj] == RED:
                self.Pot[0][jj][2] = 0

            if self.board[self.size-1][jj] == EMPTY:
                self.Pot[self.size-1][jj][3] = 128
            elif self.board[self.size-1][jj] == RED:
                self.Pot[self.size-1][jj][3] = 0

        for _ in range(6):
            self.relax_potentials(RED, level)
            self.relax_potentials(BLUE, level)

    def relax_potentials(self, player, level):
        if player == RED:
            idxs = [2, 3]
            cc = RED
        else:
            idxs = [0, 1]
            cc = BLUE

        for _ in range(2):
            for ii in range(self.size):
                for jj in range(self.size):
                    if self.board[ii][jj] == -cc:
                        continue
                    current_vals = [self.Pot[ii][jj][k] for k in idxs]
                    best = min(current_vals)
                    for nr, nc in self.get_neighbors(ii, jj):
                        vals = [self.Pot[nr][nc][k] for k in idxs]
                        if self.board[ii][jj] == cc:
                            candidate = min(vals)
                            if candidate < best:
                                best = candidate
                        else:
                            candidate = min(vals) + 64
                            if candidate < best:
                                best = candidate
                    for k in idxs:
                        if best < self.Pot[ii][jj][k]:
                            self.Pot[ii][jj][k] = best

    def select_best_move(self, level=2):
        self.compute_potentials(level)
        
        theCol = self.current_player
        if theCol == BLUE:
            idxs = [0, 1]
        else:
            idxs = [2, 3]

        best_score = float('inf')
        best_move = None
        for ii in range(self.size):
            for jj in range(self.size):
                if self.board[ii][jj] == EMPTY:
                    pot_sum = sum(self.Pot[ii][jj][k] for k in idxs)
                    score = pot_sum + random.random()*0.1
                    if score < best_score:
                        best_score = score
                        best_move = (ii, jj)
        return best_move


def save_board_to_csv(board, winner, filename="games.csv"):
    flattened = []
    size = len(board)
    for r in range(size):
        for c in range(size):
            flattened.append(board[r][c])
    flattened.append(winner)

    with open(filename, mode='a', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(flattened)

def simulate_one_game(size=11, swap_rule=False, level=2, moves_before_end=2, filename="board.csv"):
    game = HexGame(size=size, swap_rule=swap_rule)
    history_of_boards = []

    while True:
        winner = game.check_winner()
        if winner is not None or game.is_full():
            if winner is not None and game.move_count >= moves_before_end:
                state_to_save = history_of_boards[game.move_count - moves_before_end - 1]
                save_board_to_csv(state_to_save, winner, filename=filename)
            return winner, game.board

        move = game.select_best_move(level=level)
        if move is None:
            winner = game.check_winner()
            if winner is not None and game.move_count >= moves_before_end:
                state_to_save = history_of_boards[game.move_count - moves_before_end - 1]
                save_board_to_csv(state_to_save, winner, filename=filename)
            return winner, game.board

        game.make_move(*move)
        history_of_boards.append(copy.deepcopy(game.board))


def simulate_many_games(num_games=1000, size=3, swap_rule=True, level=3, moves_before_end=2, filename="board.csv"):
    print(f"Simulating {num_games} games of size {size}.")
    results = {RED:0, BLUE:0, None:0}
    for i in range(num_games):
        w, final_board = simulate_one_game(size=size, swap_rule=swap_rule, level=level, moves_before_end=moves_before_end, filename=filename)
        results[w] += 1
        if (i+1) % 100 == 0:
            print(f"{i+1} games simulated...")

    print("Simulation complete.")
    print(f"Total games: {num_games}")
    print(f"Red wins: {results[RED]}")
    print(f"Blue wins: {results[BLUE]}")
    print(f"No winner: {results[None]}")

if __name__ == "__main__":
    simulate_many_games(num_games=6000, size=11, swap_rule=True, level=5, moves_before_end=4, filename="11x11-4.csv")
