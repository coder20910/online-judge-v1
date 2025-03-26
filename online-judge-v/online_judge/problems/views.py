from django.shortcuts import render
from problems.models import Problems
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def all_problems(request):
    print('here')
    problems = Problems.objects.all()
    print('here', problems)
    context = {
        "problems": problems
    }
    return render(request, "all_problems.html", context)

@login_required
def problem(request, id):
    print('here', id)
    problem = Problems.objects.get(id=id)
    print('here', problem)
    context = {
        "problem": problem
    }
    return render(request, "problem.html", context)

