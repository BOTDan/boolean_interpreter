from op_and import *
from op_or  import *
from op_not import *
from op_var import *
from op_con import *
from op_bra import *

import copy

# Returns a list of positions of operand sthat match the one given
# Returns an empty list if none are found
def findFirstDuplicate(expression, id):
    # Make sure it's an AND or OR, otherwise it's invalid
    if expression.getType() in ["and", "or"]:
        testfor = expression.getOperand(id)
        for i, operand in enumerate(expression.getOperands()):
            if i != id and operand == testfor:
                return i
    return None

# Returns the first operand that is the NOT of the given operand
def findFirstOpposite(expression, id):
    # Make sure it's an AND or OR, otherwise it's invalid
    if expression.getType() in ["and", "or"]:
        testfor = removeNots(op_not(expression.getOperand(id)))
        for i, operand in enumerate(expression.getOperands()):
            if i != id and operand == testfor:
                return i
    return None

# Returns the first operand that contains part/all of the given operand
def findFirstContaining(expression, id, opposite=False, custom=None):
    # Make sure it's an AND or an OR, otherwise it's invlid
    if expression.getType() in ["and", "or"]:
        testfor = expression.getOperand(id)
        if opposite:
            testfor = removeNots(op_not(testfor))
        if custom:
            testfor = custom
        if testfor.getType() in ["and", "or"]:
            for i, operand in enumerate(expression.getOperands()):
                if i != id and operand.getType() == testfor.getType():
                    copy = testfor.getOperands()[:]
                    for var in operand.getOperands():
                        try:
                            del copy[copy.index(var)]
                        except ValueError:
                            continue
                    if len(copy) == 0:
                        return i
        elif testfor.getType() in ["not", "var", "con"]:
            for i, operand in enumerate(expression.getOperands()):
                if i != id:
                    if operand.getType() in ["not", "var", "con"]:
                        if operand == testfor:
                            return i
                    elif operand.getType() == "and":
                        for suboperand in operand.getOperands():
                            if suboperand == testfor:
                                return i
    return None


# Removes constants from an expression
# May create more constants that need removing, so should be called
# again if any changes are detected
def removeConstants(expression):
    if expression.getType() == "and":
        for i, operand in enumerate(expression.getOperands()):
            if operand.getType() == "con":
                if operand.getOperand(0) == "0":
                    # If the operand is a 0 in an AND, then it always equates to 0
                    return op_con("0")
                else:
                    # Remove the 1 from the expression and start again
                    expression.removeOperand(i)
                    return removeConstants(expression)
            else:
                expression.setOperand(i, removeConstants(operand))
        return expression
    elif expression.getType() == "or":
        for i, operand in enumerate(expression.getOperands()):
            if operand.getType() == "con":
                if operand.getOperand(0) == "1":
                    # If the operand is a 1 in an OR, then it always equates to 1
                    return op_con("1")
                else:
                    # Remove the 0 from the expression and start again
                    expression.removeOperand(i)
                    return removeConstants(expression)
            else:
                expression.setOperand(i, removeConstants(operand))
        return expression
    else:
        return expression

# Removes unnecessary NOTs from an expression
def removeNots(expression):
    if expression.getType() == "not":
        operand = removeNots(expression.getOperand(0))
        if operand.getType() == "con":
            return op_con(str(-int(operand.getOperand(0))+1))
        elif operand.getType() == "not":
            return operand.getOperand(0)
        else:
            return op_not(operand)
    elif expression.getType() in ["and", "or"]:
        for i, operand in enumerate(expression.getOperands()):
            expression.setOperand(i, removeNots(operand))
        return expression
    else:
        return expression

# Removes duplicates from an expression
def removeDuplicates(expression):
    if expression.getType() in ["and", "or", "not"]:
        for i, operand in enumerate(expression.getOperands()):
            expression.setOperand(i, removeDuplicates(operand))
    if expression.getType() in ["and", "or"]:
        for i in range(expression.getOperandCount()):
            id = findFirstDuplicate(expression, i)
            if id != None:
                expression.removeOperand(id)
                return removeDuplicates(expression)
    return expression

# Removes opposites from en expression. e.g. A + A' = A
def removeOpposites(expression):
    if expression.getType() in ["and", "or", "not"]:
        for i, operand in enumerate(expression.getOperands()):
            expression.setOperand(i, removeOpposites(operand))
    if expression.getType() == "and":
        for i, operand in enumerate(expression.getOperands()):
            id = findFirstOpposite(expression, i)
            if id != None:
                expression = op_con("0")
                return expression
    if expression.getType() == "or":
        for i, operand in enumerate(expression.getOperands()):
            id = findFirstOpposite(expression, i)
            if id != None:
                #print("{} is the opposite of {}".format(expression.getOperand(i), expression.getOperand(id)))
                expression = op_con("1")
                return expression
    return expression

