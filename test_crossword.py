from crossword import Crossword
from timer import Timer
from construction_algorithm import *

test_grid = [
             ['.', ' ', ' ', ' ', '.'],
             [' ', ' ', ' ', ' ', ' '],
             [' ', ' ', ' ', ' ', ' '],
             [' ', ' ', ' ', ' ', ' '],
             ['.', ' ', ' ', ' ', '.']
            ]

wordlist_file = 'sample_word_list'
if IntelligentLookahead.construct(5, 5, test_grid, wordlist_file):
    print("SUCCESS")
else:
    print("FAILED")

Timer.outputAll()
