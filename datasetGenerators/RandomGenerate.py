# --- ## ---
# Code summerized by ChatGPT:
# This code simulates Hex games on a given board size, ensuring a balanced dataset of outcomes. 
# It randomly places moves until a winner is determined, and records each game's final board and winner to a CSV file, 
# aiming for an even distribution of who starts and who wins.
# --- ## ---


import csv
import numpy as np
import random
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description="Generate Hex game CSV data.")
    
    # Optional flags
    parser.add_argument("--size", "-s", type=int, default=None, help="Board size.")
    parser.add_argument("--n_games", "-n", type=int, default=None, help="Number of games.")
    
    # Positional arguments (optional, if not using flags)
    parser.add_argument("positional_size", nargs="?", type=int, default=None,
                        help="Board size (positional, e.g. python3 gen.py 3 1000)")
    parser.add_argument("positional_n_games", nargs="?", type=int, default=None,
                        help="Number of games (positional, e.g. python3 gen.py 3 1000)")
    
    args = parser.parse_args()

    board_size = args.size if args.size is not None else (args.positional_size or 3)
    num_games  = args.n_games if args.n_games is not None else (args.positional_n_games or 1000)
    
    return board_size, num_games
    
board_size = 3

directions = [
    (-1, 0), (1, 0),
    (0, -1), (0, 1),
    (-1, 1), (1, -1) 
]

def generate_empty_board(board_size):
    """Return a board_size x board_size numpy array of zeros."""
    return np.zeros((board_size, board_size), dtype=int)

def generate_list_of_empty_cells(board_size):
    """Return a list of all cell coordinates in the board."""
    return [(i, j) for i in range(board_size) for j in range(board_size)]

def check_winner(board, position):
    """
    Checks if placing a piece at 'position' causes 'player' to win in a Hex board.
    
    player == -1 : Blue (connecting left-right)
    player == 1  : Red  (connecting top-bottom)
    """
    player = board[position]
    board_size = board.shape[0]
    
    stack = [position]
    visited = set()
    
    touches_left = touches_right = False
    touches_top = touches_bottom = False
    
    while stack:
        current = stack.pop()
        if current in visited:
            continue
        visited.add(current)
        
        x, y = current
        
        if player == -1:
            if y == 0:
                touches_left = True
            if y == board_size - 1:
                touches_right = True
        elif player == 1:
            if x == 0:
                touches_top = True
            if x == board_size - 1:
                touches_bottom = True
        
        if (player == -1 and touches_left and touches_right) or \
           (player == 1 and touches_top and touches_bottom):
            return True
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < board_size and 0 <= ny < board_size and board[nx, ny] == player:
                stack.append((nx, ny))
    
    return False

def print_board(board):
    board_size = board.shape[0]
    for i in range(board_size):
        leading = " " * (i * 3)
        row_str = []
        for cell in board[i]:
            if cell == 0:
                row_str.append(" 0 ")
            elif cell == 1:
                row_str.append(" R ")
            else:
                row_str.append(" B ")
        print(leading + " ".join(row_str))

def save_board_to_csv(board, winner, filename="game_results.csv"):
    flattened_board = board.flatten().tolist()
    flattened_board.append(winner)
    
    with open(filename, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(flattened_board)

def play_single_game(board_size):
    board = generate_empty_board(board_size)
    empty_cells = generate_list_of_empty_cells(board_size)
    
    start_player = random.choice([1, -1])
    current_player = start_player
    
    winner = None
    
    for _ in range(board_size * board_size):
        random_cell = random.choice(empty_cells)
        empty_cells.remove(random_cell)
        board[random_cell] = current_player
        
        if check_winner(board, random_cell):
            winner = current_player
            break
        
        current_player = -current_player
    
    if winner is None:
        winner = current_player
    
    return board, start_player, winner

def run_balanced_simulation(board_size, num_total_games=1000, output_csv="game_results.csv"):
    """
    Runs games until we have an equal distribution:
    - 25% Red starts, Red wins
    - 25% Red starts, Blue wins
    - 25% Blue starts, Blue wins
    - 25% Blue starts, Red wins
    """
    with open(output_csv, mode="w", newline="") as file:
        writer = csv.writer(file)
        pass
    
    target_per_scenario = num_total_games // 4  # e.g., 250 if total=1000
    
    scenario_counts = {
        (1, 1): 0,   # Red starts, Red wins
        (1, -1): 0,  # Red starts, Blue wins
        (-1, -1): 0, # Blue starts, Blue wins
        (-1, 1): 0   # Blue starts, Red wins
    }
    
    # Keep generating games until all 4 scenarios are filled
    while True:
        # If all scenarios are full, we break out
        if all(count >= target_per_scenario for count in scenario_counts.values()):
            break
        
        board, start_player, winner = play_single_game(board_size)
        
        # Identify the scenario
        scenario = (start_player, winner)
        
        # If this scenario still needs more games, record it
        if scenario_counts.get(scenario, 0) < target_per_scenario:
            scenario_counts[scenario] += 1
            save_board_to_csv(board, winner, filename=output_csv)
    
    # Just to verify the final distribution
    print("Final scenario counts:")
    print(f"Red starts, Red wins:  {scenario_counts[(1, 1)]}")
    print(f"Red starts, Blue wins: {scenario_counts[(1, -1)]}")
    print(f"Blue starts, Blue wins: {scenario_counts[(-1, -1)]}")
    print(f"Blue starts, Red wins:  {scenario_counts[(-1, 1)]}")

if __name__ == "__main__":
    board_size, num_games = parse_arguments()
    print(f"Board size: {board_size}, number of games: {num_games}")
    run_balanced_simulation(board_size, num_games, output_csv=f"size{board_size}_games{num_games}_A_balanced.csv")