# Removes parts of an expression that contain other, smaller parts
def removeSubduplicates(expression):
    if expression.getType() in ["and", "or", "not"]:
        for i, operand in enumerate(expression.getOperands()):
            expression.setOperand(i, removeSubduplicates(operand))
    if expression.getType() == "or":
        for i, operand in enumerate(expression.getOperands()):
            id = findFirstContaining(expression, i)
            if id != None:
                expression.removeOperand(id)
                return removeSubduplicates(expression)
            else:
                #print("{} not found in {}".format(operand, expression))
                pass
    return expression

# Removes parts of an expression that contain the NOT of another
def removeSubopposites(expression):
    if expression.getType() in ["and", "or", "not"]:
        for i, operand in enumerate(expression.getOperands()):
            expression.setOperand(i, removeSubopposites(operand))
    if expression.getType() == "or":
        for i, operand in enumerate(expression.getOperands()):
            id = findFirstContaining(expression, i, True)
            if id != None:
                # We've found an expression containing our thing
                container = expression.getOperand(id)
                testfor = removeNots(op_not(operand))
                if container.getType() in ["and", "or"]:
                    for j, suboperand in enumerate(container.getOperands()):
                        if suboperand == testfor:
                            container.removeOperand(j)
                            break
                else:
                    expression.removeOperand(id)
                return removeSubopposites(expression)
            else:
                #print("{} not found in {}".format(operand, expression))
                pass
    return expression

# Removes parts of an expression if they are the same bar 1 opposite
# THIS FUNCTION IS TERRIBLE
# I'VE COMPLETELY MADE UP THIS RULE BUT I BELIEVE
# IT'S AN ALMALGAMATION OF A FEW RULES
def removeMagic(expression):
    if expression.getType() in ["and", "or", "not"]:
        for i, operand in enumerate(expression.getOperands()):
            expression.setOperand(i, removeMagic(operand))
    if expression.getType() == "or":
        for i, operand in enumerate(expression.getOperands()):
            if operand.getType() == "and":
                for j, suboperand in enumerate(operand.getOperands()):
                    # Invert 1 part of the AND and look for matches
                    newand = copy.deepcopy(operand)
                    newand.setOperand(j, removeNots(op_not(suboperand)))
                    id = findFirstContaining(expression, i, False, newand)
                    if id != None:
                        # We've got a lot to remove
                        container = expression.getOperand(id)
                        # The container should always be an OR
                        if container.getType() == "and":
                            # Remove the notted version of out tets
                            for l, test in enumerate(container.getOperands()):
                                if test == removeNots(op_not(suboperand)):
                                    container.removeOperand(l)
                                    break
                            return expression
    return expression

# Removes redundancy created with expandAnds
def removeRedundancy(expression):
    if expression.getType() in ["and", "or", "not"]:
        for i, operand in enumerate(expression.getOperands()):
            expression.setOperand(i, removeRedundancy(operand))
    if expression.getType() in ["and", "or"]:
        if expression.getOperandCount() == 1:
            return expression.getOperand(0)
    return expression

# Makes sure therte's no ORs within an OR statement
def expandOrs(expression):
    if expression.getType() in ["and", "or", "not"]:
        for i, operand in enumerate(expression.getOperands()):
            expression.setOperand(i, expandOrs(operand))
    if expression.getType() == "or":
        for i, operand in enumerate(expression.getOperands()):
            if operand.getType() == "or":
                for suboperand in operand.getOperands():
                    expression.addOperand(suboperand)
                expression.removeOperand(i)
                return expression
    return expression

# Implement DeMorgans Law
def expandDeMorgans(expression):
    if expression.getType() in ["and", "or", "not"]:
        for i, operand in enumerate(expression.getOperands()):
            expression.setOperand(i, expandDeMorgans(operand))
    if expression.getType() == "not":
        expand = expression.getOperand(0)
        if expand.getType() == "and":
            created = []
            for operand in expand.getOperands():
                created.append(op_not(operand))
            return op_or(*created)
        elif expand.getType() == "or":
            created = []
            for operand in expand.getOperands():
                created.append(op_not(operand))
            return op_and(*created)
    return expression


# Expands or statements that had been ANDd together
def expandAnds(expression):
    if expression.getType() in ["and", "or", "not"]:
        for i, operand in enumerate(expression.getOperands()):
            expression.setOperand(i, expandAnds(operand))
    if expression.getType() == "and":
        # Check if we need to expand
        for i in range(expression.getOperandCount()):
            operand = expression.getOperand(i)
            if i > 0:
                previous = expression.getOperand(i-1)
                if operand.getType() == "or":
                    #print("[{}] is an OR".format(i))
                    test = None
                    if i == 1:
                        #print("merging3 {} with {}".format(operand, previous))
                        test = mergeOperands(operand, previous)
                    else:
                        #print("Merging {} with {}".format(operand, op_and(*expression.getOperands()[:i])))
                        test = mergeOperands(operand, op_and(*expression.getOperands()[:i]))
                    if i == expression.getOperandCount() -1:
                        return test
                    else:
                        return op_and(test, *expression.getOperands()[i+1:])
                elif previous.getType() == "or":
                    #print("[{}-1] is an OR".format(i))
                    test = None
                    if i == expression.getOperandCount()-1:
                        #print("merging4 {} with {}".format(previous, operand))
                        test = mergeOperands(previous, operand)
                    else:
                        #print("Merging2 {} with {}".format(previous, op_and(*expression.getOperands()[i:])))
                        test = mergeOperands(previous, op_and(*expression.getOperands()[i:]))
                    return test

            if operand.getType() == "and":
                # ANDs within an AND can be expanded out easily
                for suboperand in operand.getOperands():
                    expression.addOperand(suboperand)
                expression.removeOperand(i)
                return expression
    return expression

