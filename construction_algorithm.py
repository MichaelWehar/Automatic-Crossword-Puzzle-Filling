from crossword import Crossword
from abc import ABC, abstractmethod
from word_reader import WordReader
from collections import deque, MutableSet
from random import choice
from timer import Timer
import time

# Get current pathname
import os
pathname = os.path.dirname(os.path.abspath(__file__)) + "/"

# Time limit for construction algorithm
MAX_TIME = 10

class ConstructionAlgorithm(ABC):
    @staticmethod
    @abstractmethod
    def construct(rows, cols, empty_grid, word_list, params = {}):
        pass

    @staticmethod
    @abstractmethod
    def checkValid(crossword, word_list):
        pass

    @staticmethod
    @abstractmethod
    def readWordList(word_list_file):
        pass

class BruteForceByChar(ConstructionAlgorithm):

    def _recBruteForceConstruct(curr_let_ind, alphabet, positions, xword, word_list_dict):
        if (curr_let_ind == len(positions)):
            if BruteForceByChar.checkValid(xword, word_list_dict):
                print("FOUND:")
                print(xword)
                return True
            else:
                return False
        for i in range(len(alphabet)):
            loc = positions[curr_let_ind]
            char = alphabet[i]
            r = loc[0]
            c = loc[1]
            xword.addLetter(r, c, char)
            if BruteForceByChar._recBruteForceConstruct(curr_let_ind + 1, alphabet, positions, xword, word_list_dict):
                return True
        return False

    """
    Very slow construction algorithm which takes every possible
    permutation of letters that could fit in the crossword and checks to see
    if all of the words are valid
    """
    def construct(rows, cols, empty_grid, word_list):

        # TODO change to whatever
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        xword = Crossword(rows, cols, empty_grid)

        word_list_dict = BruteForceByChar.readWordList(word_list)

        # first assign every empty cell to be the first character in the alphabet
        # save every cell that you assign in a list
        positions = []
        curr_grid = xword.getGrid()
        for r in range(rows):
            for c in range(cols):
                if (curr_grid[r][c] != '.'):
                    positions.append( (r,c) )
        return BruteForceByChar._recBruteForceConstruct(0, alphabet, positions, xword, word_list_dict)

    """
    Helper function to check if a given grid's words are in the word list
    Returns: Boolean True/False
    """
    def checkValid(xword, word_list_dict):
        for word in xword.getAcrosses():
            if word not in word_list_dict[len(word)]:
                return False
        for word in xword.getDowns():
            if word not in word_list_dict[len(word)]:
                return False
        return True

    def readWordList(word_list_file):
        # returns a dictionary with key as len and value as a set of words of that len
        word_list_dict = {}

        with open(pathname + 'wordlists/' + word_list_file + '.txt') as my_file:
            for line in my_file:
                line = line.strip()
                try:
                    word_list_dict[len(line)].append(line)
                except KeyError:
                    word_list_dict[len(line)] = []
                    word_list_dict[len(line)].append(line)
        return word_list_dict

