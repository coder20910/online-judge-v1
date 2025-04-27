import json
import uuid
import subprocess
from pathlib import Path
import time
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from problems.models import Problems, TestCase
from .models import CodeSubmission, UserCode
from django.db import transaction
from django.db.utils import DatabaseError

def ensure_directories_exist():
    """Ensures necessary directories exist."""
    project_path = Path(settings.BASE_DIR)
    directories = ["codes", "inputs", "outputs"]

    for directory in directories:
        dir_path = project_path / directory
        dir_path.mkdir(parents=True, exist_ok=True)

def generate_file_paths(unique_id, language):
    """Generates file paths for code, input, and output files."""
    project_path = Path(settings.BASE_DIR)
    return {
        "code": project_path / "codes" / f"{unique_id}_code.{language}",
        "input": project_path / "inputs" / f"{unique_id}.txt",
        "output": project_path / "outputs" / f"{unique_id}.txt"
    }

VERDICT_CHOICES = [
    ("Accepted", "Accepted"),
    ("Wrong Answer", "Wrong Answer"),
    ("Runtime Error", "Runtime Error"),
    ("Time Limit Exceeded", "Time Limit Exceeded"),
    ("Compilation Error", "Compilation Error"),
    ("Error", "Error"),
]

def clean_error_message(error_msg):
    """Remove file paths from error messages but keep UUID"""
    if not error_msg:
        return error_msg

    lines = error_msg.split('\n')
    cleaned_lines = []

    for line in lines:
        if line.startswith('  File "'):
            # Extract UUID and line number
            try:
                file_name = line.split('"')[1].split('\\')[-1]  # Get just the filename
                line_info = line.split(', ', 1)[1] if ', ' in line else ''
                cleaned_lines.append(f'  File "{file_name}", {line_info}')
            except IndexError:
                cleaned_lines.append(line)
        else:
            cleaned_lines.append(line)

    return '\n'.join(cleaned_lines)

def execute_code(language, file_paths, timeout_limit_max=10):
    """Handles execution of Python and C++ code safely with clear verdicts."""
    try:
        if language == "cpp":
            executable_path = file_paths["code"].with_suffix("")
            compile_result = subprocess.run(
                ["g++", str(file_paths["code"]), "-o", str(executable_path)],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            if compile_result.returncode != 0:
                return {
                    'status': 'error',
                    'error_type': 'Compilation Error',
                    'message': compile_result.stderr,
                    'output': ''
                }

            with open(file_paths["input"], "r", encoding="utf-8") as input_file, \
                 open(file_paths["output"], "w", encoding="utf-8") as output_file:
                result = subprocess.run(
                    [str(executable_path)],
                    stdin=input_file,
                    stdout=output_file,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=timeout_limit_max
                )
                if result.stderr:
                    return {
                        'status': 'error',
                        'error_type': 'Runtime Error',
                        'message': result.stderr,
                        'output': ''
                    }

        elif language == "py":
            with open(file_paths["input"], "r", encoding="utf-8") as input_file, \
                 open(file_paths["output"], "w", encoding="utf-8") as output_file:
                result = subprocess.run(
                    ["python3", str(file_paths["code"])],
                    stdin=input_file,
                    stdout=output_file,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=timeout_limit_max
                )
                if result.stderr:
                    return {
                        'status': 'error',
                        'error_type': 'Runtime Error',
                        'message': result.stderr,
                        'output': ''
                    }

    except subprocess.TimeoutExpired:
        return {
            'status': 'error',
            'error_type': 'Time Limit Exceeded',
            'message': 'Time Limit Exceeded',
            'output': ''
        }

    except Exception as e:
        return {
            'status': 'error',
            'error_type': 'Error',
            'message': str(e),
            'output': ''
        }

    with open(file_paths["output"], "r", encoding="utf-8") as output_file:
        return {
            'status': 'success',
            'error_type': None,
            'output': output_file.read(),
            'message': ''
        }

def run_code_func(code, language, input_data, query_type="run", user=None):
    ensure_directories_exist()
    language_map = {"python": "py", "cpp": "cpp"}
    language = language_map.get(language)
    if not language:
        return "Unsupported language."

    unique_id = str(uuid.uuid4())
    file_paths = generate_file_paths(unique_id, language)

    with open(file_paths["code"], "w", encoding="utf-8") as code_file:
        code_file.write(code)
    with open(file_paths["input"], "w", encoding="utf-8") as input_file:
        input_file.write(input_data)

    output_data = None
    execute_code_result = execute_code(language, file_paths)

    for path in file_paths.values():
        path.unlink(missing_ok=True)

    return execute_code_result

def submit_code_func(code, language, problem_id, user = None, time_limit = 10):
    ensure_directories_exist()
    language_map = {"python": "py", "cpp": "cpp"}
    language = language_map.get(language)
    if not language:
        return "Unsupported language."

    unique_id = str(uuid.uuid4())
    file_paths = generate_file_paths(unique_id, language)

    with open(file_paths["code"], "w", encoding="utf-8") as code_file:
        code_file.write(code)

    test_cases = TestCase.objects.filter(problem_id=problem_id)
    problem = Problems.objects.get(id=problem_id)

    start = time.perf_counter()
    all_passed = True
    testcase_results = []
    code_evaluation_result = None
    test_case_failed = 0
    message = ""
    for i, tc in enumerate(test_cases, start=1):
        input_data = tc.input_data

        with open(file_paths["input"], "w", encoding="utf-8") as input_file:
            input_file.write(input_data)

        code_evaluation_result = execute_code(language, file_paths)
        if code_evaluation_result['status'] != 'success':
            all_passed = False
            testcase_results.append({
                "index": i,
                'input': tc.input_data, 
                'verdict': code_evaluation_result['error_type'], 
                'code_output': code_evaluation_result['output'].strip(),
                'expected_output': tc.output_data.strip(),
            })
            test_case_failed = i
            message = code_evaluation_result['message']
            break

        if code_evaluation_result['output'].strip() != tc.output_data.strip():
            all_passed = False
            testcase_results.append({
                "index": i,
                'input': tc.input_data,
                'verdict': 'Wrong Answer',
                'expected_output': tc.output_data.strip(),
                'code_output': code_evaluation_result['output'].strip(),
            })
            test_case_failed = i
            break
        else:
            testcase_results.append({
                "index": i,
                "verdict": "Passed"
            })
    end = time.perf_counter()
    exec_time = round(end - start, 4)  # seconds, rounded to 4 decimal places
    print("testcase_results", testcase_results)
    if all_passed:
        final_verdict = "Accepted"
        verdict_details = "Accepted"
    else:
        final_verdict = testcase_results[-1]['verdict']
        verdict_details = f'{final_verdict} on test case {test_case_failed}'

    CodeSubmission.objects.create(
        user=user,
        problem=problem,
        language=language,
        code=file_paths["code"],
        user_input="",
        output=file_paths["output"],
        verdict=final_verdict,
        verdict_details=verdict_details,
        execution_time=exec_time
    )
    resp = {
        "verdict": final_verdict,
        "message": message,
        "test_cases_count": len(test_cases),
        "test_case_failed": test_case_failed
    }
    file_paths['input'].unlink(missing_ok=True)
    return resp


# Views

@login_required
def run_code_view(request):
    if request.method == "POST":
        try:
            request_body = json.loads(request.body)
            code = request_body.get("code")
            language = request_body.get("language")
            input_data = request_body.get("input", "")
            should_save = request_body.get("save_code", False)
            problem_id = request_body.get("problem_id")

            # Save code if requested and problem_id is provided
            if should_save and problem_id:
                problem = Problems.objects.get(id=problem_id)  # Verify problem exists
                UserCode.objects.update_or_create(
                    user=request.user,
                    problem=problem,  # Use problem instance instead of problem_id
                    language=language,
                    defaults={
                        'code': code
                    }
                )

            run_code_resp = run_code_func(
                code=code,
                language=language,
                input_data=input_data,
                query_type="run",
                user=request.user
            )
            if run_code_resp.get("message") is not None:
                run_code_resp["message"] = clean_error_message(run_code_resp.get("message"))
            return JsonResponse(run_code_resp)

        except Problems.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "Problem not found"
            }, status=404)
        except json.JSONDecodeError:
            return JsonResponse({
                "status": "error",
                "message": "Invalid JSON"
            }, status=400)

    return JsonResponse({"message": "Invalid request method."}, status=400)

