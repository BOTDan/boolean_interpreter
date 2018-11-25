# BRACKET CLASS
# Temporary class during generation to make things easier.

from op import *

class op_bra(op):
    # Init function - Stores data pertaining to the class
    def __init__(self, *argv):
        super(op_bra, self).__init__(*argv)

    # Returns the type of this operator
    def getType(self):
        return "bra"

    # Calculates the value of this operator given a dictionary of variable values
    def calcValue(self, args):
        return self.getOperand(0).calcValue(args)

    # Used to see if 2 BRACKET statements are the same. Ignores operand order
    # This is useless as brackets will be removed during the filan stages
    def __eq__(self, other):
        if other == None: return False
        if other.getType() == "bra":
            return self.getOperand(0) == other.getOperand(0)
        return self.getOperand(0) == other

    # Used to print this class out nicely
    def __str__(self):
        return "[BRA: {}]".format(", ".join([str(x) for x in self.getOperands()]))
