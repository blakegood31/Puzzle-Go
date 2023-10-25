""" 
This file is used to show how the process works and to 
test functionality before adding features to puzzle_engine.py
"""


import subprocess
from subprocess import PIPE, Popen
import os
from puzzle_engine.puzzle_engine import PuzzleEngine


print(os.getcwd())
#start katago
p1 = subprocess.Popen(["katago", "gtp", "-model", "/opt/homebrew/Cellar/katago/1.13.2/share/katago/g170e-b20c256x2-s5303129600-d1228401921.bin.gz", "-config", "gtp_example.cfg"], 
                        stdin=PIPE, stdout=PIPE, cwd="/opt/homebrew/Cellar/katago/1.13.2/share/katago/configs", encoding="utf8")

#Used to store output from testing functionality
output = []

#set boardsize to 7
p1.stdin.write('boardsize 7\n')
p1.stdin.flush()
#skip lines of output from boardsize (Don't care about these)
p1.stdout.readline() 
p1.stdout.readline()

#load in specified sgf file
loadcmd = 'loadsgf ' + '/Users/blake/Research/Puzzle-Engine/puzzle_files/TestGame.sgf\n'
output.append(loadcmd)
p1.stdin.write(loadcmd)
p1.stdin.flush()
response = "loadsgf response: " + p1.stdout.readline()
output.append(response)
p1.stdout.readline() #Read past unneeded output

#generate move for player B and save result
p1.stdin.write('genmove B\n')
p1.stdin.flush()
genmove_response = p1.stdout.readline()
response = "Made Move: " + genmove_response
output.append(response)
p1.stdout.readline()


#display new board
p1.stdin.write('showboard\n')
p1.stdin.flush()
p1.stdout.readline() #skip a line of output
text=""
#read in a 7x7 board and save it
for i in range(8):
    text = p1.stdout.readline()
    output.append(text)

#quit katago
p1.stdin.write('quit\n')
p1.stdin.flush()
response = "Quit response: " + p1.stdout.readline()


print("\n--RESULTS--\n")
#print results
for i in range(len(output)):
    print(output[i].replace("\n", ""))


#Read in the given puzzle and get list of moves
with open("/Users/blake/Research/Puzzle-Engine/puzzle_files/TestGame.sgf") as f:
    temp = f.read()
temp = temp.replace("(", "").replace(")", "")
print(temp)

#Parse sgf file contents to get moves
segments = temp.split(';')
segments = segments[2:]
newMove = "B[" + genmove_response[2:4] + "]"
segments.append(newMove)
for elt in segments:
    move = elt.split("[")
    move[1] = move[1].replace("]", "")
    print(move)
