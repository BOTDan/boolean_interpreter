40# Import all the boolean code
from op_and import *
from op_or  import *
from op_not import *
from op_var import *
from op_con import *
from op_bra import *

# Import the simplify module
import simplify

# Import the graphics module
from graphics import *
try:
    from Tkinter import Tk
    import Tkinter, Tkconstants, tkFileDialog
except ImportError:
    from tkinter import filedialog
    from tkinter import Tk

# Import the JSON module for saving/loading
import json
# Import OS module for file direcotry
import os

# A list of clickable button types
ui_clickable = ["button"]
ui_hoverable = ["button"]
ui_hovered = None
button_colours = {
    "grey": ["grey85", "grey75"],
    "red": ["red2", "red3"],
    "green": ["green2", "green3"],
    "gold": ["gold2", "gold3"],
    "dark": ["grey30", "grey40"],
    "debug_left": ["turquoise1", "turquoise3", "CadetBlue1"],
    "debug_right_sub": ["medium blue", "blue"],
    "debug_right": ["DodgerBlue2", "DodgerBlue3"],
    "debug_middle": ["DeepSkyBlue2", "DeepSkyBlue3"]
}

# Exception for erronious diagrams
class EditorError(Exception):
    def __init__(self, message, element=None):
        super().__init__(message)
        self.element = element

# Creates the editor
def createEditor():
    win = GraphWin("Circuit Builder", 1920, 1080)
    initWindow(win)

    rect = Rectangle(Point(0,0), Point(win.width, win.height))
    rect.setFill("grey8")
    rect.draw(win)

    # Draw the grid
    for x in range(250, win.width+1, 20):
        line = Line(Point(x,0), Point(x, win.height))
        line.setFill("grey18")
        line.draw(win)
    for y in range(0, win.height+1, 20):
        line = Line(Point(250, y), Point(win.width, y))
        line.setFill("grey18")
        line.draw(win)

    createPanel(win, 0, 0, 250, win.height)
    createText(win, 125, 25, "Circuit Builder", 22)
    modetext = createText(win, 125, 60, "", 10)
    createText(win, 125, 105, "Inputs", 14)
    button1 = createButton(win, 0, 120, 250, 40, "VARIABLE", lambda: setEditorMode(win, 0))
    button2 = createButton(win, 0, 160, 250, 40, "CONSTANT", lambda: setEditorMode(win, 1))
    createText(win, 125, 225, "Operators", 14)
    button3 = createButton(win, 0, 240, 250, 40, "NOT", lambda: setEditorMode(win, 2))
    button4 = createButton(win, 0, 280, 250, 40, "AND", lambda: setEditorMode(win, 3))
    button5 = createButton(win, 0, 320, 250, 40, "OR", lambda: setEditorMode(win, 4))
    createText(win, 125, 385, "Tools", 14)
    button6 = createButton(win, 0, 400, 250, 40, "OUTPUT", lambda: setEditorMode(win, 5))
    button7 = createButton(win, 0, 440, 250, 40, "LINK", lambda: setEditorMode(win, 6))
    button8 = createButton(win, 0, 480, 250, 40, "DELETE", lambda: setEditorMode(win, 7))
    button9 = createButton(win, 0, 520, 250, 40, "UNLINK", lambda: setEditorMode(win, 8))
    button10 = createButton(win, 0, 560, 250, 40, "DEBUG", lambda: setEditorMode(win, 9))
    createText(win, 125, 625, "File", 14)
    createButton(win, 0, 640, 250, 40, "SAVE", lambda: editorSaveCircuit(win))
    createButton(win, 0, 680, 250, 40, "OPEN", lambda: editorOpenCircuit(win))
    createText(win, 125, 745, "Help", 14)
    createButton(win, 0, 760, 250, 40, "HELP", lambda: editorDisplayhelp(win))
    createButton(win, 0, win.height-40, 250, 40, "GENERATE", lambda: editorValidateExpression(win))
    helptext = createText(win, win.width/2+125, 30, "", 16)
    compiletext = createText(win, win.width/2+125, win.height-30, "", 16)
    compiletext[3].setTextColor("red2")

    win.editor_mode_text = modetext
    win.editor_mode_buttons = [button1, button2, button3, button4, button5, button6, button7, button8, button9, button10]
    win.editor_mode = 0
    win.editor_helptext = helptext
    win.editor_compiletext = compiletext

    win.editor_locked = False
    win.editor_lastclick = [0,0]

    win.editor_linkfrom = None
    win.editor_linkpoints = []

    win.editor_elements = []
    win.editor_links = []
    win.editor_output = None

    setEditorMode(win, 0)

    createButton(win, win.width-50, 0, 50, 30, "X", lambda: win.close(), "red")

    while win.isOpen():
        win.checkMouse()

