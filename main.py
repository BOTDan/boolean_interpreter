from op_and import *
from op_or  import *
from op_not import *
from op_var import *
from op_con import *
from op_bra import *

import simplify
import ui

import itertools

# Generates an expression given a boolean algebra string
def generateExpression(expression, last=None):
    # Don't do anything if we've been given a blank expression
    if len(expression) <= 0:
        return last
    char = expression[0]
    if last == None:
        # If we're at the beginning of the expression, we can only accept A,1 or (
        if char.isalpha():
            return generateExpression(expression[1:], op_var(char))
        elif char.isdigit():
            return generateExpression(expression[1:], op_con(char))
        elif char == "(":
            length = calcBracketLength(expression[1:])
            return generateExpression(expression[length+1:], op_bra(generateExpression(expression[1:length])))
        else:
            raise ValueError("Expression is Invalid!")
    else:
        # We're mid-expression
        if char.isalpha() or char.isdigit():
            if last.getType() == "or":
                last.setOperand(-1, op_and(last.getOperand(-1), generateExpression(expression[1:])))
                return last
            elif last.getType() == "and":
                last.addOperand(generateExpression(char))
                return generateExpression(expression[1:], last)
            else:
                return generateExpression(expression[1:], op_and(last, generateExpression(expression[0])))
        elif char == "(":
            length = calcBracketLength(expression[1:])
            if last.getType() == "and":
                last.addOperand(op_bra(generateExpression(expression[1:length])))
                return generateExpression(expression[length+1:], last)
            else:
                return generateExpression(expression[length+1:], op_and(last, op_bra(generateExpression(expression[1:length]))))
        elif char == "+":
            if last.getType() == "or":
                last.addOperand(generateExpression(expression[1:]))
                return last
            else:
                new = generateExpression(expression[1:])
                if new.getType() == "or":
                    return op_or(last, *new.getOperands())
                return op_or(last, new)
        elif char == "'":
            if last.getType() in ["bar", "var", "con", "not"]:
                return generateExpression(expression[1:], op_not(last))
            else:
                last.setOperand(-1, op_not(last.getOperand(-1)))
                return generateExpression(expression[1:], last)
        else:
            raise ValueError("Expression is Invalid!")

# Calculates how long a bracket spans for
def calcBracketLength(expression):
    brackets, i = 1, 0
    while brackets > 0:
        if i >= len(expression):
            raise ValueError("Expression has invalid brackets")
        elif expression[i] == "(":
            brackets += 1
        elif expression[i] == ")":
            brackets -= 1
        i += 1
    return i

# Removes all bracket operators from an expression
# Makes comparisons much easier and they're unnecessary
def removeBrackets(expression):
    if expression.getType() == "bra":
        return removeBrackets(expression.getOperand(0))
    elif not expression.getType() in ["var", "con"]:
        for i, operand in enumerate(expression.getOperands()):
            expression.setOperand(i, removeBrackets(operand))
    return expression


# Generates a set of variables for the given expression
def generateVariableList(expression, variables=set()):
    variables = variables or set()
    if expression.getType() == "var":
        variables.add(expression.getOperand(0))
    elif expression.getType() != "con":
        for operand in expression.getOperands():
            test = generateVariableList(operand)
            variables = variables.union(test)
    return variables

# Generates a truth table list
def generateTruthTableInputs(count):
    # Convert everything to lists instead of tuples
    return list([list(i) for i in itertools.product([0, 1], repeat=count)])

# Calculates the truth table for a given expression
def calcTruthTable(expression):
    variables = generateVariableList(expression)
    inputs = generateTruthTableInputs(len(variables))
    outputs = []
    for input_set in inputs:
        # Build dictionary of values
        checks = {}
        for i, key in enumerate(variables):
            checks[key] = input_set[i]

        # Does the calculation
        outputs.append(expression.calcValue(checks))
    # Print out the result
    print(" {} | X".format(" | ".join(variables)))
    for i, result in enumerate(outputs):
        print(" {} | {}".format(" | ".join([str(x) for x in inputs[i]]), result))

# Calculates if 2 expressions are equivalent
def isEquivalent(expression1, expression2):
    vars1 = generateVariableList(expression1)
    vars2 = generateVariableList(expression2)
    variables = set().union(vars1, vars2)
    inputs = generateTruthTableInputs(len(variables))
    # Loop through every possible combination
    for input_set in inputs:
        checks = {}
        for i, key in enumerate(variables):
            checks[key] = input_set[i]

        if expression1.calcValue(checks) != expression2.calcValue(checks):
            print("Failed at {}".format(checks))
            return False
    return True

# Calculates the value of an expression after variable values have been given
def calcValue(expression):
    variables = generateVariableList(expression)
    inputs = {}
    for i in sorted(variables):
        inputs[i] = input("[{}] = ".format(i))
        while not inputs[i] in ["0", "1"]:
            print("Error: Only 0 or 1 allowed.")
            inputs[i] = input("[{}] = ".format(i))
        inputs[i] = int(inputs[i])
    return expression.calcValue(inputs)

# Main program. Creates a command-line-type program
def main():
    print("Boolean Algebra Utility")
    print("Commands: 'table', 'eval', 'same', 'simplify', 'ui' and 'quit'")
    print("TO USE THE CIRCUIT UI, TYPE 'ui'")
    print("TO END THE PROGRAM, TYPE 'quit'")
    while True:
        command = input("\n[COMMAND] > ")

        if command.lower() in ["table", "truth", "truthtable"]:
            print("\nEnter the boolean expression to generate a truth table for it.")
            expression = generateExpression(input("[BOOLEAN] > "))
            calcTruthTable(expression)

        elif command.lower() in ["eval", "evaluate", "calc", "calculate", "calcvalue"]:
            print("\nEnter the boolean expression to get the output of.")
            expression = generateExpression(input("[BOOLEAN] > "))
            print("OUTPUT = {}".format(calcValue(expression)))

        elif command.lower() in ["equiv", "equivalent", "same", "compare"]:
            print("\nEnter the 2 boolean expressions to comapre.")
            expression1 = generateExpression(input("[BOOLEAN #1] > "))
            expression2 = generateExpression(input("[BOOLEAN #2] > "))
            print(isEquivalent(expression1, expression2) and "The 2 expressions are equivalent" or "The 2 expressions are not equivalent")

        elif command.lower() in ["simplify", "simple"]:
            print("\nEnter the expression to simplify.")
            expression = removeBrackets(generateExpression(input("[BOOLEAN] > ")))
            print("SIMPLIFIED = {}".format(simplify.prettyPrint(simplify.simplify(expression))))

        elif command.lower() in ["ui", "builder", "creator"]:
            ui.createEditor()

        elif command.lower() in ["stop", "quit", "close", "end", "leave"]:
            print("\nQuitting...")
            break

# Run the command-line-like tool
main()

#ui.createEditor()

'''
test = removeBrackets(generateExpression("0+A+(1BC0)"))
print(test)
test = simplify.removeNots(test)
print(test)
test = simplify.removeConstants(simplify.removeConstants(test))
print(test)
print("--")
test = removeBrackets(generateExpression("AB+AC+(BA)''"))
print(test)
test = simplify.removeDuplicates(simplify.removeNots(test))
print(test)
print("--")
test = removeBrackets(generateExpression("(A'+B'+C')'+(A'B'+A'C'+B'C')'"))
print("initial {}".format(test))
test = simplify.simplify(test)
print(test)
'''
