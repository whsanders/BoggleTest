# boggle_pad.py
#
# A simple notepad intended to be used for Boggle. Words can be jotted down
# as the player sees them, and at any time the pad can be told to sort itself 
# (removing duplicates and alphabetizing the internal store) or to write itself
# to file.
# 
# Supports call chaining, e.g.
#
#     pad = BogglePad()
#     pad.jot("foo").jot("bar")

class BogglePad:
    __lines = []

    def jot(self, line):
        self.__lines.append(line)
        return self

    def dedupe_and_alphabetize(self):
        print self.__lines
        print "Deduping..."
        lines = list(set(self.__lines))
        print lines
        print "Alphabetizing..."
        lines.sort()
        print lines
        self.__lines = lines
        return self

    def write_down(self, filename):
        print "Writing to %s..." % filename
        print self.__lines



