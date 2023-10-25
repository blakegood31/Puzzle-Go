import yaml
from puzzle_engine import PuzzleEngine


if __name__ == '__main__':
    with open("main_config.yaml", "r") as stream:
        try:
            config = yaml.safe_load(stream)
            # print(self.sensitive_config)
        except yaml.YAMLError as exc:
            raise ValueError(exc)

    #TODO: Add functionality to run tests for all specified engines
    test1 = PuzzleEngine("katago_config.yaml", '/Users/blake/Research/Puzzle-Engine/puzzle_files/TestGame.sgf\n')
    test1.run_tests()
