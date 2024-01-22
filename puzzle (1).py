from __future__ import division
from __future__ import print_function

import sys
import math
import time
import resource
import queue as Q


#### SKELETON CODE ####
## The Class that Represents the Puzzle
class PuzzleState(object):
    """
        The PuzzleState stores a board configuration and implements
        movement instructions to generate valid children.
    """
    def __init__(self, config, n, parent=None, action="Initial", cost=0, depth=0, heuristic=0):
        """
        :param config->List : Represents the n*n board, for e.g. [0,1,2,3,4,5,6,7,8] represents the goal state.
        :param n->int : Size of the board
        :param parent->PuzzleState
        :param action->string
        :param cost->int
        """
        if n*n != len(config) or n < 2:
            raise Exception("The length of config is not correct!")
        if set(config) != set(range(n*n)):
            raise Exception("Config contains invalid/duplicate entries : ", config)

        self.n        = n
        self.cost     = cost
        self.parent   = parent
        self.action   = action
        self.config   = config
        self.children = []
        self.depth    = depth

        # Get the index and (row, col) of empty block
        self.blank_index = self.config.index(0)
    
    def __lt__(self, other):
        cost = self.cost + self.heuristic
        otherCost = other.cost + other.heuristic
        
        if cost == otherCost:
            actionDict = {"Initial": 0, "Up": 1, "Down": 2, "Left": 3, "Right": 4}
            return actionDict[self.action] < actionDict[other.action]
        return cost < otherCost

    def display(self):
        """ Display this Puzzle state as a n*n board """
        for i in range(self.n):
            print(self.config[3*i : 3*(i+1)])

    def move_up(self):
        """ 
        Moves the blank tile one row up.
        :return a PuzzleState with the new configuration
        """
        if(self.blank_index - self.n >= 0):
            updated_config = self.config[:]
            temp = updated_config[self.blank_index]
            updated_config[self.blank_index] = updated_config[self.blank_index - self.n]
            updated_config[self.blank_index - self.n] = temp
            return PuzzleState(updated_config, self.n, parent=self, action="Up", cost=self.cost+1, depth=self.depth+1, heuristic=0)
        else: 
            return None
      
    def move_down(self):
        """
        Moves the blank tile one row down.
        :return a PuzzleState with the new configuration
        """
        if(self.blank_index + self.n <= len(self.config) - 1):
        
            updated_config = self.config[:]
            temp = updated_config[self.blank_index]
            updated_config[self.blank_index] = updated_config[self.blank_index + self.n]
            updated_config[self.blank_index + self.n] = temp
            return PuzzleState(updated_config, self.n, parent=self, action="Down", cost=self.cost+1, depth=self.depth+1, heuristic=0)
        
        else:
            return None
      
    def move_left(self):
        """
        Moves the blank tile one column to the left.
        :return a PuzzleState with the new configuration
        """
        if(self.blank_index % self.n != 0):
            updated_config = self.config[:]
            temp = updated_config[self.blank_index]
            updated_config[self.blank_index] = updated_config[self.blank_index - 1]
            updated_config[self.blank_index - 1] = temp
            return PuzzleState(updated_config, self.n, parent=self, action="Left", cost=self.cost+1, depth=self.depth+1, heuristic=0)

        else:
            return None

    def move_right(self):
        """
        Moves the blank tile one column to the right.
        :return a PuzzleState with the new configuration
        """
        if((self.blank_index + 1) % self.n != 0):
            updated_config = self.config[:]
            temp = updated_config[self.blank_index]
            updated_config[self.blank_index] = updated_config[self.blank_index + 1]
            updated_config[self.blank_index + 1] = temp
            return PuzzleState(updated_config, self.n, parent=self, action="Right", cost=self.cost+1, depth=self.depth+1, heuristic=0)
        else:
            return None
      
    def expand(self):
        """ Generate the child nodes of this node """
        
        # Node has already been expanded
        if len(self.children) != 0:
            return self.children
        
        # Add child nodes in order of UDLR
        children = [
            self.move_up(),
            self.move_down(),
            self.move_left(),
            self.move_right()]

        # Compose self.children of all non-None children states
        self.children = [state for state in children if state is not None]
        return self.children

