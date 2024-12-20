import json
from timer import Timer

class Crossword:
    # Constructor
    def __init__(self, rows, cols, optional_grid = []):
        self.rows = rows
        self.cols = cols
        self.grid = self._buildGrid(rows, cols, optional_grid)
        # construct a 2d array of spaces given the size
        self.acrosses = []
        self.downs = []
        self._loadAcrosses()
        self._loadDowns()
        # dictionary where tuples are the keys and values are the positions
        # for example (0, 0, A) : 1
        self.position_dict = {}
        self._buildPositions()

        # dictionary that takes the tuple as a key, values are a tuple of the INDEX
        # of the word to change in the acrosses/downs list and the index
        # of which character in the word it is
        # for example (0, 1, A) : (0, 1)
        self.position_index_dict = {}

        # (ind, 'A') : (r, c)
        self.word_index_to_coords = {}

        # build position_index_dict and word_index_to_coords
        # TODO make this build position_dict too
        self._buildIndexes()

    # Private Methods
    def _buildGrid(self, rows, cols, optional_grid):
        grid = []
        if (len(optional_grid) == 0):
            for r in range(rows):
                row = []
                grid.append(row)
                for c in range(cols):
                    grid[r].append(' ')
            return grid
        # throw an error if rows/cols of optional grid don't match?
        else:
            for r in range(rows):
                for c in range(cols):
                    optional_grid[r][c] = optional_grid[r][c].upper()
            return optional_grid

    def _loadAcrosses(self):
        # Loop through each row, and every time you hit a shaded square, if
        # you've accumulated a new word, then add that to the acrosses
        del self.acrosses[:]
        new_word = ""
        for r in range(self.rows):
            for c in range(self.cols):
                if (self.grid[r][c] != '.'):
                    new_word += self.grid[r][c]
                else:
                    # if you hit a shaded square
                    if (new_word != ""):
                        self.acrosses.append(new_word)
                        new_word = ""
            # at the end of the row
            if (new_word != ""):
                self.acrosses.append(new_word)
            new_word = ""

    def _loadDowns(self):
        del self.downs[:]
        new_word = ""
        for c in range(self.cols):
            for r in range(self.rows):
                if (self.grid[r][c] != '.'):
                    new_word += self.grid[r][c]
                else:
                    # if you hit a shaded square
                    if (new_word != ""):
                        self.downs.append(new_word)
                        new_word = ""
            #at the end of the row
            if (new_word != ""):
                self.downs.append(new_word)
            new_word = ""

    """
    Builds a numbering system in the self.position_dict variable.
    The numbering system is as follows:
        Left to right, top to bottom scan each cell of the grid. If any cell is
        the first letter of either an across or down, assign that cell a
        number. Start by assigning the number 1, then for each subsequent
        assigning, increase the number by one.
    Read here for more info on the common process for clue numbering:
    https://www.crosswordunclued.com/2009/10/numbering-clue-slots-in-grid.html
    """
    def _buildPositions(self):
        added_to_curr = False
        curr_position = 1
        for r in range(self.rows):
            for c in range(self.cols):
                if (self.grid[r][c] != '.'):
                    curr_tup = (r,c)
                    if (c == 0 or self.grid[r][c - 1] == '.'):
                        across_tup = curr_tup + ('A',)
                        self.position_dict[across_tup] = curr_position
                        added_to_curr = True
                    if (r == 0 or self.grid[r-1][c] == '.'):
                        across_tup = curr_tup + ('D',)
                        self.position_dict[across_tup] = curr_position
                        added_to_curr = True
                    if (added_to_curr):
                        curr_position += 1
                        added_to_curr = False
    """
    Define a dictionary where every row, column, across/down, tuple
    corresponds to an index in the list of acrosses/downs. The index will read
    -1 if it is a shaded square
    """
    def _buildIndexes(self):
        # add the acrosses to the dictionary
        new_word = ""
        word_on = 0
        for r in range(self.rows):
            for c in range(self.cols):
                if len(new_word) == 0:
                    start_r = r
                    start_c = c
                curr_tup_acc = (r, c, 'A')
                if (self.grid[r][c] != '.'):
                    new_word += self.grid[r][c]
                    in_word_ind = len(new_word) - 1
                    self.position_index_dict[curr_tup_acc] = (word_on, in_word_ind)
                    self.word_index_to_coords[(word_on, 'A')] = (start_r, start_c)
                else:
                    # if you hit a shaded square
                    if (new_word != ""):
                        word_on += 1
                        new_word = ""
                    self.position_index_dict[curr_tup_acc] = (-1 , -1)
            # at the end of the row
            if (new_word != ""):
                word_on += 1
            new_word = ""

        # add the downs to the dictionary
        new_word = ""
        word_on = 0
        for c in range(self.cols):
            for r in range(self.rows):
                if len(new_word) == 0:
                    start_r = r
                    start_c = c
                curr_tup_acc = (r, c, 'D')
                if (self.grid[r][c] != '.'):
                    new_word += self.grid[r][c]
                    in_word_ind = len(new_word) - 1
                    self.position_index_dict[curr_tup_acc] = (word_on, in_word_ind)
                    self.word_index_to_coords[(word_on, 'D')] = (start_r, start_c)
                else:
                    # if you hit a shaded square
                    if (new_word != ""):
                        word_on += 1
                        new_word = ""
                    self.position_index_dict[curr_tup_acc] = (-1, -1)
            # at the end of the row
            if (new_word != ""):
                word_on += 1
            new_word = ""

    def _createJSONEntry(self, word, row, col, orientation):
        position = self.position_dict[(row, col, orientation)]

        return  {
                    'word' : word,
                    'row' : row,
                    'col' : col,
                    'position' : position,
                    'orientation' : orientation
                }

    # Public Methods
    def addShadedSquare(self, r, c):
        # TODO: Modify so it changes the across/down lists as you go
        # could just make a validCoords helper function, could use more defensive programming
        if (r < 0 or r > self.rows - 1 or c < 0 or c > self.cols - 1):
            print("invalid coords")
        else:
            self.grid[r][c] = '.'

    def addLetter(self, r, c, char):
        # Timer.start("addLetter")
        if (r < 0 or r > self.rows - 1 or c < 0 or c > self.cols - 1):
            raise RuntimeError("The indexes don't correspond to valid locations on the grid. Tried Row: %d and Col: %d" % (r, c) )
        elif (len(char) > 1):
            print("enter just one letter")
        else:
            self.grid[r][c] = char

            # modify the across
            ind_tup = self.position_index_dict[(r, c, 'A')]
            list_spot = ind_tup[0]
            word_spot = ind_tup[1]
            self.acrosses[list_spot] = self.acrosses[list_spot][:word_spot] + char + self.acrosses[list_spot][word_spot + 1:]

            # modify the down
            ind_tup = self.position_index_dict[(r, c, 'D')]
            list_spot = ind_tup[0]
            word_spot = ind_tup[1]
            self.downs[list_spot] = self.downs[list_spot][:word_spot] + char + self.downs[list_spot][word_spot + 1:]
        # Timer.stop("addLetter")

    def addWord(self, ind_dir_tup, word):
        ind = ind_dir_tup[0]
        direction = ind_dir_tup[1]

        if (direction == 'A'):
            if len(word) != len(self.acrosses[ind]):
                raise ValueError('Trying to add a word of incorrect length. Word: %s, Current Across: %s' %(word, self.acrosses[ind]))

            start_r = self.word_index_to_coords[ind_dir_tup][0]
            start_c = self.word_index_to_coords[ind_dir_tup][1]

            # modify the grid to show the change
            c = start_c
            for char in word:
                self.addLetter(start_r, c, char)
                c += 1
        elif (direction == 'D'):
            if len(word) != len(self.downs[ind]):
                raise ValueError('Trying to add a word of incorrect length. Word: %s, Current Down: %s' %(word, self.downs[ind]))
            start_r = self.word_index_to_coords[ind_dir_tup][0]
            start_c = self.word_index_to_coords[ind_dir_tup][1]
            # modify the grid to show the change
            r = start_r
            for char in word:
                self.addLetter(r, start_c, char)
                r += 1

    def removeWord(self, ind_dir_tup):
        ind = ind_dir_tup[0]
        direction = ind_dir_tup[1]
        removed_word = ""

        if (direction == 'A'):
            start_r = self.word_index_to_coords[ind_dir_tup][0]
            start_c = self.word_index_to_coords[ind_dir_tup][1]

            # modify the grid to show the change
            c = start_c
            for i in range(len(self.acrosses[ind])):
                removed_word += self.grid[start_r][c]
                self.addLetter(start_r, c, " ")
                c += 1
        elif (direction == 'D'):
            start_r = self.word_index_to_coords[ind_dir_tup][0]
            start_c = self.word_index_to_coords[ind_dir_tup][1]
            # modify the grid to show the change
            r = start_r
            for i in range(len(self.downs[ind])):
                removed_word += self.grid[r][start_c]
                self.addLetter(r, start_c, " ")
                r += 1
        return removed_word

    def addAcross(self, ind, word):
        if len(word) != len(self.acrosses[ind]):
            raise ValueError('Trying to add a word of incorrect length. Word: %s, Current Across: %s' %(word, self.acrosses[ind]))

        start_r = self.word_index_to_coords[(ind, 'A')][0]
        start_c = self.word_index_to_coords[(ind, 'A')][1]

        # modify the grid to show the change
        c = start_c
        for char in word:
            self.addLetter(start_r, c, char)
            c += 1

    def removeAcross(self, ind):
        curr_word = self.acrosses[ind]
        start_r = self.word_index_to_coords[(ind, 'A')][0]
        start_c = self.word_index_to_coords[(ind, 'A')][1]

        # modify the grid to show the change
        c = start_c
        for char in curr_word:
            self.addLetter(start_r, c, " ")
            c += 1

    def isFull(self):
        for row in self.grid:
            for char in row:
                if (char == ' '):
                    return False
        return True

    def noDuplicates(self):
        words = self.acrosses + self.downs
        if len(set(words)) == len(words):
            return True
        return False

    def getWordIndexToCoords(self):
        return self.word_index_to_coords

    def getPositionIndexDict(self):
        return self.position_index_dict

    def getWords(self):
        return self.acrosses + self.downs

    def getAcrosses(self):
        return self.acrosses

    def getDowns(self):
        return self.downs

    def getGrid(self):
        return self.grid

    # Export data
    def exportAs2DArray(self):
        return str(self.grid)

    # This is for serializing our crossword object so that we can
    # send and receive crosswords over the internet.
    # TODO use position_index_dict to simplify this
    def exportAsJSON(self):
        """
        Returns a json type obejct as a list of words of type:
                {
                    'word' : new_word,
                    'row' : row,
                    'col' : col,
                    'position' : position
                    'orientation' : 'across/down'
                }
        """
        json_return = [] # set() and change appends to adds

        # add all of the acrosses to the list
        new_word = ""
        curr_row = 0
        curr_col = 0
        for r in range(self.rows):
            for c in range(self.cols):
                if (self.grid[r][c] != '.'):
                    # if this is the first letter we're adding, then save the coords
                    if (len(new_word) == 0):
                        curr_row = r
                        curr_col = c
                    new_word += self.grid[r][c]
                else:
                    # if you hit a shaded square
                    if (new_word != ""):
                        new_word_info = self._createJSONEntry(new_word, curr_row, curr_col, "A")
                        json_return.append(new_word_info)
                        new_word = ""
            # at the end of the row
            if (new_word != ""):
                new_word_info = self._createJSONEntry(new_word, curr_row, curr_col, "A")
                json_return.append(new_word_info)
            new_word = ""
        # add all of the downs to the list
        new_word = ""
        curr_row = 0
        curr_col = 0
        for c in range(self.cols):
            for r in range(self.rows):
                if (self.grid[r][c] != '.'):
                    #if this is the first letter we're adding, then save the coords
                    if (len(new_word) == 0):
                        curr_row = r
                        curr_col = c
                    new_word += self.grid[r][c]
                else:
                    # if you hit a shaded square
                    if (new_word != ""):
                        new_word_info = self._createJSONEntry(new_word, curr_row, curr_col, "D")
                        json_return.append(new_word_info)
                        new_word = ""
            # at the end of the row
            if (new_word != ""):
                new_word_info = self._createJSONEntry(new_word, curr_row, curr_col, "D")
                json_return.append(new_word_info)
            new_word = ""

        json_return = json.dumps(json_return)
        return json_return

    # Print function will call this
    def __str__(self):
        ret_str = ""
        for line in self.grid:
            if ret_str == "":
                ret_str = str(line)
            else:
                ret_str += "\n" + str(line)
        return ret_str
