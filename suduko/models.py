from django.db import models
import random

# 0 ->  Genius
# 40 -> Expert
# 45 -> Hard
# 50 -> Medium
# 60 -> Easy
difficultyConfig = [0, 40, 45, 50, 60]

class SudokuBox:
    """
    spaces
        0 1 2
        3 4 5
        6 7 8
    """
    def __init__(self, boxNum):
        self.spaces = [0] * 9
        self.boxNum = boxNum

    def setNum(self, num, space):
        if num >= 0 and num <= 9 and space >= 0 and space <= 8:
            self.spaces[space] = num

    def printBox(self):
        print("===============")
        for i in range(3):
            print(f"|| {self.spaces[i * 3]} | {self.spaces[i * 3 + 1]} | {self.spaces[i * 3 + 2]} ||")
        print("===============")

class Sudoku:
    def __init__(self):
        self.boxes = []
        self.keyBoxes = []
        self.numSquaresFilledIn = 0
        self.crbMap = {}
        self.isValid = True

        for i in range(9):
            self.boxes.append(SudokuBox(i))
        for i in range(1,10):
            self.crbMap[i] = {
                'column': {},
                'row': {},
                'box': {}
            }
            for j in range(9):
                self.crbMap[i]['column'][j] = False
                self.crbMap[i]['row'][j] = False
                self.crbMap[i]['box'][j] = False

    #TODO: This only is suppose to be called once, probably bad design
    def makePuzzle(self, difficulty):
        #Make a puzzle key
        self.generateKey()

        #Generate random order to remove numbers when setting the difficulty
        boxArray = []
        randBoxArray = []
        for i in range(9):
            boxArray.append([])
            for j in range(9):
                boxArray[i].append(j)
        for i in range(9):
            randBoxArray.append([])
            for j in range(9):
                randIndex = random.randint(0, len(boxArray[i]) - 1)
                randBoxArray[i].append(boxArray[i][randIndex])
                boxArray[i].pop(randIndex)

        for x in range(9):
            for i in range(1,10):
                #pick a random square and remove the number i
                randBoxNum = randBoxArray[i - 1][x]
                space = 0
                for j in range(9):
                    if self.boxes[randBoxNum].spaces[j] == i:
                        space = j
                        self.boxes[randBoxNum].spaces[j] = 0
                self.numSquaresFilledIn -= 1
                self.crbMap[i]['column'][((randBoxNum % 3) * 3 + space % 3)] = False
                self.crbMap[i]['row'][((randBoxNum // 3) * 3 + (space // 3))] = False
                self.crbMap[i]['box'][randBoxNum] = False
                possiblePuzzle = PuzzleSolver.findSolutions(self, self.boxes[randBoxNum], space, i)
                if possiblePuzzle != None:
                    #if removing this number leads to multiple solutions, re-place the number and continue
                    self.setNum(i, randBoxNum, space)
                if self.numSquaresFilledIn < difficultyConfig[difficulty]:
                    return

    def generateKey(self):
        puzzleKey = Sudoku()
        #Set boxes 1,4,7 with random numbers
        for i in range(3):
            puzzleKey.randBoxGen(puzzleKey.boxes[i * 3 + i])
        #Solve the puzzle
        puzzleKey = PuzzleSolver.solvePuzzle(puzzleKey)
        #load into boxes
        self.setPuzzle(puzzleKey)
        #load into key
        for i in range(9):
            self.keyBoxes.append(SudokuBox(i))
            for j in range(9):
                self.keyBoxes[i].setNum(self.boxes[i].spaces[j], j)

    def randBoxGen(self, box):
        orderedList = []
        for i in range(9):
            orderedList.append(i + 1)
        i = 0
        for j in range(9):
            randNum = random.randint(0, len(orderedList) - 1)
            self.setNum(orderedList[randNum], box.boxNum, j)
            orderedList.pop(randNum)

    def createCopy(self):
        copySudoku = Sudoku()
        for i in range(9):
            for j in range(9):
                copySudoku.setNum(self.boxes[i].spaces[j], i, j)
        return copySudoku

    def setPuzzle(self, puzzle):
        for i in range(9):
            for j in range(9):
                self.setNum(puzzle.boxes[i].spaces[j], i, j)

    def isGameOver(self):
        return (self.numSquaresFilledIn == 81)

    def setNum(self, num, boxNum, space):
        if num == 0:
            return
        self.numSquaresFilledIn += 1
        self.boxes[boxNum].setNum(num, space)
        #update crbMap
        self.crbMap[num]['column'][((boxNum % 3) * 3 + space % 3)] = True
        self.crbMap[num]['row'][((boxNum // 3) * 3 + (space // 3))] = True
        self.crbMap[num]['box'][boxNum] = True

    def isValidMove(self, num, boxNum, space):
        if self.keyBoxes[boxNum].spaces[space] == num:
            return True
        return False

    def getJSONBoard(self):
        response = {
            "puzzle":[],
            "isGameOver": self.isGameOver()
        }
        for box in range(9):
            response["puzzle"].append([])
            for space in range(9):
                response["puzzle"][box].append(self.boxes[box].spaces[space])
        return response

    def printAll(self):
        for i in range(3):
            box1 = self.boxes[i * 3]
            box2 = self.boxes[i * 3 + 1]
            box3 = self.boxes[i * 3 + 2]
            print("=========================================")
            for j in range(3):
                print(
                    f"|| {box1.spaces[j * 3]} | {box1.spaces[j * 3 + 1]} | {box1.spaces[j * 3 + 2]} ||",
                    f"{box2.spaces[j * 3]} | {box2.spaces[j * 3 + 1]} | {box2.spaces[j * 3 + 2]} ||",
                    f"{box3.spaces[j * 3]} | {box3.spaces[j * 3 + 1]} | {box3.spaces[j * 3 + 2]} ||",
                )
        print("=========================================")

class PuzzleSolver:

    #TODO
    # Possible Optimizations`
    #  1. Optimize method1 (if last number n is known, attempt to place n in orthogonal boxes)
    #  2. Dominos

    def solvePuzzle(puzzle):
        if puzzle.isGameOver():
            return puzzle
        method1 = False
        #method 1: Check for boxes with a single space open for number n
        for n in range(1,10):
            for box in puzzle.boxes:
                availableSpaces = PuzzleSolver.findAvailableSpaces(puzzle, box, n)
                #check if the puzzle is invalid
                if len(availableSpaces) == 0 and not puzzle.crbMap[n]['box'][box.boxNum]:
                    puzzle.isValid = False
                    return puzzle
                #method 1
                if len(availableSpaces) == 1:
                    puzzle.setNum(n, box.boxNum, availableSpaces[0])
                    method1 = True
        if method1:
            #Don't attempt methods 2,3,4 until method 1 is out of options
            return PuzzleSolver.solvePuzzle(puzzle)
        for i in range(2,5):
            solution = PuzzleSolver.methodK(puzzle, i)
            if solution != None:
                return solution
        return Sudoku()

    """
    Method K
        This method looks at k spaces that could contain a number n.
        Each space is recursively run through the solver with the number n to see if a solution is possible.
    """
    def methodK(puzzle, k):
        for n in range(1,10):
            for box in puzzle.boxes:
                availableSpaces = PuzzleSolver.findAvailableSpaces(puzzle, box, n)
                if len(availableSpaces) == k:
                    solution = None
                    for i in range(k):
                        puzzleCopy = puzzle.createCopy()
                        puzzleCopy.setNum(n, box.boxNum, availableSpaces[i])
                        solution = PuzzleSolver.solvePuzzle(puzzleCopy)
                        if solution != None and solution.isValid:
                            #found a valid puzzle, keep returning it
                            return solution
                    #If all spaces lead to an invalid puzzle, then this puzzle is invalid
                    return solution
        #No boxes in this puzzle contain k open spaces for any number
        return None

    def findAvailableSpaces(puzzle, box, num):
        #rule out occupied boxes
        if puzzle.crbMap[num]['box'][box.boxNum]:
            return []
        baseColumn = (box.boxNum % 3) * 3
        baseRow = (box.boxNum // 3) * 3

        spaceMap = []
        for i in range(9):
            spaceMap.append(1)
        #Rule out occupied spaces
        for i in range(9):
            if box.spaces[i] != 0:
                spaceMap[i] = 0
        #Rule out any columns or rows
        for i in range(3):
            if puzzle.crbMap[num]['column'][baseColumn + i]:
                for j in range(3):
                    spaceMap[i + j * 3] = 0
            if puzzle.crbMap[num]['row'][baseRow + i]:
                for j in range(3):
                    spaceMap[i * 3 + j] = 0

        #Now package the spaces to be returned
        availableSpaces = []
        for i in range(9):
            if spaceMap[i] == 1:
                availableSpaces.append(i)

        #Randomize the order of possible spaces (this enables complete range of random puzzle generation)
        shuffledSpaces = []
        for i in range(len(availableSpaces)):
            randIndex = random.randint(0, len(availableSpaces) - 1)
            shuffledSpaces.append(availableSpaces[randIndex])
            availableSpaces.pop(randIndex)
        return shuffledSpaces

    def findSolutions(puzzle, box, space, num):
        #for every number but num
        for i in range(1,10):
            availableSpaces = PuzzleSolver.findAvailableSpaces(puzzle, box, i)
            numPossible = False
            #make sure that num can be placed in the space
            for aSpace in availableSpaces:
                if aSpace == space:
                    numPossible = True
            if i != num and numPossible:
                #attempt to solve the puzzle with that number in
                puzzleCopy = puzzle.createCopy()
                puzzleCopy.setNum(i, box.boxNum, space)
                solution = PuzzleSolver.solvePuzzle(puzzleCopy)
                if solution.isValid:
                    #return the puzzle with multiple solutions
                    return puzzle
        return None

def tests():
    puzzle = Sudoku()

    puzzle.makePuzzle(3)
    print("given:", puzzle.numSquaresFilledIn)
    puzzle.printAll()

# tests()
# puzzleResearch()
