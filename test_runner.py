import os
import subprocess
import json
import tempfile
import shutil
from pathlib import Path

# --- Configuration ---
TEST_CASES_DIR = Path("data/test_cases/inputs")
EXPECTED_OUTPUTS_DIR = Path("data/test_cases/expected_outputs")
RUN_COMMAND_FILE = Path("solution/run_command.txt")

# Colors for Windows terminal (requires ANSI support, usually on by default in Win 10/11)
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'

def print_header(text):
    print(f"{BLUE}╔" + "═" * 56 + "╗")
    print(f"║ {text:^54} ║")
    print(f"╚" + "═" * 56 + "╝{NC}")

def main():
    # 1. Read the solution command
    if not RUN_COMMAND_FILE.exists():
        print(f"{RED}Error: Run command file not found: {RUN_COMMAND_FILE}{NC}")
        return

    with open(RUN_COMMAND_FILE, 'r') as f:
        solution_cmd = f.read().strip()

    # 2. Check for test cases
    if not TEST_CASES_DIR.exists():
        print(f"{RED}Error: Test cases directory not found: {TEST_CASES_DIR}{NC}")
        return

    test_files = sorted(list(TEST_CASES_DIR.glob("test_*.json")))
    total_tests = len(test_files)

    if total_tests == 0:
        print(f"{RED}Error: No test files found in {TEST_CASES_DIR}{NC}")
        return

    print_header("Box Box Box - Test Runner")
    print(f"Solution Command: {YELLOW}{solution_cmd}{NC}")
    print(f"Test Cases Found: {YELLOW}{total_tests}{NC}\n")

    # 3. Setup tracking
    passed = 0
    failed = 0
    errors = 0
    has_answers = EXPECTED_OUTPUTS_DIR.exists()

    # 4. Run Tests
    print(f"{BLUE}Running tests...{NC}\n")

    for test_path in test_files:
        test_name = test_path.stem
        test_id = test_name.replace("test_", "TEST_")

        try:
            # Read input file to pipe into the solution
            with open(test_path, 'r') as f_in:
                input_data = f_in.read()

            # Execute the solution command
            process = subprocess.Popen(
                solution_cmd,
                shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input=input_data)

            if process.returncode != 0:
                print(f"{RED}✗{NC} {test_id} - Execution error")
                if stderr:
                    print(f"  {RED}Error:{NC} {stderr.splitlines()[0]}")
                errors += 1
                continue

            # Parse Output JSON
            try:
                actual_json = json.loads(stdout)
                predicted = actual_json.get("finishing_positions")

                if predicted is None:
                    print(f"{RED}✗{NC} {test_id} - Invalid output format (missing finishing_positions)")
                    failed += 1
                    continue

                # Verification logic
                answer_file = EXPECTED_OUTPUTS_DIR / f"{test_name}.json"
                
                if has_answers and answer_file.exists():
                    with open(answer_file, 'r') as f_ans:
                        expected_json = json.load(f_ans)
                        expected = expected_json.get("finishing_positions")

                    if predicted == expected:
                        print(f"{GREEN}✓{NC} {test_id}")
                        passed += 1
                    else:
                        print(f"{RED}✗{NC} {test_id} - Incorrect prediction")
                        failed += 1
                else:
                    print(f"{YELLOW}?{NC} {test_id} - Output generated (no answer key to verify)")
                    passed += 1

            except json.JSONDecodeError:
                print(f"{RED}✗{NC} {test_id} - Invalid JSON output")
                failed += 1

        except Exception as e:
            print(f"{RED}✗{NC} {test_id} - Unexpected error: {str(e)}")
            errors += 1

    # 5. Final Results
    print_header("Results")
    
    pass_rate = (passed * 100 / total_tests) if total_tests > 0 else 0

    print(f"Total Tests:    {YELLOW}{total_tests}{NC}")
    print(f"Passed:         {GREEN}{passed}{NC}")
    print(f"Failed:         {RED}{failed}{NC}")
    if errors > 0:
        print(f"Errors:         {RED}{errors}{NC}")
    
    print(f"\nPass Rate:      {GREEN}{pass_rate:.1f}%{NC}\n")

    if not has_answers:
        print(f"{YELLOW}Note: Running without expected outputs. Only checking output format.{NC}\n")

    # 6. Exit logic
    if passed == total_tests:
        print(f"{GREEN}🏆 Perfect score! All tests passed!{NC}")
        exit(0)
    elif passed > 0:
        print(f"{YELLOW}Keep improving! Check failed test cases.{NC}")
        exit(0)
    else:
        print(f"{RED}No tests passed. Review your implementation.{NC}")
        exit(1)

if __name__ == "__main__":
    main()