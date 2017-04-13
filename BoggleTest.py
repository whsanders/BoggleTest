# BoggleTest.py
#
# Programming Rules:
#  1. Python 2.7.x or Python 3.3.x maybe used.
#     A. Please document which version was used.
#     B. Include make files or project files where appropriate.
#  2. Any core language feature may be used.
#  3. 3rd Party modules are not allowed.
#  4. Sample board and dictionary files provided.
#  5. Submit all source files needed to run the solution.
#
# Game Rules:
#  Boggle is a word game.  The goal is to make as many words as possible
#  out of the given set of letters laid out in a 4x4 grid.  Words are 
#  formed by starting with any letter and moving to an adjacent letter
#  (up, down, left, right, or diagonal) and so-forth on.  Once a letter
#  is used in a word, it can not be used again.  All words must be a 
#  minimum of 3 characters in length.  Finally, in this version, a "q"
#  will always represent "qu", since "u" nearly always follows "q" in
#  English.  If a word may be formed multiple ways on the same board, it
#  only counts once.
#
# Example:
#
# Board:
#    P W Y R
#    E N T H
#    G S I Q
#    O L S A
#
# A few possible words:
#   pen
#   peg
#   quit
#   hit
#   slit
#   slits
#
# Command line arguments:
#  python BoggleTest.py <dictionary_filename> <board_filename> <output_filename>
#
# Dictionary:
#  The dictionary file is an ASCII text file that lists acceptable words.  Each word is
#  new line separated.  Words are in alphabetical order and all lowercase, utilizing
#  only letters 'a' to 'z'.
#
# Board:
#  The board file is an ASCII text file that is 4 lines of 4 characters.  These
#  represent the game board, a 4x4 matrix of characters.  These may be mixed case.
#  Whitespace is optional and should be ignored.  Only letters 'a' to 'z' or 'A'
#  to 'Z' are used.
#
# Output:
#  The output should be an ASCII text file (in alphabetical order) of all legal words
#  possible to spell on the current board that are in the given dictionary.  These
#  should be all lowercase and newline separated (same format as the dictionary).
#
# Notes:
#  Your final solution should be PRODUCTION QUALITY, as if it is getting checked
#  in to live production code.

import sys
import argparse
import re
from boggle_pad import BogglePad

def main():
    args = parse_arguments()

    run_boggle_game(args.dictionary_filename, args.board_filename, args.output_filename)

    sys.exit(0)


def parse_arguments():
    parser = argparse.ArgumentParser(description="Play Boggle.")

    parser.add_argument("dictionary_filename")
    parser.add_argument("board_filename")
    parser.add_argument("output_filename")

    return parser.parse_args()


def run_boggle_game(dictionary_filename, board_filename, output_filename):
    player = BogglePlayer()

    player.know_thy_words(dictionary_filename)
    player.observe_ye_board(board_filename)

    scorepad = player.play_boggle()
    scorepad.dedupe_and_alphabetize().write_down(output_filename)