# Updates the currently selected button
def setEditorMode(win, mode):
    global button_colours
    if not win.editor_locked:
        for button in win.editor_mode_buttons:
            button[5] = "grey"
            button[3][0].setFill(button_colours["grey"][0])
        win.editor_mode = mode
        win.editor_mode_buttons[mode][5] = "green"
        win.editor_mode_buttons[mode][3][0].setFill(button_colours["green"][1])
        for op in win.editor_elements:
            if op == win.editor_output:
                op[1][3][0].setFill(button_colours["gold"][0])
                op[1][5] = "gold"
            else:
                op[1][3][0].setFill(button_colours["grey"][0])
                op[1][5] = "grey"
        for link in win.editor_links:
            for elem in link[2]:
                elem.setFill(button_colours["grey"][0])

# Handles when the mouse is clicked within the editor window
def onEditorMousePressed(win, x, y):
    if win.editor_mode == 0:
        # Variable Mode
        if not win.editor_locked:
            # We're not already creating a variable
            win.editor_locked = True
            win.editor_lastclick = [250+round((x-250)/20)*20, round(y/20)*20]
            win.editor_helptext[3].setText("Press the letter of the Variable you'd like to create...")
    elif win.editor_mode == 1:
        # Constant Mode
        if not win.editor_locked:
            # We're not already creating a variable
            win.editor_locked = True
            win.editor_lastclick = [250+round((x-250)/20)*20, round(y/20)*20]
            win.editor_helptext[3].setText("Press number 1 or 0 to create a constant...")
    elif win.editor_mode == 2:
        # Not Mode
        editorCreateNot(win, 250+round((x-250)/20)*20, round(y/20)*20)
    elif win.editor_mode == 3:
        # And Mode
        editorCreateAnd(win, 250+round((x-250)/20)*20, round(y/20)*20)
    elif win.editor_mode == 4:
        # Or Mode
        editorCreateOr(win, 250+round((x-250)/20)*20, round(y/20)*20)
    elif win.editor_mode == 5:
        # Output Mode
        # This is handled in the button press logic
        # No code needs to run here
        pass
    elif win.editor_mode == 6:
        # Link Mode
        if win.editor_locked:
            # The user is looking to make a nice line
            win.editor_linkpoints.append([250+round((x-250)/20)*20, round(y/20)*20])
    elif win.editor_mode == 7:
        # Output Mode
        # This is handled in the button press logic
        # No code needs to run here
        pass

# Handles when a button is pressed
def onEditorKeyPressed(win, key):
    if win.editor_mode == 0 and win.editor_locked:
        # We're in Variable mode, trying to create a variable
        if key in "abcdefghijklmnopqrstuvwxyz":
            editorCreateVariable(win, win.editor_lastclick[0], win.editor_lastclick[1], key.upper())
            win.editor_locked = False
            win.editor_helptext[3].setText("")
    elif win.editor_mode == 1 and win.editor_locked:
        # We're in Variable mode, trying to create a variable
        if key in "01":
            editorCreateConstant(win, win.editor_lastclick[0], win.editor_lastclick[1], key)
            win.editor_locked = False
            win.editor_helptext[3].setText("")

