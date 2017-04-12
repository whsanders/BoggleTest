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
    args = parser.parse_args()
    return args


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
            print "WARN: This dictionary doesn't seem to include '%s'." % self._AN_INDISPENSABLE_WORD

        print "Learned %d words (ignored %d short words)" % (learned, skipped)

    def learn(self, word):
        if len(word) < 3:
            return False

        key = word[:2]
        if not key in self.__words_known_by_first_two_letters:
            self.__words_known_by_first_two_letters[key] = []
        if not word in self.__words_known_by_first_two_letters[key]:
            self.__words_known_by_first_two_letters[key].append(word)

        return True

    def observe_ye_board(self, filename):
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
        print "Playing Boggle!"

        pad = BogglePad()

        # REMOVE: take this out!
        self.learn("jqu")

        for pair in self.__consider_each_possible_pair():
            beginning = pair.read(True)
            print "thinking of words starting with '%s'..." % beginning
            first_two = beginning[:2]        # different from beginning iff 'Q' is involved
            for rest in [word[len(beginning):] for word in self.__words_i_know_starting_with(first_two) if word.startswith(beginning)]:
                print "rest could be '%s'" % rest

        pad.jot("day")
        pad.jot("die")
        pad.jot("home")
        pad.jot("kid")
        pad.jot("rid")
        pad.jot("way")
        return pad

    def __consider_each_possible_pair(self):
        for bogg in self.__board.boggs():
            bogg.consider()
            for neighbor in bogg.neighbors():
                if not neighbor.is_considered():
                    neighbor.consider(bogg)
                    yield neighbor
                    neighbor.forget()
            bogg.forget()

    def __words_i_know_starting_with(self, two_letters):
        if not two_letters in self.__words_known_by_first_two_letters:
            print "don't known any!"
            return
        for word in self.__words_known_by_first_two_letters[two_letters]:
            yield word


class BoggleBoard:
    def __init__(self):
        self.__boggs = []

    def set_board(self, rows):
        if len(rows) != 4:
            raise ValueError("A Boggle board must have exactly 4 rows!")
        if [row for row in rows if len(row) != 4]:
            raise ValueError("Every row in Boggle must have exactly 4 letters!")

        # clean board
        self.__boggs = []

        # set it
        for row in rows:
            self.__set_row(row)

        # set adjacency
        for i in range(4):
            for j in range(4):
                for adj_i in range(i-1, i+2):
                    for adj_j in range(j-1, j+2):
                        if adj_i == i and adj_j == j:
                            continue
                        if adj_i in range(4) and adj_j in range(4):
                            # print "Linking (%d,%d)->(%d,%d)" % (i, j, adj_i, adj_j)
                            self.__boggs[i][j].set_adjacent(self.__boggs[adj_i][adj_j])

        # print "Sanity checking adjacency:"
        # for i in range(4):
        #     for j in range(4):
        #         bogg = self.__boggs[i][j]
        #         print "'%s' -> [%s]" % (bogg.read(), ','.join(["'%s'" % neighbor.read() for neighbor in bogg.neighbors()]))

    def __set_row(self, row):
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
        if include_considered_chain and self.__is_considered and self.__considered_after:
            return self.__considered_after.read() + self.__word_part
        else:
            return self.__word_part

    def set_adjacent(self, bogg):
        if not bogg in self.__adj:
            self.__adj.append(bogg)

    def neighbors(self):
        for neighbor in self.__adj:
            yield neighbor

    def consider(self, previous=None):
        self.__is_considered = True
        self.__considered_after = previous

    def is_considered(self):
        return self.__is_considered

    def forget(self):
        self.__considered_after = None
        self.__is_considered = False


if __name__ == '__main__':
    main()
