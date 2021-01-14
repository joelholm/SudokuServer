from django.urls import path
from suduko import views

urlpatterns = [
    path('sudoku/', views.sudoku_list),
    path('sudoku/move/', views.sudoku_move),
]