# Creates a variable
def editorCreateVariable(win, x, y, letter):
    button = createButton(win, x-20, y-20, 40, 40, letter)
    operator = [
        "var",
        button,
        letter
    ]
    button[4] = lambda: editorOnOperatorClicked(win, operator)
    win.editor_elements.append(operator)

# Creates a constant
def editorCreateConstant(win, x, y, numb):
    button = createButton(win, x-20, y-20, 40, 40, numb)
    operator = [
        "con",
        button,
        numb
    ]
    button[4] = lambda: editorOnOperatorClicked(win, operator)
    win.editor_elements.append(operator)

# Creates a not
def editorCreateNot(win, x, y):
    button = createButton(win, x-20, y-20, 40, 40, "NOT")
    operator = [
        "not",
        button
    ]
    button[4] = lambda: editorOnOperatorClicked(win, operator)
    win.editor_elements.append(operator)

# Creates an and
def editorCreateAnd(win, x, y):
    button = createButton(win, x-20, y-20, 40, 40, "AND")
    operator = [
        "and",
        button
    ]
    button[4] = lambda: editorOnOperatorClicked(win, operator)
    win.editor_elements.append(operator)

# Creates an or
def editorCreateOr(win, x, y):
    button = createButton(win, x-20, y-20, 40, 40, "OR")
    operator = [
        "or",
        button
    ]
    button[4] = lambda: editorOnOperatorClicked(win, operator)
    win.editor_elements.append(operator)

# Creates a link between 2 elements
def editorCreateLink(win, elem1, elem2):
    # Draw the line between the 2
    p1x, p1y = elem1[1][1][0]+40, elem1[1][1][1]+20
    p2x, p2y = elem2[1][1][0], elem2[1][1][1]+20
    win.editor_linkpoints.insert(0, [p1x, p1y])
    win.editor_linkpoints.append([p2x, p2y])
    elems = []
    for i in range(1, len(win.editor_linkpoints)):
        p1 = win.editor_linkpoints[i-1]
        p2 = win.editor_linkpoints[i]
        line = Line(Point(p1[0], p1[1]), Point(p2[0], p2[1]))
        line.setFill("white")
        line.setWidth(3)
        line.draw(win)
        elems.append(line)
        circle = Circle(Point(p1[0], p1[1]), 4)
        circle.setOutline("white")
        circle.setFill("white")
        circle.draw(win)
        elems.append(circle)
    p1 = win.editor_linkpoints[-1]
    circle = Circle(Point(p1[0], p1[1]), 4)
    circle.setOutline("white")
    circle.setFill("white")
    circle.draw(win)
    elems.append(circle)
    # Stores the link element
    link = [elem1, elem2, elems, win.editor_linkpoints[1:-1]]
    win.editor_links.append(link)

