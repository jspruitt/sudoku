# Jenny Pruitt

"""
Sudoku Puzzle Solver
The point of this program is to solve 120 sudoku puzzles in the least amount of time
The algorithm uses a brute force algorithm but speeds it up
This algorithm solves 128 puzzles in under 10 seconds
"""

import time
def main():
    """
    Main method that reads in input and runs the main program
    :return: nothing
    """
    # Start timer
    init = time.time()

    # Read sudoku.txt
    puzzle_list = open("sudoku.txt", "r").read().split()
    global num_of_pzls, side, box, neighbors, symbols, groups

    # Create global variables like the size of the pzl
    # Note: this allows for the sudoku puzzles to be of any size
    num_of_pzls = len(puzzle_list[0])
    side = int(num_of_pzls ** (.5))
    box = int(side ** (.5))
    symbols = "123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"[:side]

    # Create groups which represent the indices within every columm, row and box
    corners = [row * side + col for row in range(0, side, box) for col in range(0, side, box)]
    groups = [{first + index for index in range(0, side)} for first in range(0, num_of_pzls, side)] + \
             [{top + side * index for index in range(0, side)} for top in range(0, side)] + \
             [{index + col + row * side for row in range(0, box) for col in range(0, box)} for index in corners]

    # Create neighbors which maps each index to the indices that can't have the same symbol
    neighbors = {idx: set().union(*[nbrSet for nbrSet in groups if idx in nbrSet]) - {idx} for idx in range(num_of_pzls)}

    # Solve every puzzle in puzzle list
    for count, pzl in enumerate(puzzle_list):
        possibles = create_possibles(pzl)
        # Do initial deductions on the puzzle
        pzl = index_deductions(pzl, possibles)
        pzl = symbol_deductions(pzl, possibles)
        result = brute_force(pzl, possibles)
        # Prints out the result of brute force
        if result == "":
            print("Puzzle {}".format(count))
            print("It's Impossible")
        # The list comprehension sums up the symbols in puzzle
        else:
            print("{} {} {}".format(count, result, sum([int(result[i], 10) for i in range(len(result))])))
    print("Total Time: {} seconds".format(time.time() - init))


def brute_force(pzl, possibles):
    """
    Solves the pzl through a Brute Force algorithm
    :param pzl: a string representing the puzzle to be solved with "."s in the open spots
    :param possibles: a dictionary mapping each index to the possible symbols
    :return: a string representing a solved puzzle
    """
    # Checks if puzzle is finished
    if pzl.find(".") == -1: return pzl
    # Finds the next index with the least number of possible symbols
    next_index = min(possibles, key=lambda c: len(possibles[c]))
    index_set = possibles[next_index].copy()
    for symbol in index_set:
        changes = update_possibles(possibles, next_index, symbol)
        temporary = brute_force(pzl[:next_index] + symbol + pzl[next_index + 1:], possibles)
        if temporary != "": return temporary
        # Reverses the changes done in update_possibles
        deupdate_possibles(possibles, symbol, changes)
        possibles[next_index] = index_set
    return ""


def update_possibles(possibles, index, symbol):
    """
    Changes possibles to fit the changed puzzle
    :param possibles: a dictionary mapping each index to the possible symbols
    :param index: an integer representing the location of the change to puzzle
    :param symbol: a string representing the symbol that is added to puzzle
    :return: a dictionary representing the indices changed in possibles
    """
    changes = []
    for nbr in neighbors[index]:
        if nbr in possibles and symbol in possibles[nbr]:
            possibles[nbr].discard(symbol)
            changes.append(nbr)
    del possibles[index]
    return changes


def deupdate_possibles(possibles, symbol, changes):
    """
    Reverses the changes done in update_possibles
    :param possibles: a dictionary mapping each index to the possible symbols
    :param symbol: a string representing the symbol that was added to puzzle
    :param changes: a dictionary representing the indices in possibles that need to be changed back
    :return: nothing
    """
    for change in changes:
        possibles[change].add(symbol)


def index_deductions(pzl, possibles):
    """
    Does initial deductions based on the possibles dictionary if there is only one possible
    symbol for an index then it puts that symbol in the puzzle
    :param pzl: a string representing the puzzle to be solved with "."s in the open spots
    :param possibles: a dictionary mapping each index to the possible symbols
    :return: a string representing a puzzle with a few deductions
    """
    count = 0
    changes = []
    possibles_set = possibles.keys()
    for index in possibles_set:
        if len(possibles[index]) == 1:
            symbol = possibles[index].pop()
            count += 1
            changes.append((index, symbol))
            pzl = pzl[:index] + symbol + pzl[index + 1:]
    for index, symbol in changes:
        update_possibles(possibles, index, symbol)
    if count == 0:
        return pzl
    # Repeats process until there are no indices with only one symbol
    else:
        return index_deductions(pzl, possibles)


def symbol_deductions(pzl, possibles):
    """
    Performs deductions on each square, row and column through the traditional sudoku strategy
    :param pzl: a string representing the puzzle to be solved with "."s in the open spots
    :param possibles: a dictionary mapping each index to the possible symbols
    :return: a string representing a pzl with a few deductions
    """
    set_changed=[]
    for current_set in groups:
        # Within a group map each symbol to its possible indices
        symbol_dictionary = {i: set() for i in symbols}
        for symbol in symbols:
            if symbol_in_set(pzl, current_set, symbol): break
            for index in current_set:
                if pzl[index] == "." and symbol in possibles[index]:
                    symbol_dictionary[symbol].add(index)
        # If there is one symbol that fits only one index in a group, add it to the puzzle
        for symbol in symbol_dictionary:
            if len(symbol_dictionary[symbol]) == 1:
                index = symbol_dictionary[symbol].pop()
                pzl = pzl[:index] + symbol + pzl[index + 1:]
                set_changed.append((index, symbol))
    for index, symbol in set_changed:
        update_possibles(possibles, index, symbol)
    return pzl


def symbol_in_set(pzl, index_set, symbol):
    """
    Returns whether or not the symbol is in one of the squares, rows or columns
    :param pzl: a string representing the puzzle to be solved with "."s in the open spots
    :param index_set: a set of indices representing a square, row or column
    :param symbol: a string representing the symbol
    :return: a boolean representing whether or not the symbol is the square, row or column
    """
    for i in index_set:
        if pzl[i] == symbol: return True
    return False


def create_possibles(pzl):
    """
    Creates possibles, a dictionary mapping indices to the possible symbols
    :param pzl: a string representing the puzzle to be solved with "."s in the open spots
    :return: a dictionary  mapping indices to the possible symbols
    """
    possibles = {}
    for index in range(num_of_pzls):
        if pzl[index] == ".":
            possibles[index] = set(symbols)
            for neighbor in neighbors[index]:
                if pzl[neighbor] != ".":
                    possibles[index].discard(pzl[neighbor])
    return possibles


main()



