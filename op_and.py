# AND CLASS
# Stores a collection of operands all to be AND'd together.

from op import *

class op_and(op):
    # Init function - Stores data pertaining to the class
    def __init__(self, *argv):
        super(op_and, self).__init__(*argv)

    # Returns the type of this operator
    def getType(self):
        return "and"

    # Calculates the value of this operator given a dictionary of variable values
    def calcValue(self, args):
        output = 1
        for operand in self.getOperands():
            output = output & operand.calcValue(args)
        return output

    # Used to see if 2 AND statements are the same. Ignores operand order
    def __eq__(self, other):
        if other == None: return False
        if other.getType() != "and": return False
        if len(self.getOperands()) != len(other.getOperands()): return False
        copy = self.getOperands()[:]
        for var in other.getOperands():
            try:
                del copy[copy.index(var)]
            except ValueError:
                print("Failed looking for {} in {}".format(var, copy))
                return False
        return len(copy) == 0

    # Used to print this class out nicely
    def __str__(self):
        return "[AND: {}]".format(", ".join([str(x) for x in self.getOperands()]))
