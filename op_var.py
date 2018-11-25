# VARIABLE CLASS
# Stores a single varible for calculations later

from op import *

class op_var(op):
    # Init function - Stores data pertaining to the class
    def __init__(self, *argv):
        super(op_var, self).__init__(*argv)

    # Returns the type of this operator
    def getType(self):
        return "var"

    # Calculates the value of this operator given a dictionary of variable values
    def calcValue(self, args):
        return args[self.getOperand(0)]

    # Used to see if 2 AND statements are the same. Ignores operand order
    def __eq__(self, other):
        if other == None: return False
        if other.getType() != "var": return False
        return self.getOperand(0) == other.getOperand(0)

    # Used to print this class out nicely
    def __str__(self):
        return "[VAR: {}]".format(self.getOperand(0))
