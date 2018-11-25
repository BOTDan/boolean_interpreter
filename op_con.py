# CONSTANT CLASS
# Stores a single constant for calculations later

from op import *

class op_con(op):
    # Init function - Stores data pertaining to the class
    def __init__(self, *argv):
        super(op_con, self).__init__(*argv)

    # Returns the type of this operator
    def getType(self):
        return "con"

    # Calculates the value of this operator given a dictionary of variable values
    def calcValue(self, args):
        return int(self.getOperand(0))

    # Used to see if 2 AND statements are the same. Ignores operand order
    def __eq__(self, other):
        if other == None: return False
        if other.getType() != "con": return False
        return self.getOperand(0) == other.getOperand(0)

    # Used to print this class out nicely
    def __str__(self):
        return "[CON: {}]".format(self.getOperand(0))