# Function that Writes to output.txt

### Students need to change the method to have the corresponding parameters
def writeOutput(goal_state, nodesExpanded, maxDepth, maxRam, totalTime):
    ### Student Code Goes here
    path = get_path(goal_state)
    pathString = str(path)
    # always 8 decimal places
    maxRam = format(maxRam, '.8f')
    totalTime = format(totalTime, '.8f')
    with open("output.txt", "w") as file:
        file.write("path_to_goal: " + pathString + "\n")
        file.write("cost_of_path: " + str(goal_state.cost) + "\n")
        file.write("nodes_expanded: " + str(nodesExpanded) + "\n")
        file.write("search_depth: " + str(goal_state.depth) + "\n")
        file.write("max_search_depth: " + str(maxDepth) + "\n")
        file.write("running_time: " + totalTime + "\n")
        file.write("max_ram_usage: " + maxRam + "\n") # check if this is correct or not
        

def bfs_search(initial_state):
    """BFS search"""
    ### STUDENT CODE GOES HERE ###
    frontier = Q.Queue()
    frontier.put(initial_state)
    explored = set()
    frontierSet = set()
    frontierSet.add(tuple(initial_state.config))
    nodesExpanded = 0
    maxDepth = 0
    startRam =  resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    maxRam = 0
    
    while not frontier.empty():
        state = frontier.get()
        explored.add(tuple(state.config))
        
        if(state.depth > maxDepth):
            maxDepth = state.depth
            
        ram = (resource.getrusage(resource.RUSAGE_SELF).ru_maxrss - startRam)/(2**20)
        maxRam = max(ram, maxRam)
        
        if(test_goal(state)):
            return state, nodesExpanded, maxDepth, maxRam
        
        nodesExpanded += 1
        for child in state.expand():
            if tuple(child.config) not in explored and tuple(child.config) not in frontierSet:
                frontier.put(child)
                frontierSet.add(tuple(child.config))
                if(child.depth > maxDepth):
                    maxDepth = child.depth
    return None, nodesExpanded, maxDepth, maxRam

def get_path(goal_state):
    path = []
    curr = goal_state
    while curr.parent:
        path.append(curr.action)
        curr = curr.parent
    # reverse the path so I get it from start to goal instead of goal to start
    return path[::-1]
        
    
def dfs_search(initial_state):
    """DFS search"""
    ### STUDENT CODE GOES HERE ###
    frontier = Q.LifoQueue()
    frontier.put(initial_state)
    explored = set()
    frontierSet = set()
    frontierSet.add(tuple(initial_state.config))
    nodesExpanded = 0
    maxDepth = 0
    startRam =  resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    maxRam = 0
    
    while frontier:
        state = frontier.get()
        explored.add(tuple(state.config))
        
        if(state.depth > maxDepth):
            maxDepth = state.depth
            
        ram = (resource.getrusage(resource.RUSAGE_SELF).ru_maxrss - startRam)/(2**20)
        maxRam = max(ram, maxRam)
        
        if(test_goal(state)):
            return state, nodesExpanded, maxDepth, maxRam
        
        nodesExpanded += 1
        #reverse to make sure UDLR order when popped out of the stack
        for child in reversed(state.expand()):
            if tuple(child.config) not in explored and tuple(child.config) not in frontierSet:
                frontier.put(child)
                frontierSet.add(tuple(child.config))
                if(child.depth > maxDepth):
                    maxDepth = child.depth
    return None, nodesExpanded, maxDepth, maxRam

