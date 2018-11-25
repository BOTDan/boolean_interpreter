# Operator base class
# Contains all the variables and methods a default operator will need

class op:
    # Init function - Stores data pertaining to the class
    def __init__(self, *argv):
        self.operands = []
        if len(argv) <= 0:
            ValueError("Not enough arguments for operator OR")
        self.operands = list(argv)

    # Returns the type of this operator
    def getType(self):
        # OVERWRITE
        return "base"

    # Returns how many variables the AND invovle
    def getOperandCount(self):
        return len(self.operands)

    # Returns an operand at the given index
    def getOperand(self, index):
        if len(self.operands) < index:
            IndexError("Operand #{} does not exist.".format(index))
        return self.operands[index]

    # Returns all the operands
    def getOperands(self):
        return self.operands

    # Adds an operand to the AND statement
    def addOperand(self, val):
        self.operands.append(val)

    # Sets an operand at the given index
    def setOperand(self, index, val):
        self.operands[index] = val

    # Deletes an operand at the given index
    def removeOperand(self, index):
        del self.operands[index]

    # Calculates the value of this operator given a dictionary of variable values
    def calcValue(self, args):
        # OVERWRITE
        return 0

    # Used to see if 2 AND statements are the same. Ignores operand order
    def __eq__(self, other):
        # OVERWRITE
        return False

    # Used to print this class out nicely
    def __str__(self):
        # OVERWRITE
        return "BASE"
