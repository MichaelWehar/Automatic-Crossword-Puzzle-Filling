# Automatic Crossword Puzzle Filling - Open Source
## Introduction
A **crossword layout** is a two-dimensional grid that describes where the answers are located.  These answers are to be placed in horizontal and vertical blocks of contiguous empty cells.  The goal of this project is to develop an algorithm that takes in a crossword layout along with a word list and fills all such blocks with valid words.  This is an essential task when constructing a crossword puzzle.  Therefore, we call it the **Crossword Puzzle Construction Problem (CPCP)**.

## Summer Research (Summer 2020)
During summer of 2020 Otis Peterson worked with Professor Michael Wehar at Swarthmore College on solving the crossword puzzle construction problem. In particular, we implemented our own heuristic algorithms (based on established approaches) to provide a web-based crossword construction application. Otis presented this work at the National Conference on Undergraduate Research (NCUR 2021).  See our accepted abstract and an explanation of our implementation @ [crosswordconstruction.com](https://www.crosswordconstruction.com)

## Getting Started and Usage
The code in this repo is a self-contained demonstration of our original implementation.  You can simply use python to run the `test_crossword.py` file to test our algorithm on an example 5 by 5 crossword layout.  Or, you can install [flask](https://flask.palletsprojects.com/en/stable/) and run the `flask_app.py` file.  Then, you can navigate to the local host url in your web browser to generate crossword puzzles using our demonstration UI.  Alternatively, you can try out our algorithm @ [crosswordconstruction.com](https://www.crosswordconstruction.com/generator)

We included a sample word list of 100,000 suggested English words.  We encourage you to add your own word lists.  You can simple create files `wordlists/your_word_list.txt` or `wordlists/your_other_word_list.txt` to test our implementation with your own word lists.

## License
- MIT

## Credits
- Michael Wehar
- Otis Peterson

## Libraries
- Our UI demo uses [Bootstrap](https://getbootstrap.com).

## References and Links
- [Abstract](https://www.crosswordconstruction.com/static/files/abstract.pdf) and [Poster](https://www.crosswordconstruction.com/static/files/poster.pdf) presented at NCUR 2021
- [Live Demo @ crosswordconstruction.com](https://www.crosswordconstruction.com/generator)
- [Previous Project on Generating Crossword Puzzle Layouts](https://github.com/MichaelWehar/Crossword-Layout-Generator)
- [Blog Post on Generating Crosswords](https://www.aiplusinfo.com/blog/ai-generated-crossword-puzzles/)
