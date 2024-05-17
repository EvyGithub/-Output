from random import randint, choice
from time import sleep

# variables and stuff
direction = (1, 0) # start facing right
y = x = 0          # start in upper left corner
stack0 = []        # data storage
stack1 = []        # data storage part 2
DIRECTIONS = [(1, 0), (0, -1), (-1, 0), (0, 1)]
selectedStack = 0  # decides which stack is used (you can modify this using the ( and ) command)
maxLenLine = ""    # stores the line with the longest length

# swag functions
def interpret(file: str) -> None:
    global direction, x, y, stack0, stack1, selectedStack, maxLenLine, code
    with open(file, "r") as f:
        # process the 2D stuff and put it into a 2D list
        # also get ready for some nice list comprehension lol
        code = [list(line) for line in [line.rstrip("\n") for line in f.readlines()]]

    maxLenLine = sorted(code, key=len, reverse=True)[0]

    # fill in blank cells
    for i in code:
        try:
            # try to access each spot and if an indexerror occurs then it needs to be filled
            for index in range(len(maxLenLine)):
                i[index]
        except:
            # fill in the blank with a space
            # print("filled wank")
            i.append(" ")

    # print(code)

    # check to see whether you should care about what you're reading or not
    stringMode = 0
    string = ""

    # default marked cell
    marked = (0, 0)

    # ok, good.
    # now time to do the other stuff.
    while 1: # indefinetly
        # read instruction and do accordingly
        cmd = code[y][x]
        # get ready

        # select stack according to selectedStack
        stack = stack1 if selectedStack else stack0
        otherStack = stack0 if selectedStack else stack1

        if cmd == "X" and stringMode == 0:
            # end
            break

        # toggle stringMode
        if cmd == '"':
                # read until another " and push all characters as one string
                # or you could say this toggles stringMode
                stringMode = not stringMode

        if stringMode:
            # ignore what the character means and just add it to the string
            string += cmd
        
        else:
            # push string if it's not empty
            if string != "":
                stack.append(string[1:])
                string = ""

            if cmd == " ":
                # no-op
                pass

            # 1. IP Movement
            elif cmd == ">":
                # right
                direction = (1, 0)
            elif cmd == "<":
                # left
                direction = (-1, 0)
            elif cmd == "^":
                # up
                direction = (0, -1)
            elif cmd == "v":
                # down
                direction = (0, 1)
            elif cmd == "?":
                # random direction
                direction = choice(DIRECTIONS)
            elif cmd == "#":
                # jump over the next character in the current direction
                move()
            elif cmd == "j":
                # IP = (y, x) in the codebox
                y, x = stack.pop(), stack.pop()
            elif cmd == "@":
                # IP go spinnie spinnie
                dirIndex = DIRECTIONS.index(direction)
                dirIndex += stack.pop(-1)
                direction = DIRECTIONS[dirIndex % 4]

            # there's still more

            # 2. Stack Manipulation
            elif cmd == "(":
                # select first stack (stack 0)
                selectedStack = 0
            elif cmd == ")":
                # select second stack (stack 1)
                selectedStack = 1
            elif cmd in "0123456789abcdef":
                # push the character as a hex digit
                stack.append(int(cmd, 16))
            elif cmd == "$":
                # swap
                top, second = stack.pop(-1), stack.pop(-1)
                stack += [top, second]
            elif cmd == "~":
                # delete top item
                stack.pop(-1)
            elif cmd == ":":
                # duplicate top item
                stack.append(stack[-1])
            elif cmd == "r":
                # reverse stack
                stack.reverse()
            elif cmd == "m":
                # send top item to the other stack
                otherStack.append(stack.pop(-1))
            elif cmd == "M":
                # same as m command, but you going reverse
                stack.append(otherStack.pop(-1))
            elif cmd == "V":
                # move the top item x places down.
                # explanation:
                # 1. pop top item
                # 2. move the second item top item places down
                raise NotImplementedError("the V command is really useless and I have no idea how to implement it lol")
            # stringMode is implemented, check above
            
            # 3. Arithmetic and Logic
            elif cmd == "!":
                # bitwise not
                temp = stack.pop(-1)
                if temp:
                    stack.append(0)
                else:
                    stack.append(1)
            elif cmd == "n":
                # negate                
                stack.append(-stack.pop(-1))
            elif cmd == "+":
                # add
                temp1, temp2 = stack.pop(-1), stack.pop(-1)
                stack.append(temp2 + temp1)
            elif cmd == "*":
                # multiply
                stack.append(stack.pop(-1) * stack.pop(-1))
            elif cmd == "/":
                # divide
                temp1, temp2 = stack.pop(-1), stack.pop(-1)
                temp = temp2 / temp1
                # also auto truncate decimal if it's a whole number
                if temp % 1 == 0:
                    temp = int(temp)           
                stack.append(temp)
            elif cmd == "\\":
                # exponent
                # if one value is string and one is number the string gets pushed on the stack the number of times
                temp1, temp2 = stack.pop(-1), stack.pop(-1)
                
                # I'ma be honest this method sucks but it's the only one I could think of
                if type(temp1) == str and type(temp2) == str:
                    # uh oh
                    raise TypeError("exponent can't use string and string")
                elif type(temp1) == str:
                    for _ in range(temp2):
                        stack.append(temp1)
                elif type(temp2) == str:
                    # same as if temp1 == str, but you going reverse
                    for _ in range(temp1):
                        stack.append(temp2)
                else:
                    stack.append(temp2 ** temp1)
            elif cmd == "=":
                # equality check
                stack.append((stack.pop(-1) == stack.pop(-1)) + 0) # + 0 is for converting to int
            elif cmd == "`":
                # greatality check
                temp1, temp2 = stack.pop(-1), stack.pop(-1)
                if type(temp1) == str:
                    temp1 = len(temp1)
                if type(temp2) == str:
                    temp2 = len(temp2)
                stack.append((temp2 > temp1) + 0)
            elif cmd == "&":
                # convert to float
                try:
                    number = stack.pop(-1)
                    number = float(number)
                    if number % 1 == 0:
                        number = int(number)
                    stack.append(number)
                except:
                    stack.append(number)
            elif cmd == "s":
                # convert to string
                stack.append(str(stack.pop(-1)))
            elif cmd == "t":
                # type; push 0 if x is number, 1 otherwise
                stack.append((type(stack.pop(-1)) == str) + 0)
            elif cmd == "U":
                # unicode command;
                # take a string and push its unicode characters left to right
                # if it's a number, then push the unicode value instead
                temp = stack.pop(-1)
                if type(temp) == str:
                    for char in temp:
                        stack.append(ord(char))
                else:
                    stack.append(chr(temp))
            elif cmd == ".":
                # literally y.split(x) lol
                temp1, temp2 = stack.pop(-1), stack.pop(-1)
                if type(temp1) != str: temp1 = chr(temp1)
                stack.append(temp2.split(temp1))
            elif cmd == ",":
                # random number
                temp1, temp2 = stack.pop(-1), stack.pop(-1)
                stack.append(randint(temp2, temp1))
            elif cmd == "l":
                # length of string
                stack.append(len(stack.pop(-1)))
            
            # 4. I/O
            elif cmd == "i":
                # take a string of input from user
                stack.append(input("Input? "))
            elif cmd == "o":
                # print top item
                print(stack.pop(-1))
            
            # Self-Modification
            elif cmd == "g":
                # get character as string
                codeY, codeX = stack.pop(-1), stack.pop(-1)
                try:
                    char = code[codeY][codeX]
                except:
                    char = " "
                stack.append(char)
            elif cmd == "G":
                # get character as unicode character
                codeY, codeX = stack.pop(-1), stack.pop(-1)
                try:
                    char = code[codeY][codeX]
                except:
                    char = chr(0)
                stack.append(ord(char))
            elif cmd == "p":
                # put character at location
                codeY, codeX, value = stack.pop(-1), stack.pop(-1), stack.pop(-1)
                code[codeY][codeX] = chr(value) if type(value) != str else value
            
            # 5. Control Flow
            elif cmd == "[":
                # mark current position
                marked = (x, y)
            elif cmd == "]":
                # go to marked position if not zero
                if stack.pop(-1):
                    x, y = marked
            elif cmd == "_":
                # right if zero, left otherwise
                if not stack.pop(-1):
                    direction = (1, 0)
                else:
                    direction = (-1, 0)
            else:
                # any invalid instruction is skipped
                pass

        move()

        # debug stuff, I would really recommend a wide terminal for this
        # print("Last command: " + cmd, f"(x, y): ({x}, {y})", f"Direction: {direction}", f"stack 0: {stack0}", f"stack 1: {stack1}", f"marked cell: {marked}", sep=" | ")

        # sleep(1/4)

def move() -> None:
    global direction, x, y, code
    # I tried using `x, y += direction` and then `x, y += *direction` but I guess Im too dumb because it didn't work. so we're using this lol
    x += direction[0]
    y += direction[1]

    # wrapping
    if x < 0:
        # left -> right
        x = len(maxLenLine) - 1
    elif x > len(maxLenLine) - 1:
        # right -> left
        x = 0
    elif y < 0:
        # top -> bottom
        y = len(code) - 1
    elif y > len(code) - 1:
        # bottom -> top
        y = 0

if __name__ == "__main__":
    interpret("code.poutput")