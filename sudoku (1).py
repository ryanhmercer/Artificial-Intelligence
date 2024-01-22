#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 15 22:52:17 2023

@author: ryanhuang
"""

#!/usr/bin/env python
#coding:utf-8

"""
Each sudoku board is represented as a dictionary with string keys and
int values.
e.g. my_board['A1'] = 8
"""
import sys
import time

ROW = "ABCDEFGHI"
COL = "123456789"


def print_board(board):
    """Helper function to print board in a square."""
    print("-----------------")
    for i in ROW:
        row = ''
        for j in COL:
            row += (str(board[i + j]) + " ")
        print(row)


def board_to_string(board):
    """Helper function to convert board dictionary to string for writing."""
    ordered_vals = []
    for r in ROW:
        for c in COL:
            ordered_vals.append(str(board[r + c]))
    return ''.join(ordered_vals)


# initially set the domains of the unassigned values in the board
# greatly reduces runtime if we do an initial prune rather than just have
# starting domains of 1-9
def initial_domain_pruning(board):
    domains = {key: {1,2,3,4,5,6,7,8,9} for key in board if board[key] == 0}

    for key in board:
        if board[key] != 0:
            num = board[key]
            
            row, col = key[0], key[1]

            # prune for row
            for r in ROW:
                if r + col in domains and num in domains[r + col]:
                    domains[r + col].remove(num)

            # prune for column
            for c in COL:
                if row + c in domains and num in domains[row + c]:
                    domains[row + c].remove(num)

            # prune for 3x3 box
            boxRowStart, boxColStart = 3 * (ROW.index(row) // 3), 3 * (COL.index(col) // 3)
            for r in range(3):
                for c in range(3):
                    boxKey = ROW[boxRowStart + r] + COL[boxColStart + c]
                    if boxKey in domains and num in domains[boxKey]:
                        domains[boxKey].remove(num)

    return domains

def backtracking(board):
    """Takes a board and returns solved board."""
    # TODO: implement this
    domains = initial_domain_pruning(board)      
    solved_board = backtrack(board, domains)
    return solved_board

def backtrack(assignment, domains):
    if(isComplete(assignment)):
        return assignment
    
    var = select_unassigned_var(assignment, domains)
    
    for num in domains[var]:
        if isValid(assignment, num, var):
            assignment[var] = num
            changes,originalDomain = forwardCheck(var, assignment, domains, num)
            if not emptyDomains(domains): 
                result = backtrack(assignment, domains)
                
                if result is not None:
                    return result
            
            assignment[var] = 0
            revertChange(changes, domains)
            domains[var] = originalDomain
            
    return None

def emptyDomains(domains):
    for key in domains:
        if len(domains[key]) == 0:
            return True
    return False


def revertChange(changes, domains):
    for key in changes:
        domains[key] |= changes[key] #set union to revert changes to domain
        
def forwardCheck(var, board, domains, num):
    row = var[0]
    col = var[1]
    changes = dict()
    originalDomain = domains[var].copy()
    
    #changing the domains in the other unassigned spots in the board, forawrd check
    
    # in the same row
    for c in COL:
        key = row + c
        if board[key] == 0:
            if num in domains[key]:
                if key not in changes:
                    changes[key] = set()
                changes[key].add(num)
                domains[key].discard(num)
    
    # in the same column
    for r in ROW:
         key = r + col
         if board[key] == 0:
             if num in domains[key]:
                 if key not in changes:
                     changes[key] = set()
                 changes[key].add(num)
                 domains[key].discard(num)
    
    # in the same box
    boxRow = 3 * (ROW.index(row) // 3)
    boxCol = 3 * (COL.index(col) // 3)
    for r in range(3):
        for c in range(3):
            key = ROW[boxRow + r] + COL[boxCol + c]
            if board[key] == 0:
                if key not in changes:
                    changes[key] = set()
                changes[key].add(num)
                domains[key].discard(num)
    # returning the changes made so they can be reverted later
    return changes, originalDomain
    

# uses minimum remaining value heuristic
def select_unassigned_var(board, domains):
    minimumVal = sys.maxsize
    minimumKey = ""
    for key in board:
        if board[key] == 0:
            if(len(domains[key]) < minimumVal):
                minimumVal = len(domains[key])
                minimumKey = key
    return minimumKey

def isValid(board, num, key):
    row = key[0]
    col = key[1]
    
    for r in ROW:
        if board[r + col] == num:
            return False
    
    for c in COL:
        if board[row + c] == num:
            return False
    
    boxRow = 3 * (ROW.index(row) // 3)
    boxCol = 3 * (COL.index(col) // 3)
    
    for r in range(3):
        for c in range(3):
            if board[ROW[boxRow + r] + COL[boxCol + c]] == num:
                return False
    
    return True

    

def isComplete(board):
    # if there are no 0's left on the board it is complete, no values left to assign
    for key in board:
        if(board[key] == 0):
            return False
    return True

def compute_statistics(times):
    n = len(times)
    mean = sum(times) / n
    squared_diffs = [(t - mean) ** 2 for t in times]
    variance = sum(squared_diffs) / n
    std_dev = variance ** 0.5

    return min(times), max(times), mean, std_dev


if __name__ == '__main__':
    times = []
    if len(sys.argv) > 1:
        
        # Running sudoku solver with one board $python3 sudoku.py <input_string>.
        print(sys.argv[1])
        # Parse boards to dict representation, scanning board L to R, Up to Down
        board = { ROW[r] + COL[c]: int(sys.argv[1][9*r+c])
                  for r in range(9) for c in range(9)}       
        
        start_time = time.time()
        solved_board = backtracking(board)
        end_time = time.time()
        
        runtime = end_time - start_time
        times.append(runtime)
        # Write board to file
        out_filename = 'output.txt'
        outfile = open(out_filename, "w")
        outfile.write(board_to_string(solved_board))
        outfile.write('\n')

    else:
        # Running sudoku solver for boards in sudokus_start.txt $python3 sudoku.py

        #  Read boards from source.
        src_filename = 'sudokus_start.txt'
        try:
            srcfile = open(src_filename, "r")
            sudoku_list = srcfile.read()
        except:
            print("Error reading the sudoku file %s" % src_filename)
            exit()

        # Setup output file
        out_filename = 'output.txt'
        outfile = open(out_filename, "w")

        # Solve each board using backtracking
        for line in sudoku_list.split("\n"):

            if len(line) < 9:
                continue

            # Parse boards to dict representation, scanning board L to R, Up to Down
            board = { ROW[r] + COL[c]: int(line[9*r+c])
                      for r in range(9) for c in range(9)}

            # Print starting board. TODO: Comment this out when timing runs.
            #print_board(board)

            # Solve with backtracking
            start_time = time.time()
            solved_board = backtracking(board)
            end_time = time.time()
            
            runtime = end_time - start_time
            times.append(runtime)

            # Print solved board. TODO: Comment this out when timing runs.
            #print_board(solved_board)

            # Write board to file
            outfile.write(board_to_string(solved_board))
            outfile.write('\n')

        #print("Finishing all boards in file.")
    
    #min_time, max_time, mean_time, std_dev_time = compute_statistics(times)
    #print("\nRunning Time Statistics:")
    #print(f"Min Time: {min_time:.4f} seconds")
    #print(f"Max Time: {max_time:.4f} seconds")
    #print(f"Mean Time: {mean_time:.4f} seconds")
    #print(f"Standard Deviation: {std_dev_time:.4f} seconds")