# Marges 2 operands together into 1 AND
def mergeOperands(expression1, expression2):
    created = []
    if expression1.getType() == "and":
        if expression2.getType() == "and":
            return mergeAnds(expression1, expression2)
        elif expression2.getType() == "or":
            return mergeAndOr(expression1, expression2)
        else:
            return mergeAndOther(expression1, expression2)
    elif expression1.getType() == "or":
        if expression2.getType() == "and":
            return mergeAndOr(expression2, expression1)
        elif expression2.getType() == "or":
            return mergeOrs(expression1, expression2)
        else:
            return mergeOrOther(expression1, expression2)
    else:
        if expression2.getType() == "and":
            return mergeAndOther(expression2, expression1)
        elif expression2.getType() == "or":
            return mergeOrOther(expression2, expression1)
        else:
            return op_and(expression1, expression2)

# Marges 2 ANDS
def mergeAnds(expression1, expression2):
    created = []
    created += expression1.getOperands()
    created += expression2.getOperands()
    return op_and(*created)

# Marges an AND and an OR
def mergeAndOr(expression1, expression2):
    created = []
    for i, operand in enumerate(expression2.getOperands()):
        created.append(op_and(operand, *expression1.getOperands()))
    return op_or(*created)

# Merges an AND and anything else
def mergeAndOther(expression1, expression2):
    return op_and(expression2, *expression1.getOperands())

# Marges 2 OR statements together
def mergeOrs(expression1, expression2):
    created = []
    for i, operand in enumerate(expression1.getOperands()):
        for j, operand2 in enumerate(expression2.getOperands()):
            created.append(op_and(operand, operand2))
    return op_or(*created)

# Marges an OR with anything else
def mergeOrOther(expression1, expression2):
    created = []
    for i, operand in enumerate(expression1.getOperands()):
        created.append(op_and(operand, expression2))
    return op_or(*created)

# Simplifys an expression recursively
def simplify(expression, stage="START"):
    print("Stage [{:<14}]: {}".format(stage, prettyPrint(expression)))
    initial = copy.deepcopy(expression)
        # Remove NOTs
    new = removeNots(expression)
    if new != initial: return simplify(new, "RULE 9")
        # Remove Constants
    new = removeConstants(new)
    if new != initial: return simplify(new, "RULE 1 to 4")
        # Remove Duplicates
    new = removeDuplicates(new)
    if new != initial: return simplify(new, "RULE 5 to 6")
        # Remove Opposites
    new = removeOpposites(new)
    if new != initial: return simplify(new, "RULE 7 to 8")
        # Remove Subsuplicates
    new = removeSubduplicates(new)
    if new != initial: return simplify(new, "RULE 5, 6 + 10")
        # Remove subopposites
    new = removeSubopposites(new)
    if new != initial: return simplify(new, "RULE 7, 8 + 11")
        # Remove unnecessary ORs
    new = expandOrs(new)
    if new != initial: return simplify(new, "ASSOCIATIVE")
        # Expand out touching ANDs
    new = expandAnds(new)
    if new != initial: return simplify(new, "DISTRIBUTIVE")
        # Remove redundancy caused by removeAnds
    new = removeRedundancy(new)
    if new != initial: return simplify(new, "(internal)")
        # Removes magic or something
    new = removeMagic(new)
    if new != initial: return simplify(new, "RULE 11")
        # Do DeMorgans Law
    new = expandDeMorgans(new)
    if new != initial: return simplify(new, "DEMORGANS")
        # Finished, return simplified thing
    return new

# Pretty prints a boolean expression
def prettyPrint(expression):
    if expression.getType() == "and":
        return "".join(prettyPrint(x) for x in expression.getOperands())
    elif expression.getType() == "or":
        return "({})".format("+".join(prettyPrint(x) for x in expression.getOperands()))
    elif expression.getType() == "not":
        if expression.getOperand(0).getType() == "and":
            return "({})'".format(prettyPrint(expression.getOperand(0)))
        else:
            return "{}'".format(prettyPrint(expression.getOperand(0)))
    elif expression.getType() in ["con", "var"]:
        return str(expression.getOperand(0))
    elif expression.getType() == "bra":
        # Should never have to print these, but just in-case
        return "({})".format(prettyPrint(expression.getOperand(0)))