# Operator was clicked
def editorOnOperatorClicked(win, operator):
    global button_colours
    if win.editor_mode == 5:
        if win.editor_output != None:
            win.editor_output[1][5] = "grey"
            win.editor_output[1][3][0].setFill(button_colours["grey"][0])
        win.editor_output = operator
        operator[1][5] = "gold"
        operator[1][3][0].setFill(button_colours["gold"][1])
    elif win.editor_mode == 6:
        # We're in link mode
        if win.editor_locked:
            # We're the second part of the link
            if win.editor_linkfrom != operator:
                if not operator[0] in ["var", "con"]:
                    # It's a valid link
                    # If we're connecting to a NOT, make sure it's not connected to anything else
                    if operator[0] == "not":
                        todelete = []
                        for id, link in enumerate(win.editor_links):
                            # Check if we're part of this link, and if so, delete it
                            if link[1] == operator:
                                for elem in link[2]:
                                    elem.undraw()
                                todelete.append(id)
                        todelete.sort(reverse=True)
                        for id in todelete:
                            del win.editor_links[id]
                    editorCreateLink(win, win.editor_linkfrom, operator)
            win.editor_linkfrom = None
            win.editor_linkpoints = []
            win.editor_locked = False
            win.editor_helptext[3].setText("")
        else:
            # We're the first part of the link
            win.editor_helptext[3].setText("Click on the operator you would like to input to...")
            win.editor_linkfrom = operator
            win.editor_linkpoints = []
            win.editor_locked = True
    elif win.editor_mode == 7:
        # We're in Delete mode
        todelete = []
        for id, link in enumerate(win.editor_links):
            # Check if we're part of this link, and if so, delete it
            if link[0] == operator or link[1] == operator:
                for elem in link[2]:
                    elem.undraw()
                todelete.append(id)
        todelete.sort(reverse=True)
        for id in todelete:
            del win.editor_links[id]
        if win.editor_output == operator:
            win.editor_output = None
        win.editor_elements.remove(operator)
        undrawElement(win, operator[1])
    elif win.editor_mode == 8:
        # We're in unlink mode
        if win.editor_locked:
            # We're looking for the element to unlink
            if win.editor_linkfrom != operator:
                todelete = []
                for id, link in enumerate(win.editor_links):
                    if link[0] == win.editor_linkfrom and link[1] == operator:
                        todelete.append(id)
                todelete.sort(reverse=True)
                for id in todelete:
                    for elem in win.editor_links[id][2]:
                        elem.undraw()
                    del win.editor_links[id]
                win.editor_linkfrom = None
                win.editor_locked = False
                win.editor_helptext[3].setText("")
        else:
            # We're selecting the first item to unlink
            win.editor_helptext[3].setText("Click on the operator you would like to unlink from...")
            win.editor_linkfrom = operator
            win.editor_locked = True
    elif win.editor_mode == 9:
        # We're in DEBUG mode
        # Reset every element
        for op in win.editor_elements:
            if op == win.editor_output:
                op[1][3][0].setFill(button_colours["gold"][0])
                op[1][5] = "gold"
            else:
                op[1][3][0].setFill(button_colours["dark"][0])
                op[1][5] = "dark"
        for link in win.editor_links:
            for elem in link[2]:
                elem.setFill(button_colours["dark"][0])
        # Colour the clicked element green
        operator[1][3][0].setFill(button_colours["debug_middle"][0])
        operator[1][5] = "debug_middle"
        # Find all the elements in front and behind this element
        for link in win.editor_links:
            if link[1] == operator:
                # Colour the links light blue
                for elem in link[2]:
                    elem.setFill(button_colours["debug_left"][0])
                # Colour the operator
                link[0][1][3][0].setFill(button_colours["debug_left"][0])
                link[0][1][5] = "debug_left"
                editorColourBackwards(win, link[0])
            elif link[0] == operator:
                # Colour the links light blue
                for elem in link[2]:
                    elem.setFill(button_colours["debug_right"][0])
                # Colour the operator
                link[1][1][3][0].setFill(button_colours["debug_right"][0])
                link[1][1][5] = "debug_right"
                editorColourForwards(win, link[1])
    else:
        operator[1][3][0].setFill("blue")

# Recursively colours from a node backwards
def editorColourBackwards(win, element):
    global button_colours
    new_elems = []
    for link in win.editor_links:
        if link[1] == element:
            link[0][1][3][0].setFill(button_colours["grey"][0])
            link[0][1][5] = "grey"
            for elem in link[2]:
                elem.setFill(button_colours["grey"][0])
            if not elem in new_elems:
                new_elems.append(link[0])
    for elem in new_elems:
        editorColourBackwards(win, elem)

