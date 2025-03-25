from django.urls import path
from problems.views import all_problems, problem
urlpatterns = [
    path("", all_problems, name='problems'),
    path("<int:id>/", problem, name='problem'),
]