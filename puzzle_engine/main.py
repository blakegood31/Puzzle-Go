import yaml
from puzzle_engine import PuzzleEngine
import os


def load_config(filename):
    """
    Method to load in configuration files (yaml format)
    """
    with open(filename, "r") as stream:
        try:
            config = yaml.safe_load(stream)
            return config
        except yaml.YAMLError as exc:
            raise ValueError(exc)

if __name__ == '__main__':
    #Load in main config file
    config = load_config("main_config.yaml")

    #Check if necessary information for the engines listed in main config exist,
    #and add them to a dictionary of engines to be tested
    listed_engines = config['engines']
    engines = {}
    for engine in listed_engines:
        engine_path = config["engines_path"] + engine + "/" 
        if os.path.exists(engine_path):
            print("Found path for -->", engine)
        else:
            print("No folder found for -->", engine, "<-- Please add one to test it.")
        
        config_path = engine_path + engine + "_config.yaml"
        if os.path.exists(config_path):
            engines[engine] = {}
            engines[engine]["folder_path"] = engine_path
            engines[engine]["config_path"] = config_path
        else:
            print("No config file exists for -->", engine, "<-- will not add to tested engines." )


    #Gather all the puzzles to test the engines on
    puzzle_folders = os.listdir(config["puzzles_path"])
    print(puzzle_folders)
    puzzles = []
    for lvl in puzzle_folders:
        path = config["puzzles_path"] + lvl + "/"
        found = os.listdir(path)
        for elt in found:
            pname = path + elt
            puzzles.append(pname)

    #If needed, get the necessary rotations of the given SGF puzzles
    if config["rotate_puzzles"]:
        aux = PuzzleEngine(config, puzzles, None)
        rotated_puzzles = []
        for puzzle in puzzles:
            if "deg" not in puzzle:
                moves, answer, curr_player, prev_player = aux.parse_sgf(puzzle)
                gtp_board = aux.sgf_to_matrix(moves)
                new_puzzles = aux.get_sgf_rotations(gtp_board, moves, puzzle)
                if len(new_puzzles) > 0:
                    rotated_puzzles.extend(new_puzzles)
        puzzles.extend(rotated_puzzles)

    #Run the tests for each engine
    for engine in engines:
        engine_config = load_config(engines[engine]["config_path"])
        puzzleEngine = PuzzleEngine(config, puzzles, engine_config)
        puzzleEngine.run_tests()