# Recursively colours from a node forwards
def editorColourForwards(win, element):
    global button_colours
    new_elems = []
    for link in win.editor_links:
        if link[0] == element:
            link[1][1][3][0].setFill(button_colours["debug_right_sub"][0])
            link[1][1][5] = "debug_right_sub"
            for elem in link[2]:
                elem.setFill(button_colours["debug_right_sub"][0])
            if not elem in new_elems:
                new_elems.append(link[1])
    for elem in new_elems:
        editorColourForwards(win, elem)

# Makes sure the logic is sound and generates an expression from it
def editorValidateExpression(win):
    if win.editor_output == None:
        win.editor_compiletext[3].setText("You have not selected an output node!")
    else:
        try:
            output = editorGenerateExpression(win, win.editor_output)
            win.editor_compiletext[3].setText("")
            popup = createPanel(win, 0, win.height/2-120, win.width, 240)

            # text elements to display the final result
            exp1 = simplify.prettyPrint(output)
            exp2 = simplify.prettyPrint(simplify.simplify(output))
            title1 = createText(win, win.width/2, win.height/2-100, "Generated Expression", 24)
            expression = createText(win, win.width/2, win.height/2-70, exp1, 20)
            copy1 = createButton(win, win.width/2-75, win.height/2-45, 150, 40, "Copy to Clipboard", lambda: copyToClipboard(exp1), "grey")
            title2 = createText(win, win.width/2, win.height/2+20, "Simplified Expression", 24)
            simplified = createText(win, win.width/2, win.height/2+50, exp2, 20)
            copy2 = createButton(win, win.width/2-75, win.height/2+75, 150, 40, "Copy to Clipboard", lambda: copyToClipboard(exp2), "grey")

            close = createButton(win, win.width-50, win.height/2+-120, 50, 30, "X", None, "red")

            close[4] = lambda: undrawElements(win, popup, title1, title2, expression, simplified, copy1, copy2, close)
        except EditorError as e:
            win.editor_compiletext[3].setText(e)
            if e.element:
                e.element[1][3][0].setFill("red")

# Creates the help popup
def editorDisplayhelp(win):
    popup = createPanel(win, 0, win.height/2-120, win.width, 240)
    title = createText(win, win.width/2, win.height/2-100, "HELP", 24)
    help1 = createText(win, win.width/2, win.height/2-70, "Create letters (A) and numbers (0/1) using the VARIABLE/CONSTANT tools.", 20)
    help2 = createText(win, win.width/2, win.height/2-47, "Click where you'd like something to appear then press the key of the desired letter/number.", 20)
    help3 = createText(win, win.width/2, win.height/2-24, "Create operators by choosing an operator and clicking on the grid.", 20)
    help4 = createText(win, win.width/2, win.height/2+10, "Link them together using the LINK tool.", 20)
    help5 = createText(win, win.width/2, win.height/2+33, "Click firstly on the node you want to get the output of, then what it should input to (normally left-to-right).", 20)
    help6 = createText(win, win.width/2, win.height/2+70, "To then get the expression at a node, click on it using the OUTPUT tool then press GENERATE.", 20)

    close = createButton(win, win.width-50, win.height/2+-120, 50, 30, "X", None, "red")

    close[4] = lambda: undrawElements(win, popup, title, help1, help2, help3, help4, help5, help6, close)

# Copies a string to the clipboard
def copyToClipboard(string):
    r = Tk()
    r.withdraw()
    r.clipboard_clear()
    r.clipboard_append(string)
    r.update() # now it stays on the clipboard after the window is closed
    r.destroy()

# Saves the current circuit
def editorSaveCircuit(win):
    if not os.path.exists("circuits"):
        os.makedirs("circuits")
    f = filedialog.asksaveasfile(initialdir=os.path.dirname(os.path.realpath(__file__))+"/circuits", title="Select file", defaultextension=".pycircuit", filetypes=(("Python Circuits","*.pycircuit"),("All files","*.*")))
    if f is None:
        return
    operators = []
    for operator in win.editor_elements:
        new = {
            "type": operator[0],
            "x": operator[1][1][0]+20,
            "y": operator[1][1][1]+20
        }
        if operator[0] in ["con", "var"]:
            new["value"] = operator[2]
        operators.append(new)
    links = []
    for link in win.editor_links:
        new = {
            "from": win.editor_elements.index(link[0]),
            "to": win.editor_elements.index(link[1]),
            # Add path support later
            "path": [{"x": x[0], "y": x[1]} for x in link[3]]
        }
        links.append(new)
    tosave = {
        "operators": operators,
        "links": links
    }
    texttosave = json.dumps(tosave)
    f.write(texttosave)
    f.close()

