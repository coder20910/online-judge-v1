import json
import uuid
import subprocess
from pathlib import Path
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import CodeSubmission

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

def execute_code(language, file_paths):
    """Handles execution of Python and C++ code safely."""
    try:
        if language == "cpp":
            executable_path = file_paths["code"].with_suffix("")
            compile_result = subprocess.run(
                ["clang++", str(file_paths["code"]), "-o", str(executable_path)],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            if compile_result.returncode != 0:
                return compile_result.stderr

            with open(file_paths["input"], "r", encoding="utf-8") as input_file, \
                 open(file_paths["output"], "w", encoding="utf-8") as output_file:
                subprocess.run(
                    [str(executable_path)],
                    stdin=input_file,
                    stdout=output_file,
                    stderr=subprocess.PIPE,
                    text=True
                )
        
        elif language == "py":
            with open(file_paths["input"], "r", encoding="utf-8") as input_file, \
                 open(file_paths["output"], "w", encoding="utf-8") as output_file:
                result = subprocess.run(
                    ["python3", str(file_paths["code"])],
                    stdin=input_file,
                    stdout=output_file,
                    stderr=subprocess.PIPE,
                    text=True
                )
                if result.stderr:
                    output_file.write("\nError:\n" + result.stderr)

    except Exception as e:
        return f"Execution error: {str(e)}"

    with open(file_paths["output"], "r", encoding="utf-8") as output_file:
        return output_file.read()

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

    output_data = execute_code(language, file_paths)

    if query_type == "run":
        for path in file_paths.values():
            path.unlink(missing_ok=True)
    elif query_type == "submit" and user:
        CodeSubmission.objects.create(
            user=user,
            language=language,
            code=file_paths["code"],
            user_input=file_paths["input"],
            output=file_paths["output"]
        )

    return output_data

@login_required
def run_code_view(request):
    if request.method == "POST":
        request_body = json.loads(request.body)
        code = request_body.get("code")
        language = request_body.get("language")
        input_data = request_body.get("input", "")

        output = run_code_func(code=code, language=language, input_data=input_data, query_type="run", user=request.user)
        return JsonResponse({"output": output})

    return JsonResponse({"message": "Invalid request method."}, status=400)

@login_required
def submit_code_view(request):
    if request.method == "POST":
        request_body = json.loads(request.body)
        code = request_body.get("code")
        language = request_body.get("language")
        input_data = request_body.get("input", "")

        output = run_code_func(code=code, language=language, input_data=input_data, query_type="submit", user=request.user)
        return JsonResponse({"output": output})

    return JsonResponse({"message": "Invalid request method."}, status=400)