class BruteForceByWord(ConstructionAlgorithm):
    def _recBruteForceConstruct(curr_word_ind, word_list_dict, xword):
        if (curr_word_ind == len(xword.getAcrosses() )):
            # know that all inserted acrosses are valid so we only check downs
            isValid = BruteForceByWord.checkValid(xword, word_list_dict)
            if isValid:
                print("FOUND:")
                print(xword)
                return True
            else:
                print("--------")
                print(xword)
                return False
        current_across = xword.getAcrosses()[curr_word_ind]

        try:
            filtered_word_set = word_list_dict[len(current_across)]
        except:
            # if there are were no words available of that length
            return False
        for i in range(len(filtered_word_set)):
            word = word_list_dict[len(current_across)].popleft()
            Timer.start("addAcross")
            xword.addAcross(curr_word_ind, word)
            Timer.stop("addAcross")
            if BruteForceByWord._recBruteForceConstruct(curr_word_ind + 1, word_list_dict, xword):
                return True
            Timer.start("removeAcross")
            xword.removeAcross(curr_word_ind)
            Timer.stop("removeAcross")
            word_list_dict[len(current_across)].append(word)
        return False

    # should be a parent method in ConstructionAlgorithm
    def _shuffleDict(word_list_dict):
        for key in word_list_dict:
            temp_list = list(word_list_dict[key])
            shuffle(temp_list)
            word_list_dict[key] = deque(temp_list)
        return word_list_dict

    def construct(rows, cols, empty_grid, word_list_file):
        Timer.start("readWordList")
        word_list_dict = BruteForceByWord.readWordList(word_list_file)
        Timer.stop("readWordList")
        # shuffle the wordlist
        Timer.start("shuffleDict")
        word_list_dict = BruteForceByWord._shuffleDict(word_list_dict)
        Timer.stop("shuffleDict")
        xword = Crossword(rows, cols, empty_grid)
        return BruteForceByWord._recBruteForceConstruct(0, word_list_dict, xword)

    def checkValid(xword, word_list_dict):
        # removed makes sure none of the downs are the same as any other down/across
        removed = []
        for word in xword.getDowns():
            if word not in word_list_dict[len(word)] or word in removed:
                return False
            else:
                removed.append(word)
        return True

    def readWordList(word_list_file):
        # returns a dictionary with key as len and value as a deque of that len
        word_list_dict = {}

        with open(pathname + 'wordlists/' + word_list_file + '.txt') as my_file:
            for line in my_file:
                line = line.strip()
                try:
                    word_list_dict[len(line)].append(line)
                except KeyError:
                    word_list_dict[len(line)] = deque()
                    word_list_dict[len(line)].append(line)

        return word_list_dict