# Loads a new circuit
def editorOpenCircuit(win):
    if not os.path.exists("circuits"):
        os.makedirs("circuits")
    f = filedialog.askopenfilename(initialdir=os.path.dirname(os.path.realpath(__file__))+"/circuits", title="Select file", filetypes=(("Python Circuits","*.pycircuit"),("All files","*.*")))
    if f is None or f == "":
        return
    # Open the file from the given filename
    file = open(f, "r")
    data = json.loads(file.read())
    # Clear out links
    for link in win.editor_links:
        for elem in link[2]:
            elem.undraw()#
    # Clear out operators
    for operator in win.editor_elements:
        undrawElement(win, operator[1])
    # Reset variables
    win.editor_elements = []
    win.editor_links = []
    win.editor_output = None
    win.editor_linkfrom = None
    win.editor_linkpoints = []
    win.editor_locked = False
    # Generate each node
    for item in data["operators"]:
        if item["type"] == "not":
            editorCreateNot(win, item["x"], item["y"])
        elif item["type"] == "and":
            editorCreateAnd(win, item["x"], item["y"])
        elif item["type"] == "or":
            editorCreateOr(win, item["x"], item["y"])
        elif item["type"] == "con":
            editorCreateConstant(win, item["x"], item["y"], item["value"])
        elif item["type"] == "var":
            editorCreateVariable(win, item["x"], item["y"], item["value"])
    # Generate the links
    for link in data["links"]:
        if link["from"] < len(win.editor_elements) and link["to"] < len(win.editor_elements):
            win.editor_linkpoints = [[x["x"], x["y"]] for x in link["path"]]
            editorCreateLink(win, win.editor_elements[link["from"]], win.editor_elements[link["to"]])
    # Created


# generates an expression from the editor
def editorGenerateExpression(win, operator):
    op = operator[0]
    if op == "not":
        # Find the first backlink from the NOT
        link = None
        for test in win.editor_links:
            if test[1] == operator:
                link = test
                break
        if link != None:
            return op_not(editorGenerateExpression(win, link[0]))
        else:
            raise EditorError("NOT operator not connected!", operator)
    elif op == "and":
        # Find all links that apply to this AND
        links = []
        for test in win.editor_links:
            if test[1] == operator:
                links.append(test[0])
        if len(links) >= 2:
            operands = [editorGenerateExpression(win, x) for x in links]
            return op_and(*operands)
        else:
            raise EditorError("AND operator only has {} links. 2 or more required.".format(len(links)), operator)
    elif op == "or":
        # Find all links that apply to this OR
        links = []
        for test in win.editor_links:
            if test[1] == operator:
                links.append(test[0])
        if len(links) >= 2:
            operands = [editorGenerateExpression(win, x) for x in links]
            return op_or(*operands)
        else:
            raise EditorError("OR operator only has {} links. 2 or more required.".format(len(links)), operator)
    elif op == "var":
        return op_var(operator[2])
    elif op == "con":
        return op_con(operator[2])

