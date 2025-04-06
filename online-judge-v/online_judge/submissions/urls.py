from django.urls import path
from submissions.views import submit_code_view, run_code_view

urlpatterns = [
    path("submit_code/<int:problem_id>/", submit_code_view, name='submit_code'),
    path("run_code/", run_code_view, name='run_code'),
]