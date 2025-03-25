from django.shortcuts import render
from problems.models import Problems

# Create your views here.
def all_problems(request):
    print('here')
    problems = Problems.objects.all()
    print('here', problems)
    context = {
        "problems": problems
    }
    return render(request, "all_problems.html", context)

def problem(request, id):
    print('here', id)
    problem = Problems.objects.get(id=id)
    print('here', problem)
    context = {
        "problem": problem
    }
    return render(request, "problem.html", context)