# Initialises a window to use the UI system
def initWindow(win):
    # Make it fullscreen
    win.master.attributes("-fullscreen", True)
    win.master.iconify()
    win.master.iconbitmap(os.path.dirname(os.path.realpath(__file__))+"/icon.ico")
    # Make sure the canvas knows the new width and height
    win.place(x=0, y=0, w=win.master.winfo_width(), h=win.master.winfo_height())
    win.width, win.height = win.master.winfo_width(), win.master.winfo_height()
    # Store a list of all the UI elements
    win.ui_elements = []

    # Handles when the mouse is pressed
    win.bind("<ButtonPress-1>", lambda e: onMousePressed(win, e.x, e.y))
    win.bind("<Motion>", lambda e: onMouseMoved(win, e.x, e.y))
    win.bind_all("<Key>", lambda e: onKeyPressed(win, e.char))
    win.bind_all("<Escape>", lambda e: onEscapePressed(win))

# Undraws a UI element
def undrawElement(win, element):
    if isinstance(element[3], list):
        for elem in element[3]:
            elem.undraw()
    else:
        element[3].undraw()
    win.ui_elements.remove(element)

# Undraws a list of elements
def undrawElements(win, *args):
    for elem in args:
        undrawElement(win, elem)

# Creates a Panel UI element (basically a rectangle)
def createPanel(win, x, y, w, h):
    bg = Rectangle(Point(x, y), Point(x+w, y+h))
    bg.setFill("grey25")
    bg.setOutline("grey30")
    bg.draw(win)

    element = [
        "panel",
        [x,y],
        [w,h],
        bg
    ]
    win.ui_elements.append(element)
    return element

# Creates a text element (basically text)
def createText(win, x, y, name="NO NAME", size=20):
    text = Text(Point(x, y), name)
    text.setSize(size)
    text.setTextColor("white")
    text.draw(win)

    element = [
        "text",
        [x,y],
        size,
        text
    ]
    win.ui_elements.append(element)
    return element

# Creates a button UI elements
def createButton(win, x, y, w, h, name="NO TEXT", callback=None, col="grey"):
    global button_colours
    bg = Rectangle(Point(x, y), Point(x+w, y+h))
    bg.setFill(button_colours[col][0])
    bg.setOutline("black")
    bg.draw(win)

    text = Text(Point(x+w/2, y+h/2), name)
    text.setTextColor("black")
    text.draw(win)

    element = [
        "button",
        [x,y],
        [w,h],
        [bg, text],
        callback,
        col
    ]
    win.ui_elements.append(element)
    return element

# Handles when a button is pressed within the window
def onKeyPressed(win, char):
    onEditorKeyPressed(win, char)

# Handles when the mouse is clicked
def onMousePressed(win, x, y):
    for element in win.ui_elements:
        if element[0] in ui_clickable:
            elem_x, elem_y = element[1][0], element[1][1]
            elem_w, elem_h = element[2][0], element[2][1]
            if (elem_x <= x <= elem_x+elem_w) and (elem_y <= y <= elem_y+elem_h):
                # We've clicked on an object
                if element[0] == "button":
                    # Button just has a callback
                    if element[4]:
                        element[4]()
                return
    onEditorMousePressed(win, x, y)

# Handles when the mouse moves
def onMouseMoved(win, x, y):
    global ui_hovered
    for element in win.ui_elements:
        if element[0] in ui_hoverable:
            elem_x, elem_y = element[1][0], element[1][1]
            elem_w, elem_h = element[2][0], element[2][1]
            if (elem_x <= x <= elem_x+elem_w) and (elem_y <= y <= elem_y+elem_h):
                if ui_hovered != None and ui_hovered != element:
                    unhoverElement(win, ui_hovered)
                # We've hovered over a hoverable object
                hoverElement(win, element)
                ui_hovered = element
                return
    if ui_hovered != None:
        unhoverElement(win, ui_hovered)
        ui_hovered = None

# Hovers an element
def hoverElement(win, element):
    global button_colours
    if element[0] == "button":
        element[3][0].setFill(button_colours[element[5]][1])

# Unhoveres an element
def unhoverElement(win, element):
    global button_colours
    if element[0] == "button":
        element[3][0].setFill(button_colours[element[5]][0])

# Handles when a button is pressed
def onEscapePressed(win):
    win.close()