class BogglePlayer:

    _AN_INDISPENSABLE_WORD = "pirate"

    def __init__(self):
        self.__words_known_by_first_two_letters = {}
        self.__board = BoggleBoard()

    def know_thy_words(self, filename):
        # Learn words from a dictionary file.
        # Reads file into memory; not tested for big files. Two letters are enough to rule
        # out most invalid search paths entirely, so we chunk (and key) by that.

        print "Learning words from %s..." % filename

        learned = 0
        skipped = 0
        seems_legit = False

        dictionary = open(filename)
        for line in dictionary:
            word = line.strip()
            if self.learn(word):
                learned += 1
            else:
                skipped += 1
            if word == self._AN_INDISPENSABLE_WORD:
                seems_legit = True
        dictionary.close()

        if not seems_legit:
            print "WARN: This dictionary doesn't seem to include '%s'" % self._AN_INDISPENSABLE_WORD

        print "Learned %d words (ignored %d short words)" % (learned, skipped)

    def learn(self, word):
        if len(word) < 3:
            return False

        if len(word) > 16:
            return True        # Whatever. We know this won't be on the exam; this helps against malicious dictionaries.

        key = word[:2]
        if not key in self.__words_known_by_first_two_letters:
            self.__words_known_by_first_two_letters[key] = []
        if not word in self.__words_known_by_first_two_letters[key]:
            self.__words_known_by_first_two_letters[key].append(word)

        return True

    def unlearn(self, word):
        if len(word) < 3:
            return

        key = word[:2]
        if not key in self.__words_known_by_first_two_letters:
            return
        if word in self.__words_known_by_first_two_letters[key]:
            self.__words_known_by_first_two_letters[key].remove(word)

    def observe_ye_board(self, filename):
        # Setup a Boggle board from a file.
        # If the file doesn't have exactly 4 rows of 4 characters each, this will raise a ValueError.

        print "Looking at board from %s..." % filename

        board = open(filename)
        lines = board.readlines()
        board.close()
        rows = []
        for line in lines:
            rows.append(re.sub("[^a-zA-Z]", '', line))

        print '\n'.join(rows)
        self.__board.set_board(rows)

    def play_boggle(self):
        # Play Boggle with a board and dictionary previously specified.
        #
        # For each ordered pair of adjacent "boggs", checks to see if there are known words beginning with them. If so,
        # switches over to perform a depth-first search for each word from that point. This may be unnecessary
        # complexity but it performs fine while demonstrating more features of the python language, which seems
        # appropriate for this exercise.
        #
        # Returns: A boggle_pad.BogglePad containing the unsorted (and possibly redundant) words found during play.

        print "Playing Boggle!"

        pad = BogglePad()

        for pair in self.__consider_each_possible_pair():
            first_few_letters = pair.read(True)

            one_to_unlearn = ""
            for candidate in self.__words_i_know_starting_with(first_few_letters):
                rest_of_word = candidate[len(first_few_letters):]
                if self.__can_get_there_from_here(rest_of_word, pair):
                    pad.jot(candidate)
                    one_to_unlearn = candidate
            self.unlearn(one_to_unlearn)        # Lazy non-critical optimization to help when many permutations of a word exist.

        print "Jotted down %d total words" % pad.count()
        return pad

    def __consider_each_possible_pair(self):
        # Iterates through all permutations of a first and adjacent second "bogg" on the board.
        #
        # This flags each bogg as being considered and is intended as the start of the consideration chain. It
        # is NOT safe to nest or to use when a chain is going, and will break consideration badly.
        #
        # NOTE: If you break or return out of the loop, you are still considering the chain and are responsible for
        # forgetting it when appropriate with Bogg.forget().

        for bogg in self.__board.boggs():
            bogg.consider()
            for neighbor in bogg.neighbors():
                if not neighbor.is_considered():
                    neighbor.consider(bogg)
                    yield neighbor
                    neighbor.forget()
            bogg.forget()

    def __words_i_know_starting_with(self, at_least_two_letters):
        # Iterates through known words that start with the given string.
        #
        # Complains and throws up its hands (but does not raise an exception) if the starting string isn't at least 2 characters long.

        if len(at_least_two_letters) < 2:
            print "ERROR: can't list words starting with '%s', there are just too many; I need at least two letters" % at_least_two_letters
            return
        two_letters = at_least_two_letters[:2]
        two_covers_it = len(at_least_two_letters) == 2        # Can we skip an explicit check later because we got exactly 2?
        if not two_letters in self.__words_known_by_first_two_letters:
            return
        for word in self.__words_known_by_first_two_letters[two_letters]:
            if two_covers_it or word.startswith(at_least_two_letters):
                yield word

    def __can_get_there_from_here(self, rest_of_word, start_bogg):
        # Search recursively for a string from the given consideration chain.
        #
        # You must mark start_bogg as considered yourself; this does not assume it can safely do it for you.
        if rest_of_word == "":
            return True        # we're already there
        for next in start_bogg.neighbors():
            if not next.is_considered():
                next_part = next.read()
                if rest_of_word.startswith(next_part):
                    next.consider(start_bogg)
                    got_there = self.__can_get_there_from_here(rest_of_word[len(next_part):], next)
                    next.forget()
                    if got_there:
                        return True
        return False


class BoggleBoard:

    def __init__(self):
        self.__boggs = []

    def set_board(self, rows):
        # Initialize board state given a 4x4 array of characters.

        if len(rows) != 4:
            raise ValueError("A Boggle board must have exactly 4 rows!")
        if [row for row in rows if len(row) != 4]:
            raise ValueError("Every row in Boggle must have exactly 4 letters!")

        # clean board
        self.__boggs = []

        # set it
        for row in rows:
            self.__set_bogg_row(row)

        # set adjacency
        for i in range(4):
            for j in range(4):
                for adj_i in range(i-1, i+2):
                    for adj_j in range(j-1, j+2):
                        if adj_i == i and adj_j == j:
                            continue
                        if adj_i in range(4) and adj_j in range(4):
                            self.__boggs[i][j].set_adjacent(self.__boggs[adj_i][adj_j])

    def __set_bogg_row(self, row):
        bogg_row = []
        for letter in row:
            bogg_row.append(self.__make_bogg(letter))
        self.__boggs.append(bogg_row)

    def __make_bogg(self, letter):
        bogg = Bogg()
        bogg.set_letter(letter)
        return bogg

    def boggs(self):
        for row in self.__boggs:
            for bogg in row:
                yield bogg


# A player's semantic representation of a tile on the Boggle board
#
# (Yes, there is probably a better name.)
#
# A bogg knows about the tile's syntactic contribution, e.g. "Q" -> "qu",
# as well as who its neighbors are and whether the player is currently 
# considering it as part of a word.
class Bogg:

    def __init__(self):
        self.__adj = []
        self.__letter = ""
        self.__word_part = ""
        self.__is_considered = False
        self.__considered_after = None

    def set_letter(self, letter):
        if len(letter) != 1:
            print "WARN: Single character expected, but received '%s'" % letter
        self.__letter = letter
        self.__word_part = letter.lower()
        if self.__word_part == "q":
            self.__word_part = "qu"

    def read(self, include_considered_chain=False):
        # Reads from the bogg or, optionally, a consideration chain it terminates.

        if include_considered_chain and self.__is_considered and self.__considered_after:
            return self.__considered_after.read(True) + self.__word_part
        else:
            return self.__word_part

    def set_adjacent(self, bogg):
        # Tells the bogg about a neighbor.
        if not bogg in self.__adj:
            self.__adj.append(bogg)

    def neighbors(self):
        # Iterates through the bogg's adjacent neighbors.

        for neighbor in self.__adj:
            yield neighbor

    def consider(self, previous=None):
        # Marks the bogg as being considered in a word.

        self.__is_considered = True
        self.__considered_after = previous

    def is_considered(self):
        # Returns True if the bogg is being considered in a solution.

        return self.__is_considered

    def forget(self):
        # Marks the bogg as no longer being considered.

        self.__considered_after = None
        self.__is_considered = False


if __name__ == '__main__':
    main()
