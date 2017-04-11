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

def main():
    args = parse_arguments()

    run_boggle_game(args)

    sys.exit(0)


def parse_arguments():
    parser = argparse.ArgumentParser(description="Play Boggle.")
    parser.add_argument("dictionary_filename")
    parser.add_argument("board_filename")
    parser.add_argument("output_filename")
    args = parser.parse_args()
    return args


def run_boggle_game(args):
    player = BogglePlayer()
    player.know_thy_words(args.dictionary_filename)
    player.observe_ye_board(args.board_filename)

    scoresheet = player.play_boggle()
    scoresheet.alphabetize().dedupe().write_down(args.output_filename)


class BogglePlayer:

    def know_thy_words(self, filename):
        print "Learning words from %s..." % filename

    def observe_ye_board(self, filename):
        print "Looking at board from %s..." % filename

    def play_boggle(self):
        print "Playing Boggle!"
        return Scoresheet()


class Scoresheet:

    def dedupe(self):
        print "Deduping..."
        return self

    def alphabetize(self):
        print "Alphabetizing..."
        return self

    def write_down(self, filename):
        print "Writing answers to %s..." % filename


if __name__ == '__main__':
    main()
