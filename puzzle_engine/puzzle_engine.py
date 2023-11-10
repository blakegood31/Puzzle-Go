import subprocess
from subprocess import PIPE, Popen
import yaml
import numpy as np
import os
from matplotlib import pyplot as plt

class PuzzleEngine:
    def __init__(self, config, puzzles, engine_config):
        self.config = config
        self.puzzles = puzzles
        self.process = None
        self.engineconfig = engine_config
        self.board = np.zeros((int(self.config['boardsize']), int(self.config['boardsize'])))

    def run_tests(self):
        #Run the necessary tests
        for puzzle in self.puzzles:
            for _ in range(self.config["tests_per_puzzle"]):
                #Start the external engine
                self.process = subprocess.Popen(self.engineconfig['command'], stdin=PIPE, stdout=PIPE, 
                                                    cwd=self.engineconfig['cwdpath'], encoding="utf8")

                #self.board = np.zeros((int(self.config['boardsize']), int(self.config['boardsize'])))
                
                #Used for testing functionality
                output = []

                #set boardsize for game
                self.boardsize_cmd()

                print("\nLog for: ", puzzle)
                #load in specified sgf file
                self.loadsgf_cmd(puzzle)

                #process SGF file for internal use
                moves, answer, curr_player, prev_player = self.parse_sgf(puzzle)
                output.append("\nProper Answer: ")
                output.append(answer)
                output.append("\nMoves in SGF: ")
                output.append(moves)
                #create matrix from SGF moves (stored in self.board)
                gtp_board = self.sgf_to_matrix(moves)


                #have engine generate move for the next player in the game and save result
                response, curr_player, prev_player = self.genmove_cmd(curr_player)
                engineMove = "Enging Made Move: " + response
                output.append(response)

                if len(answer) == 0:
                    ans_for_score = "gg"
                else:
                    ans_for_score = answer[1]
                
                self.score_engine(response, ans_for_score, puzzle)
                #update the matrix representation of the board with the new move
                self.update_board(response, prev_player)

                #display new board
                """self.process.stdin.write('showboard\n')
                self.process.stdin.flush()
                self.process.stdout.readline() #skip a line of output
                #read in a 7x7 board and save it
                text=""
                for i in range(8):
                    text = self.process.stdout.readline()
                    output.append(text)"""

                #quit katago
                self.process.stdin.write('quit\n')
                self.process.stdin.flush()
                response = "Quit response: " + self.process.stdout.readline()

                #print results
                print("\n--RESULTS--\n")  
                """for i in range(len(output)):
                    print(output[i].replace("\n", ""))"""
                for elt in output:
                    print(elt)
                
                print(self.board)
                print("Next Player: ", curr_player)
                print("Previous Player: ", prev_player)

                print("\n\n\n\n\n\n-------------------------\n\n\n\n\n")

        moves = []
        rewards = []
        with open("/Users/blake/Research/Puzzle-Go/puzzle_logs/Katago/Beginner_Exercise1V2_logs/Beginner_Exercise1V2_scores.txt") as f:
            scores = f.readlines()
            for s in scores:
                parsed = s.split(',')
                if parsed[0] in moves:
                    idx = moves.index(parsed[0])
                    rewards[idx] = rewards[idx] + 1
                else:
                    moves.append(parsed[0])
                    rewards.append(1)
            
        fig = plt.figure(figsize = (10, 5))
        plt.bar(moves, rewards, color='green', width=0.4)
        plt.show()



    def boardsize_cmd(self):
        """
        Method to send a 'boardsize' command to the running engine.
            - This will set the engine's board size to whatever is 
               specified in 'main_config.yaml'

        Input/Output: None
        """
        cmd = "boardsize " + str(self.config['boardsize']) + "\n"
        self.process.stdin.write(cmd)
        self.process.stdin.flush()
        #skip lines of output from boardsize (Don't need)
        self.process.stdout.readline() 
        self.process.stdout.readline()

    
    def loadsgf_cmd(self, puzzle_name):
        """
        Method to send a 'loadsgf' command to the running engine. 
            - This will set the engine's board state to match that 
               of the puzzle given in SGF format
        
        Input: The name of the puzzle to be loaded 
        Output: None
        """
        #Used to initialize board state so engine can solve a puzzle
        loadcmd = 'loadsgf ' + puzzle_name + '\n'
        self.process.stdin.write(loadcmd)
        self.process.stdin.flush()
        #skip unwanted lines of output
        self.process.stdout.readline()
        self.process.stdout.readline()


    def genmove_cmd(self, player):
        """
        Method to send a 'genmove' command to the running engine 
        and read the result. 
            - This tells the engine generate a move and play it on the board.

        Input: The player to generate a move for, either B or W
        Output: The GTP vertex of the engine-generated move, and the 
                next player in the game (opponent of the input player)
        """
        genmovecmd = "genmove " + player + "\n"
        self.process.stdin.write(genmovecmd)
        self.process.stdin.flush()
        genmove_response = self.process.stdout.readline()
        genmove_response = genmove_response[2:4]
        self.process.stdout.readline() #skip a line of output
        curr_player = "B" if player == "W" else "W"
        prev_player = player

        letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j'
                    'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's']
        try:
            genmove_response = genmove_response[0].lower() + letters[7-int(genmove_response[1])]
            
        except ValueError as e:
            genmove_response = genmove_response.lower()
            print("No switch needed")

        return genmove_response, curr_player, prev_player



    def parse_sgf(self, puzzle_name):
        """
        Read in the given puzzle in SGF format, parse the SGF file 
        into list of moves, and return the matrix representation of the board 
        and the color of the next player (B or W)
        Input: 
            - Name of the puzzle to load 
        Returns: 
            - Matrix representation of board
            - Next player 
        """
        #Get SGF file as text
        filepath = puzzle_name
        with open(filepath) as f:
            temp = f.read()
        temp = temp.replace("(", "").replace(")", "")

        #Get a list of moves and puzzle answer from the SGF file
        sgf_info = temp.split(';')
        sgf_info = sgf_info[2:]
        moves = []
        ans = []
        for elt in sgf_info:
            if "C" in elt:
                finalElt = elt.split("C")
                elt = finalElt[0]

                raw_ans = finalElt[1].split(" ")[1]
                ans = raw_ans.split(",")
                ans[1] = ans[1].replace("]", "")        

            parsed_move = elt.split("[")
            parsed_move[1] = parsed_move[1].replace("]", "")
            moves.append(parsed_move)

        #get current/next player
        curr_player = "B" if moves[-1][0] == "W" else "W"
        prev_player = "B" if curr_player == "W" else "W"
        #return all information from SGF file
        return moves, ans, curr_player, prev_player


    def sgf_to_matrix(self, moves):
        """
        Method to make a numpy matrix from a parsed SGF file 

        Input: 
            - moves: A list of moves, where each move is a list ['Player', 'GTP vertex']
        
        Output: None, only updates (self.board)
        """
        gtp_board = np.array(['00' for _ in range(49)], dtype='a5').reshape(7,7)
        curr_player = ""
        for elt in moves:
            row, col = self.gtp_vertex_to_idx(elt[1])
            if elt[0] == 'B':
                self.board[row][col] = 1
                gtp_board[row][col] = elt[1]
                curr_player = 'W'
            else:
                self.board[row][col] = -1
                gtp_board[row][col] = elt[1]
                curr_player = 'B'

        return gtp_board

    def gtp_vertex_to_idx(self, v):
        """
        Method to convert gtp vertices of letters in the form 'column''row'
        into indices to be used with a matrix
        
        Input: a vertex 'v'

        Output: matrix indices row, col
        """
        letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j'
                    'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's']
        try:
            col = letters.index(v[0].lower())
        except ValueError as e:
            col = int(v[0])
        try:
            row = letters.index(v[1])
        except ValueError as e:
            row = int(self.config["boardsize"]) - int(v[1])
        return row, col

    def update_board(self, v, player):
        """
        Method to update the matrix representation of the board 
        after a new move is played 

        Input: a GTP vertex 
        Output: No return, only updates self.board
        """
        row, col = self.gtp_vertex_to_idx(v)
        print(f"\n\nRow:{row}  Col:{col}\n\n")
        self.board[row][col] = 1 if player == "B" else -1
        
    def score_engine(self, move_played, answer, puzzle):
        """
        Method to score the engine's answer to a puzzle 

        Input:
            - move_played: the sgf vertex of the move that the engine played
            - answer: the correct answer to the puzzle (optimal move)
            - puzzle: the name of the SGF file containing the puzzle 

        Output:
            - None, just score the move played and save the score to a log file. 
        """
        if move_played == answer:
            score = 1
        else:
            score = -1

        self.save_puzzle_score(score, puzzle, move_played)
        

    def get_sgf_rotations(self, move_board, moves, puzzle):
        """
        This is a method to get multiple rotations of a given SGF file. It 
        is meant to ensure a more thorough testing of the chosen models, but 
        this can be turned off in main_config.yaml. 

        Inputs: 
            - move_board: a 2D numpy matrix containing the gtp vertices in their 
                            corresponding locations in the matrix 
            - moves: an array of each move in the sgf file, in the form "PLAYER", "vertex"
            - puzzle: the "root" SGF puzzle to make rotations of 
        
        Returns: 
            A list 'new_puzzles', containing the filepaths of the new rotated SGF 
            files created. This also saves the SGF files under the corresponding 
            'puzzle_files' directory
        """
        
        rotations = [90, 180, 270]
        check_rots = [90, 180, 270]

        split_puzzle = puzzle.split("/")
        path_elements = split_puzzle[:-1]
        sgf_path = "/".join(path_elements) + "/"
        puzzle_name = split_puzzle[-1]
        tag = puzzle_name.replace(".sgf", "")

        for rot in check_rots:
            new_puzzle_name = tag + "_" + str(rot) + "deg.sgf"
            new_puzzle_path = os.path.join(sgf_path, new_puzzle_name)
            if os.path.exists(new_puzzle_path):
                print("DONT DO ANYTHING FOR :", new_puzzle_path)
                try:
                    rotations.remove(rot)
                except:
                    print(f'Rotation {rot} already removed')
            else: 
                print("WILL MAKE NEW PUZZLE FOR: ", new_puzzle_path)
        
        move_order = []
        for m in moves:
            move_order.append(m[1])

        new_rot = np.ndarray.copy(move_board)
        new_puzzles = []
        for i in range(len(rotations)):
            new_vertices = []
            new_rot = np.rot90(new_rot)
            cp = "B"
            for m in move_order:
                result = list(zip(*np.where(new_rot == bytes(m, 'utf-8'))))[0]
                row, col = result[0], result[1]
                v = self.idx_to_sgf_vertex(row, col)
                new_sgf_v = ";" + cp + "[" + v + "]"
                new_vertices.append(new_sgf_v)
                cp = "W" if cp == "B" else "B"
            new_puzzles.append(self.make_rotated_sgf(puzzle, rotations[i], new_vertices))
        return new_puzzles

    def idx_to_sgf_vertex(self, row, col):
        """
        This is a method to get the gtp equivalent of a given (row, column) index 
        in a 2D matrix. Used as a helper method for getting SGF rotations 

        Inputs: row, col -- matrix indices to be translated to a gtp vertex

        Returns: gtp_vertex -- the gtp equivalent of the given (row, col)
        """
        letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j'
                'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's']

        gtp_vertex = letters[col] + letters[row]
        return gtp_vertex


    def make_rotated_sgf(self, puzzle, rot, vertices):
        """
        This is a method used to save a new SGF file of a rotated board, 
        keeping the same move order and configuration settings as the 
        original file. 

        Input: 
            - puzzle: the file path of the original SGF file being rotated
            - rot: a number 90, 180, or 270 used for the new file name 
            - vertices: a list of GTP vertices to be written to the new SGF file 

        Returns: 
            - new_puzzle_path: the path of the new SGF file that has been saved in the 
                                proper directory under 'puzzle_files'
        """

        #Get SGF file as text
        split_puzzle = puzzle.split("/")
        puzzle_path = split_puzzle[:-1]
        path = "/".join(puzzle_path) + "/"

        with open(puzzle) as f:
            temp = f.read()

        sgf_info = temp.split(';')
        end = None
        if 'C' in sgf_info[-1]:
            end = "C" + sgf_info[-1].split("C")[-1]

        split_puzzle = puzzle.split("/")
        path_elements = split_puzzle[:-1]
        sgf_path = "/".join(path_elements) + "/"
        puzzle_name = split_puzzle[-1]
        tag = puzzle_name.replace(".sgf", "")
        new_puzzle_name = tag + "_" + str(rot) + "deg.sgf"

        new_puzzle_path = os.path.join(sgf_path, new_puzzle_name)
        print("MAKING NEW SGF FOR: ", new_puzzle_path)
        if not os.path.isfile(new_puzzle_path):
            sgf = open(new_puzzle_path, 'w')
            sgf.close()

        sgf = open(new_puzzle_path, 'a')
        header = sgf_info[0] + ";" + sgf_info[1]
        sgf.write(header)

        for v in vertices:
            sgf.write(v)
            
        if end is not None:
            sgf.write(end)
        else:
            end = ")"
            sgf.write(end)
        sgf.close()

        return new_puzzle_path





    def save_puzzle_score(self, score, puzzle, move_played):
        """
        Method to log scores from each test of an engine solving a puzzle

        Input: 
            - score: the score from solving the puzzle (1 for correct, -1 for incorrect)
            - puzzle: the name of the sgf puzzle being solved

        Output: 
            - None, just append new result to a file "puzzleName_logs.txt"
        """
        raw_puzzle_name = puzzle.split("/")[-1]
        temp = raw_puzzle_name.split("_")
        if len(temp) > 2:
            folder_name = temp[0] + "_" + temp[1] + "_logs"
        else:
            folder_name = raw_puzzle_name.replace(".sgf", "_logs")
        log_path = os.path.join(self.config["puzzle_logs_path"], self.engineconfig["name"], folder_name)
        
        if not os.path.exists(log_path):
            os.makedirs(log_path)

        filename = raw_puzzle_name.replace(".sgf", "_scores.txt")
        score_file = os.path.join(log_path, filename)
        if not os.path.isfile(score_file):
            log = open(score_file, 'w')
            log.close()
        log = open(score_file, 'a')
        score_info = move_played + "," + str(score) 
        log.write(score_info + "\n")
        log.close()
        

    def save_test_result(self):
        #Do Nothing yet
        print()