def A_star_search(initial_state):
    """A * search"""
    ### STUDENT CODE GOES HERE ###
    frontier = Q.PriorityQueue()
    initial_state.heuristic = calculate_total_cost(initial_state)
    frontier.put((initial_state.cost + initial_state.heuristic, initial_state))
    explored = set()
    frontierDict = {}
    frontierDict[tuple(initial_state.config)] = initial_state.cost + initial_state.heuristic
    nodesExpanded = 0
    maxDepth = 0
    startRam =  resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    maxRam = 0
    
    while not frontier.empty():
        priority, state = frontier.get()
        explored.add(tuple(state.config))
        
        if(state.depth > maxDepth):
            maxDepth = state.depth
            
        ram = (resource.getrusage(resource.RUSAGE_SELF).ru_maxrss - startRam)/(2**20)
        maxRam = max(ram, maxRam)
        
        if(test_goal(state)):
            return state, nodesExpanded, maxDepth, maxRam
        
        nodesExpanded += 1
        for child in state.expand():
            child.heuristic = calculate_total_cost(child)
            if tuple(child.config) not in explored and (tuple(child.config) not in frontierDict):
                frontier.put((child.cost + child.heuristic, child))
                frontierDict[tuple(child.config)] = child.cost + child.heuristic
                if child.depth > maxDepth:
                    maxDepth = child.depth
            elif (tuple(child.config) in frontierDict) and child.cost + child.heuristic < frontierDict[tuple(child.config)]:
                frontier.put((child.cost + child.heuristic, child))
                frontierDict[tuple(child.config)] = child.cost + child.heuristic
    return None, nodesExpanded, maxDepth, maxRam

def calculate_total_cost(state):
    """calculate the total estimated cost of a state"""
    ### STUDENT CODE GOES HERE ###
    sum = 0
    for i in range(len(state.config)):
        if state.config[i] != 0:
            sum += calculate_manhattan_dist(i, state.config[i], state.n)
    return sum

def calculate_manhattan_dist(idx, value, n):
    """calculate the manhattan distance of a tile"""
    ### STUDENT CODE GOES HERE ###
    goalRow = value // n
    goalCol = value % n
    
    currRow = idx // n
    currCol = idx % n
    return abs(goalRow - currRow) + abs(goalCol - currCol)

def test_goal(puzzle_state):
    """test the state is the goal state or not"""
    ### STUDENT CODE GOES HERE ###
    goal = list(range(0, puzzle_state.n*puzzle_state.n))
    if(puzzle_state.config == goal):
        return True
    else:
        return False

# Main Function that reads in Input and Runs corresponding Algorithm
def main():
    search_mode = sys.argv[1].lower()
    begin_state = sys.argv[2].split(",")
    begin_state = list(map(int, begin_state))
    board_size  = int(math.sqrt(len(begin_state)))
    hard_state  = PuzzleState(begin_state, board_size)
    start_time  = time.time()
    
    if   search_mode == "bfs": 
        goal_state, nodesExpanded, maxDepth, maxRam = bfs_search(hard_state)
        end_time = time.time()
        totalTime = end_time - start_time
        writeOutput(goal_state, nodesExpanded, maxDepth, maxRam, totalTime)
    elif search_mode == "dfs": 
        goal_state, nodesExpanded, maxDepth, maxRam = dfs_search(hard_state)
        end_time = time.time()
        totalTime = end_time - start_time
        writeOutput(goal_state, nodesExpanded, maxDepth, maxRam, totalTime)
    elif search_mode == "ast": 
        goal_state, nodesExpanded, maxDepth, maxRam = A_star_search(hard_state)
        end_time = time.time()
        totalTime = end_time - start_time
        writeOutput(goal_state, nodesExpanded, maxDepth, maxRam, totalTime)
    else: 
        print("Enter valid command arguments !")
    
    
    print("Program completed in %.3f second(s)"%(end_time-start_time))

if __name__ == '__main__':
    main()
