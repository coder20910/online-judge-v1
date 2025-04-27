from django.urls import path
from problems.views import problem_detail_view, all_problems_view
from submissions.views import submission_history_view

urlpatterns = [
    path("", all_problems_view, name="all_problems"),
    path("<int:problem_id>/", problem_detail_view, name="problem_detail"),
    path("<int:problem_id>/submissions/", submission_history_view, name="problem_submissions"),
]
