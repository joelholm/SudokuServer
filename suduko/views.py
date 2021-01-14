from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from rest_framework.response import Response
from rest_framework import status
from suduko.models import Sudoku
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view



puzzle = None

@csrf_exempt
@api_view(['GET','POST'])
def sudoku_list(request):
    global puzzle
    if request.method == 'GET':
        if puzzle != None:
            return JsonResponse(puzzle.getJSONBoard())
        else:
            return Response("Puzzle not created yet", status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'POST':
        difficulty = request.data['difficulty']
        if difficulty > 0 and difficulty <= 5:
            puzzle = Sudoku()
            puzzle.makePuzzle(difficulty)
        print("squares:", puzzle.numSquaresFilledIn)
        return JsonResponse(puzzle.getJSONBoard())

@csrf_exempt
@api_view(['POST'])
def sudoku_move(request):
    global puzzle
    if request.method == 'POST':
        move = request.data["move"]
        if puzzle == None:
            return Response("Puzzle not created yet", status=status.HTTP_400_BAD_REQUEST)
        elif puzzle.isValidMove( move["num"], move["boxNum"], move["space"]):
            puzzle.setNum( move["num"], move["boxNum"], move["space"])
            return JsonResponse(puzzle.getJSONBoard())
        else:
            return Response("Move is not valid", status=status.HTTP_422_UNPROCESSABLE_ENTITY)
