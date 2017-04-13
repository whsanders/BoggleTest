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

    def count(self):
        return len(self.__lines)

    def dedupe_and_alphabetize(self):
        print "Deduping...",
        lines = list(set(self.__lines))
        print " %d redundant items" % (self.count() - len(lines))

        print "Alphabetizing..."
        lines.sort()

        self.__lines = lines
        return self

    def write_down(self, filename):
        print "Writing %d items to %s..." % (self.count(), filename)
        output = "\n".join(self.__lines)
        print output
        file = open(filename, 'w')
        file.write(output + '\n')
        file.close()



