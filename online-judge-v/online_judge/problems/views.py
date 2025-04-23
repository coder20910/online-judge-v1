from django.shortcuts import render
from problems.models import Problems, TestCase
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def all_problems(request):
    problems = Problems.objects.all()
    context = {
        "problems": problems
    }
    return render(request, "all_problems.html", context)

@login_required
def problem(request, id):
    problem = Problems.objects.get(id=id)
    sample_test_cases =TestCase.objects.filter(problem_id=id, is_sample=True)
    context = {
        "problem": problem,
        "sample_test_cases": sample_test_cases
    }
    return render(request, "problem.html", context)
