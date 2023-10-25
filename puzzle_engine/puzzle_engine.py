import subprocess
from subprocess import PIPE, Popen
import yaml
import numpy as np
import os

class PuzzleEngine:
    def __init__(self, config, puzzles):
        self.config = config
        self.puzzles = puzzles
        self.process = None
        self.engineconfig = None

    def run_tests(self):
        #Run the necessary tests

        #Start a new process
        with open(self.config, "r") as stream:
            try:
                self.engineconfig = yaml.safe_load(stream)
                # print(self.sensitive_config)
            except yaml.YAMLError as exc:
                raise ValueError(exc)

        #TODO: Add loop to run all tests
        #TODO: Add logging functionality to save results to file
        
        #Start the external engine
        self.process = subprocess.Popen(self.engineconfig['command'], stdin=PIPE, stdout=PIPE, 
                                            cwd=self.engineconfig['cwdpath'], encoding="utf8")

        #Used for testing functionality
        output = []

        #set boardsize for game
        self.set_boardsize()

        #load in specified sgf file
        self.load_sgf("TestGame.sgf")

        #process SGF file for internal use
        board, next_player = self.parse_sgf("TestGame.sgf")
        print(board)
        print("Next Player: ", next_player)

        #generate move for player B and save result
        #TODO: Add method to handle genmove command
        self.process.stdin.write('genmove B\n')
        self.process.stdin.flush()
        genmove_response = self.process.stdout.readline()
        response = "Made Move: " + genmove_response
        output.append(response)
        self.process.stdout.readline()


        #display new board
        self.process.stdin.write('showboard\n')
        self.process.stdin.flush()
        self.process.stdout.readline() #skip a line of output
        #read in a 7x7 board and save it
        text=""
        for i in range(8):
            text = self.process.stdout.readline()
            output.append(text)

        #quit katago
        self.process.stdin.write('quit\n')
        self.process.stdin.flush()
        response = "Quit response: " + self.process.stdout.readline()

        #print results
        print("\n--RESULTS--\n")  
        for i in range(len(output)):
            print(output[i].replace("\n", ""))



    def set_boardsize(self):
        cmd = "boardsize " + str(self.engineconfig['boardsize']) + "\n"
        self.process.stdin.write(cmd)
        self.process.stdin.flush()
        #skip lines of output from boardsize (Don't need)
        self.process.stdout.readline() 
        self.process.stdout.readline()

    
    def load_sgf(self, puzzle_name):
        #Used to initialize board state so engine can solve a puzzle
        loadcmd = 'loadsgf ' + self.engineconfig['puzzlespath'] + puzzle_name + '\n'
        self.process.stdin.write(loadcmd)
        self.process.stdin.flush()
        #skip unwanted lines of output
        self.process.stdout.readline()
        self.process.stdout.readline()


    def parse_sgf(self, puzzle_name):
        """
        Read in the given puzzle and get list of moves
        Input: 
            - Name of the puzzle to load 
        Returns: 
            - Matrix representation of board
            - Next player 
        """
        #Get SGF file as text
        filepath = self.engineconfig['puzzlespath'] + puzzle_name
        with open(filepath) as f:
            temp = f.read()
        temp = temp.replace("(", "").replace(")", "")

        #Get a list of moves from the SGF file
        sgf_info = temp.split(';')
        sgf_info = sgf_info[2:]
        moves = []
        for elt in sgf_info:
            parsed_move = elt.split("[")
            parsed_move[1] = parsed_move[1].replace("]", "")
            moves.append(parsed_move)
        #Call method to get matrix representation of board and next player
        return self.sgf_to_matrix(moves, self.engineconfig['boardsize'])


    def sgf_to_matrix(self, moves, size):
        board = np.zeros((int(size), int(size)))
        next_player = ""
        for elt in moves:
            row, col = self.sgf_vertex_to_idx(elt[1])
            if elt[0] == 'B':
                board[row][col] = 1
                next_player = 'W'
            else:
                board[row][col] = -1
                next_player = 'B'
        return board, next_player


    def sgf_vertex_to_idx(self, v):
        letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j'
                    'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's']
        col = letters.index(v[0])
        row = letters.index(v[1])
        return row, col


    def save_test_result(self):
        #Do Nothing yet
        print()

"""test1 = PuzzleEngine("katago_config.yaml", '/Users/blake/Research/Puzzle-Engine/puzzle_files/TestGame.sgf\n')
test1.run_tests()"""

#print(os.getcwd())