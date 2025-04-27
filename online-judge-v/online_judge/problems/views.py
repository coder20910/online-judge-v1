from django.shortcuts import render
from problems.models import Problems, TestCase
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, F, ExpressionWrapper, FloatField, Case, When

# Create your views here.
@login_required
def all_problems_view(request):
    problems = Problems.objects.annotate(
        total_submissions=Count('codesubmission'),
        accepted_submissions=Count(
            'codesubmission',
            filter=Q(codesubmission__verdict='Accepted')
        ),
        acceptance_rate=Case(
            When(total_submissions__gt=0, 
                then=ExpressionWrapper(
                    F('accepted_submissions') * 100.0 / F('total_submissions'),
                    output_field=FloatField()
                )
            ),
            default=0.0,
            output_field=FloatField(),
        ),
        unique_users=Count('codesubmission__user', distinct=True)
    ).all()

    return render(request, 'all_problems.html', {'problems': problems})

@login_required
def problem_detail_view(request, problem_id):
    problem = Problems.objects.get(id=problem_id)
    sample_test_cases =TestCase.objects.filter(problem_id=problem_id, is_sample=True)
    context = {
        "problem": problem,
        "sample_test_cases": sample_test_cases
    }
    return render(request, "problem.html", context)
