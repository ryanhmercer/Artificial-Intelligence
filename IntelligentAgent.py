#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: ryanhuang
uni: rh3129
"""

import math
import time
import random
from BaseAI import BaseAI

class IntelligentAgent(BaseAI):
    
    def __init__(self):
        self.maxDepth = 5
        self.timeLimit = 0.18
        super(IntelligentAgent, self).__init__()
        
    def getMove(self, grid):
        self.startTime = time.process_time()
        move, _ = self.maximize(grid, float('-inf'), float('inf'), 0)
        return move 

    
    def minimize(self, state, alpha, beta, depth=0):
        if self.terminal(state) or time.process_time() - self.startTime > self.timeLimit or depth >= self.maxDepth:
            return None, self.h(state)
        
        minChild = None
        minUtility = float('inf')
        possibleTiles = state.getAvailableCells();
        
        for tile in possibleTiles:
            # call maximize twice, state with 2 added and state with 4 added
            # this will return two utilty values so take the weighted avg of these 2
            # the weights are 0.9 and 0.1
            stateWithTwo = state.clone()
            stateWithTwo.insertTile(tile, 2)
            _, utility2 = self.maximize(stateWithTwo, alpha, beta, depth + 1)
            
            stateWithFour = state.clone()
            stateWithFour.insertTile(tile, 4)
            _, utility4 = self.maximize(stateWithFour, alpha, beta, depth + 1)

            if time.process_time() - self.startTime >= self.timeLimit:
                break
            
            avgUtil = 0.9 * utility2 + 0.1 * utility4
            
            #check if util is min util so far
            if avgUtil < minUtility:
                minUtility = avgUtil
                minChild = tile
            
            if minUtility <= alpha:
                break
            
            if minUtility < beta:
                beta = minUtility
        
        return minChild, minUtility
    
    def maximize(self, state, alpha, beta, depth=0):
        if self.terminal(state) or time.process_time() - self.startTime > self.timeLimit or depth >= self.maxDepth:
            return None, self.h(state)
        
        maxChild = None
        maxUtility = float('-inf')
        
        possibleMoves = state.getAvailableMoves();
        
        for move, newState in possibleMoves:
            # utility calculated by minimize(state with  move)
            # check if util is better than max util so far
            _, utility = self.minimize(newState, alpha, beta, depth+1)
            
            if time.process_time() - self.startTime >= self.timeLimit:
                break
            
            if utility > maxUtility:
                maxUtility = utility
                maxChild = move
            
            if maxUtility >= beta:
                break
            
            if maxUtility > alpha:
                alpha = maxUtility
                
        return maxChild, maxUtility
    
   
    def terminal(self, state):
        # exhausted time limit
        # or have gone too far in the tree
        if state.canMove() == False:
            return True
        return False
    
    def calculate_monotonicity(self, grid):
        w4 = 8
        w3 = 4
        w2 = 2
        w1 = 1
        
        weights = [[[w4, w3, w2, w1],
                   [w3, -1, -1, -1],
                   [w2, -1, -1, -1],
                   [w1, -1, -1, -1]],
                   
                   [[w1, w2, w3, w4],
                    [-1, -1, -1, w3],
                    [-1, -1, -1, w2],
                    [-1, -1, -1, w1]],
                   
                   [[w1, -1, -1, -1],
                    [w2, -1, -1, -1],
                    [w3, -1, -1, -1],
                    [w4, w3, w2, w1]],
                   
                   [[-1, -1, -1, w1],
                    [-1, -1, -1, w2],
                    [-1, -1, -1, w3],
                    [w1, w2, w3, w4]]]
        
        # We initialize the monotonicity score for all directions
        monotonicity = [0, 0, 0, 0]
    
        # Now we iterate over all the directions
        for d in range(4):
            for x in range(4):
                for y in range(4):
                    if weights[d][x][y] != -1:  # We only consider the tiles that are not marked as -1
                        value = math.log2(grid.map[x][y]) if grid.map[x][y] else 0
                        monotonicity[d] += value * weights[d][x][y]
    
        total_monotonicity = max(monotonicity)
        
        return total_monotonicity
        
                   
    
    def calculate_empty_cells(self, grid):
        return len(grid.getAvailableCells())
    
    def calculate_possible_merges(self, grid):
        merge_count = 0
        for x in range(4):
            # Only go up to the second to last element for horizontal check
            for y in range(3):  
                if grid.map[x][y] == grid.map[x][y + 1] and grid.map[x][y] != 0:
                    merge_count += 1
        for y in range(4):
            # Only go up to the second to last element for vertical check
            for x in range(3):  
                if grid.map[x][y] == grid.map[x + 1][y] and grid.map[x][y] != 0:
                    merge_count += 1
        return merge_count
    

    def h(self, grid):
        empty_cells = self.calculate_empty_cells(grid)
        monotonicity = self.calculate_monotonicity(grid)
        merges = self.calculate_possible_merges(grid)
        #smoothness = self.calculate_smoothness(grid)
        # Weight factors
        weight_empty = 0.6
        weight_mono = 0.13
        weight_merge = 0.27
    
        # Calculate heuristic by combining empty cells count and monotonicity
        heuristic_value = weight_mono * monotonicity + weight_empty * empty_cells + weight_merge * merges
        return heuristic_value