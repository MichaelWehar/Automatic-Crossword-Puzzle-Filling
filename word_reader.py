import os
pathname = os.path.dirname(os.path.abspath(__file__)) + "/"

class WordReader:
    @staticmethod
    def read(name):
        word_list = []
        with open(pathname + 'wordlists/' + name + '.txt') as my_file:
            for line in my_file:
                line = line.strip()
                word_list.append(line)
        return word_list
