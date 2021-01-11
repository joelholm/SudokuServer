from django.urls import path
from suduko import views

urlpatterns = [
    path('suduko/', views.suduko_list),
]
