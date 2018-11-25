# NOT CLASS
# Stores a single operator to be NOT'd

from op import *

class op_not(op):
    # Init function - Stores data pertaining to the class
    def __init__(self, *argv):
        super(op_not, self).__init__(*argv)

    # Returns the type of this operator
    def getType(self):
        return "not"

    # Calculates the value of this operator given a dictionary of variable values
    def calcValue(self, args):
        return -self.getOperand(0).calcValue(args)+1

    # Used to see if 2 AND statements are the same. Ignores operand order
    def __eq__(self, other):
        if other == None: return False
        if other.getType() != "not": return False
        return self.getOperand(0) == other.getOperand(0)

    # Used to print this class out nicely
    def __str__(self):
        return "[NOT: {}]".format(str(self.getOperand(0)))