@login_required
def submit_code_view(request, problem_id):
    if request.method != "POST":
        return JsonResponse({"message": "Invalid request method."}, status=400)

    try:
        request_body = json.loads(request.body)
        code = request_body.get("code")
        language = request_body.get("language")

        # Save code and get submit response in one transaction
        with transaction.atomic():
            UserCode.objects.update_or_create(
                user=request.user,
                problem_id=problem_id,  # Django will validate FK constraint
                language=language,
                defaults={'code': code}
            )

            submit_code_resp = submit_code_func(
                code=code,
                language=language,
                problem_id=problem_id,
                user=request.user
            )

        if submit_code_resp.get("message"):
            submit_code_resp["message"] = clean_error_message(submit_code_resp.get("message"))

        return JsonResponse(submit_code_resp)

    except DatabaseError:
        return JsonResponse({
            "status": "error",
            "message": "Database error occurred"
        }, status=500)
    except json.JSONDecodeError:
        return JsonResponse({
            "status": "error", 
            "message": "Invalid JSON"
        }, status=400)

@login_required
def submission_history_view(request, problem_id):
    project_path = Path(settings.BASE_DIR)
    submissions = CodeSubmission.objects.filter(
        problem_id=problem_id,
        user=request.user
    ).order_by('-timestamp')

    for submission in submissions:
        extracted_code_file_name = submission.code.split("codes")[1]
        code_file_full_path = f'{project_path}/codes/{extracted_code_file_name}'
        if Path(code_file_full_path).exists():
            with open(code_file_full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            submission.code = content
    problem = Problems.objects.get(id=problem_id)
    context = {
        "submissions": submissions,
        "problem": problem
    }

    return render(request, "submissions/submission_history.html", context)

@login_required
def load_code_state_view(request, problem_id):
    try:
        problem = Problems.objects.get(id=problem_id)  # Verify problem exists
        user_code = UserCode.objects.get(
            user=request.user,
            problem=problem,
            language=request.GET.get('language', 'python')  # Get language from query params
        )
        return JsonResponse({
            "status": "success",
            "code": user_code.code,
            "language": user_code.language
        })
    except (Problems.DoesNotExist, UserCode.DoesNotExist):
        return JsonResponse({
            "status": "success",
            "code": "",
            "language": "python"
        })
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)
