from django.shortcuts import render
from django.http import JsonResponse
from suduko.models import Sudoku

puzzle = Sudoku()

def sudoku_list(request):

    if request.method == 'GET':
        global puzzle
        puzzle.printAll()
        return JsonResponse(
            {
                '1': ['_', '7', '9'],
                '2': ['1', '4', '_']
            }
        )


# GET sudoku_list   -> 9x9 board

# POST sudoku_list  -> difficulty
#                   -> response: new game

# POST sudoku_detail -> set a space
#                    -> response: isValidMove and 9x9 board and isGameOver
