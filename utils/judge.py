import subprocess
import time
import os
from typing import Dict, List, Tuple


def run_python_code(
    code: str, test_input: str, time_limit: float
) -> Tuple[str, float, bool]:
    """Run Python code with the given input and return output, execution time, and timeout status"""

    # Create a temporary file with the code
    temp_file = "temp_code.py"
    with open(temp_file, "w") as f:
        f.write(code)

    start_time = time.time()
    process = subprocess.Popen(
        ["python", temp_file],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    try:
        output, error = process.communicate(input=test_input, timeout=time_limit)
        execution_time = time.time() - start_time

        if error:
            return error.strip(), execution_time, False
        return output.strip(), execution_time, False

    except subprocess.TimeoutExpired:
        process.kill()
        return "", time_limit, True


def run_c_code(
    code: str, test_input: str, time_limit: float
) -> Tuple[str, float, bool]:
    """Run C code with the given input and return output, execution time, and timeout status"""

    # Create temporary C file
    temp_c_file = "temp_code.c"
    temp_exe_file = "temp_code.exe"

    with open(temp_c_file, "w") as f:
        f.write(code)

    # Compile C code
    compile_process = subprocess.run(
        ["gcc", temp_c_file, "-o", temp_exe_file], capture_output=True, text=True
    )

    if compile_process.returncode != 0:
        return f"Compilation error:\n{compile_process.stderr}", 0, False

    # Run the compiled code
    start_time = time.time()
    process = subprocess.Popen(
        [f"./{temp_exe_file}"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    try:
        output, error = process.communicate(input=test_input, timeout=time_limit)
        execution_time = time.time() - start_time

        if error:
            return error.strip(), execution_time, False
        return output.strip(), execution_time, False

    except subprocess.TimeoutExpired:
        process.kill()
        return "", time_limit, True


def test_code(code: str, language: str, test_cases: List[Dict]) -> List[Dict]:
    """Test code against multiple test cases and return results"""
    results = []

    for i, test_case in enumerate(test_cases, 1):
        input_data = test_case["input"]
        expected = test_case["expected"]
        time_limit = test_case.get("time_limit", 1.0)

        if language == "Python":
            output, time_taken, timeout = run_python_code(code, input_data, time_limit)
        elif language == "C":
            output, time_taken, timeout = run_c_code(code, input_data, time_limit)
        else:
            results.append(
                {
                    "test_case": i,
                    "status": "Error",
                    "message": f"Unsupported language: {language}",
                }
            )
            continue

        if timeout:
            status = "Time Limit Exceeded"
            message = f"Time limit of {time_limit}s exceeded"
        elif output == expected:
            status = "Passed"
            message = f"Output matches expected. Time: {time_taken:.3f}s"
        else:
            status = "Failed"
            message = f"Expected '{expected}', but got '{output}'"

        results.append(
            {"test_case": i, "status": status, "message": message, "time": time_taken}
        )

    return results
