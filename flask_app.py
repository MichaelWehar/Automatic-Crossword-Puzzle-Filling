# Imports
import json
from construction_algorithm import *

# Import Flask
from flask import Flask, render_template, request
app = Flask(__name__)

# Helper functions
def processFilename(filename):
    if filename == "option1":
        return "sample_word_list"
    elif filename == "option2":
        return "your_word_list"
    else:
        return "your_other_word_list"

# Server routes
@app.route("/")
def get_main_page():
    return render_template("index.html")

@app.route('/generateCrossword', methods=['POST'])
def generateCrossword():
    # Get request data
    data = request.get_json()
    filename = data["wordlist"]
    grid = data["grid"]
    # Get dimensions
    rows = len(grid)
    cols = 0
    if rows > 0:
        cols = len(grid[0])
    # Process filename and grid
    filename = processFilename(filename)
    # Construction algorithm
    print(grid)
    if IntelligentLookahead.construct(rows, cols, grid, filename):
        print(json.dumps(grid))
        return json.dumps(grid)
    else:
        return ""

if __name__ == '__main__':
    app.run()