class IntelligentLookahead(ConstructionAlgorithm):

    """
    IDEA: Store a list of words that could fit in each word space. Add words
    to the word space with the fewest options. If there are no options, remove
    the last added word. As you add words, update the list of words available
    for each word space.

    Despite this, this algorithm, with a sufficient wordlist, can quickly
    solve a 15x15 with ample shaded squares.
    """
    def _matches(dict_word, grid_word):
        """
        Take a dict_word: a word
        Take a grid_word: spaces for blanks, and letters for letters
        return true if the word `fits` given the letters
        """
        for i in range(len(grid_word)):
            dict_char = dict_word[i].upper()
            grid_char = grid_word[i].upper()
            if grid_char != dict_char and grid_char != ' ':
                return False

        return True

    def _buildGridDict(word_list_dict, xword):
        grid_words_dict = {}
        acrosses = xword.getAcrosses()
        # make across dictionaries
        for i, grid_word in enumerate(acrosses):
            curr_tup = (i, 'A')
            # get all words of length of current across saved at curr_tup index
            try:
                fitting_words = [dict_word for dict_word in word_list_dict[len(grid_word)]
                                    if IntelligentLookahead._matches(dict_word, grid_word)]
            except:
                # if there are no words of that length
                fitting_words = []
            if len(fitting_words) == 0 and ' ' not in grid_word:
                fitting_words.append(grid_word)
            elif len(fitting_words) == 0:
                return False
            grid_words_dict[curr_tup] = []
            grid_words_dict[curr_tup].append(set(fitting_words))

        downs = xword.getDowns()
        # make down dictionaries
        for i, grid_word in enumerate(downs):
            curr_tup = (i, 'D')
            # get all words of length of current down saved at curr_tup index
            try:
                fitting_words = [dict_word for dict_word in word_list_dict[len(grid_word)]
                                    if IntelligentLookahead._matches(dict_word, grid_word)]
            except:
                # if there are no words of that length
                fitting_words = []
            if len(fitting_words) == 0 and ' ' not in grid_word:
                fitting_words.append(grid_word)
            elif len(fitting_words) == 0:
                return False
            grid_words_dict[curr_tup] = []
            grid_words_dict[curr_tup].append(set(fitting_words))
        return grid_words_dict

    def _update_coords(coords, fixing_dir):
        """
        Given a tuple of coords, and a fixing direction A/D
        Return coordinates that move one character in the direction of the
        fixing direction
        """
        if (fixing_dir == 'D'):
            coords = (coords[0], coords[1] + 1, coords[2])
        elif (fixing_dir == 'A'):
            coords = (coords[0] + 1, coords[1], coords[2])
        return coords

    def _get_intersecting_spaces(xword, curr_fewest_tup, word):
        """
        Return a list of tuples that are keys for the grid_words_dict
        given a word tuple
        """
        intersecting_spaces = []

        word_index_to_coords = xword.getWordIndexToCoords()
        position_index_dict = xword.getPositionIndexDict()
        # get the starting coordinates (in (r, c) form), of the recently added word
        coords = word_index_to_coords[curr_fewest_tup]
        if (curr_fewest_tup[1] == 'A'):
            fixing_dir = 'D'
        elif (curr_fewest_tup[1] == 'D'):
            fixing_dir = 'A'
        coords += (fixing_dir,)

        # for each inserted char in the word, update the intersecting word's wordlist
        for i in range(len(word)):
            # get the index of the intersecting word
            fixing_dir_index = position_index_dict[coords][0]
            # get the character index of this (r,c) of the opposite direction word

            fixing_tup = (fixing_dir_index, fixing_dir)
            intersecting_spaces.append(fixing_tup)

            # update coords to go to the next character
            coords = IntelligentLookahead._update_coords(coords, fixing_dir)
        return intersecting_spaces

    def _findSmallestSet(grid_words_dict, tup_stack):
        """
        Take in the current list of words available for each word space and
        looks through each of the word lists (for any words not yet
        inserted).
        Return the tuple of the word with the fewest options.
        If all of the tuples have been inserted, return -1
        """
        min_amount = -1
        for key in grid_words_dict:
            if key not in tup_stack:
                if (len(grid_words_dict[key][-1]) < min_amount) or (min_amount == -1):
                    # curr_fewest_tup will be a tuple (ind, A/D)
                    curr_fewest_tup = key
                    min_amount = len(grid_words_dict[key][-1])
        if min_amount == -1:
            return -1
        return curr_fewest_tup

    def _updateGridDictAddWord(grid_words_dict, xword, curr_fewest_tup, word):
        word_index_to_coords = xword.getWordIndexToCoords()
        position_index_dict = xword.getPositionIndexDict()
        # get the starting coordinates (in (r, c) form), of the recently added word
        coords = word_index_to_coords[curr_fewest_tup]
        if (curr_fewest_tup[1] == 'A'):
            fixing_dir = 'D'
        elif (curr_fewest_tup[1] == 'D'):
            fixing_dir = 'A'
        coords += (fixing_dir,)

        intersecting_spaces = IntelligentLookahead._get_intersecting_spaces(xword, curr_fewest_tup, word)

        # for each inserted char in the word, update the intersecting word's wordlist
        for i in range(len(intersecting_spaces)):
            fixing_tup = intersecting_spaces[i]
            words_still_valid = set()
            fixing_char_num = position_index_dict[coords][1]

            # Loop through the "active" word list
            for list_word in grid_words_dict[fixing_tup][-1]:
                # remove every word in the list if the character that was added
                # doesn't match the character at that spot in the list
                if list_word[fixing_char_num] == word[i] and list_word != word:
                    words_still_valid.add(list_word)
            # push onto the stack the new set of valid words
            grid_words_dict[fixing_tup].append(words_still_valid)
            coords = IntelligentLookahead._update_coords(coords, fixing_dir)

        return grid_words_dict

    def _updateGridDictRemoveWord(grid_words_dict, xword, removed_word_tup, removed_word):
        word_index_to_coords = xword.getWordIndexToCoords()
        position_index_dict = xword.getPositionIndexDict()
        # get the starting coordinates (in (r, c) form), of the recently removed word
        coords = word_index_to_coords[removed_word_tup]
        if (removed_word_tup[1] == 'A'):
            fixing_dir = 'D'
        elif (removed_word_tup[1] == 'D'):
            fixing_dir = 'A'
        coords += (fixing_dir,)

        # for each inserted letter in the word, update the intersecting word's wordlist
        for i in range(len(removed_word)):
            # get the opposite direction word's index
            fixing_dir_index = position_index_dict[coords][0]
            fixing_tup = (fixing_dir_index, fixing_dir)
            # pop the last wordlist off the stack
            grid_words_dict[fixing_tup].pop()
            # increment the coordinates to be the next letter
            coords = IntelligentLookahead._update_coords(coords, fixing_dir)

        return grid_words_dict

    def construct(rows, cols, empty_grid, word_list_file):
        start_time = time.time()
        # make the crossword out of the empty grid
        xword = Crossword(rows, cols, empty_grid)

        word_list_dict = IntelligentLookahead.readWordList(word_list_file)
        # for each across/down word, make a list of words that could fit there
        # this will be a dictionary:
        #   Keys will be a tuple, index of word and A/D
        #   Values will be a STACK of sets of words
        # if grid_words_dict is False, then it won't be able to fill
        grid_words_dict = IntelligentLookahead._buildGridDict(word_list_dict, xword)
        if not grid_words_dict:
            return False

        # this list is a stack that keeps track of which words have been
        # inserted in what order
        tup_stack = []
        num_words = len(xword.getWords())

        while len(tup_stack) != num_words:
            # if the program is taking longer than MAX_TIME, quit
            if time.time() - start_time > MAX_TIME:
                print("Exceeded time limit")
                return False

            # find the word with the fewest options that hasn't yet been filled in
            curr_fewest_tup = IntelligentLookahead._findSmallestSet(grid_words_dict, tup_stack)

            # if curr_fewest_tup is -1, then all of the tuples are in tup_stack
            if curr_fewest_tup == -1:
                min_amount = -1
            else:
                min_amount = len(grid_words_dict[curr_fewest_tup][-1])

            # if min_amount IS -1, that means that the grid is filled in well
            if min_amount > 0:
                tup_stack.append(curr_fewest_tup)
                smallest_set = grid_words_dict[curr_fewest_tup][-1]
                # get a random word from the set and remove it from the set
                word = choice(list(smallest_set))
                grid_words_dict[curr_fewest_tup][-1].remove(word)

                xword.addWord(curr_fewest_tup, word)
                IntelligentLookahead._updateGridDictAddWord(grid_words_dict, xword, curr_fewest_tup, word)

            # if min_amount == 0, then the last insert forced a collision, so remove the last word
            elif min_amount == 0:
                # if the list is empty, that means we've tried every path
                if len(tup_stack) == 0:
                    return False
                removed_word_tup = tup_stack.pop()
                removed_word = xword.removeWord(removed_word_tup)
                IntelligentLookahead._updateGridDictRemoveWord(grid_words_dict, xword, removed_word_tup, removed_word)

            print(xword)
            print("--------")
        print("FOUND:")
        print(xword)

        # double check that all inserted words are valid
        for word in xword.getWords():
            if word not in word_list_dict[len(word)]:
                print("THAT'S NOT A WORD:", word)

        return True

    def readWordList(word_list_file):
        # returns a dictionary with:
        # key as len and value as a list of uppercase words of that len
        word_list_dict = {}

        with open(pathname + 'wordlists/' + word_list_file + '.txt') as my_file:
            for line in my_file:
                line = line.strip()
                try:
                    word_list_dict[len(line)].append(line.upper())
                except KeyError:
                    word_list_dict[len(line)] = []
                    word_list_dict[len(line)].append(line.upper())
        return word_list_dict
