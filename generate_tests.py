import os
import json

TEST_CASES_FOLDER = os.path.abspath("test_cases")
TEST_INPUT_FOLDER = os.path.join(TEST_CASES_FOLDER, "in")
TEST_OUTPUT_FOLDER = os.path.join(TEST_CASES_FOLDER, "out")
SOLUTION_FOLDER = os.path.abspath("solution")

CONFIG_FILE = "tester_config.json"
TEST_FILE = "tests/test_assembly.py"

def discover_test_cases():
    """Discover all test cases by matching input and output files."""
    test_cases = []
    
    if not os.path.exists(TEST_INPUT_FOLDER) or not os.path.exists(TEST_OUTPUT_FOLDER):
        print("Error: Test case directories not found.")
        return []

    for input_file in sorted(os.listdir(TEST_INPUT_FOLDER)):
        if input_file.endswith(".txt"):
            case_name = os.path.splitext(input_file)[0]
            output_file = f"output{case_name.replace("input", "")}.txt"
            if output_file in os.listdir(TEST_OUTPUT_FOLDER):
                test_cases.append((input_file, output_file))
    
    return test_cases

def generate_config(test_cases):
    """Generate a JSON configuration file based on discovered test cases."""
    config = {
        "version": 2,
        "python_version": 3.9,
        "solution_signature": "solution/Dockerfile",
        "number_of_tests": len(test_cases),
        "can_submit_single_file": True,
        "single_file_path": "solution/Dockerfile",
        "packages": [
            {
                "name": "8086_judge",
                "score": 100,
                "tests": [f"test_{i+1}" for i in range(len(test_cases))],
                "aggregator": "sum"
            }
        ]
    }

    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

    print(f"✅ Configuration file '{CONFIG_FILE}' generated successfully.")

def generate_test_file(test_cases):
    """Generate a Python unittest file with all discovered test cases."""
    test_content = '''import unittest
import os
from scripts.docker_handler import DockerHandler
from scripts.asm_runner import AssemblyRunner

class TestAssemblyPrograms(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        DockerHandler.start_container()

    @classmethod
    def tearDownClass(cls):
        DockerHandler.stop_container()
'''

    for index, (input_file, output_file) in enumerate(test_cases):
        test_content += f'''
    def test_{index + 1}(self):
        asm_file = "Q2.asm"
        input_file = "{input_file}"
        output_file = "{output_file}"

        AssemblyRunner.compile_asm(asm_file)
        output = AssemblyRunner.run_asm(asm_file, input_file)

        output_path = os.path.join(AssemblyRunner.TEST_CASES_FOLDER, "out", output_file)
        with open(output_path, "r") as f:
            expected_output = [line.strip() for line in f.readlines()]

        self.assertEqual(output, expected_output, f"Unexpected output for {{asm_file}}")
'''

    test_content += '''

if __name__ == "__main__":
    unittest.main()
'''

    with open(TEST_FILE, "w") as f:
        f.write(test_content)

    print(f"✅ Test file '{TEST_FILE}' generated successfully.")

if __name__ == "__main__":
    test_cases = discover_test_cases()
    
    if test_cases:
        generate_config(test_cases)
        generate_test_file(test_cases)
        print("🚀 Test suite and configuration successfully generated!")
    else:
        print("⚠️ No valid test cases found. Please check your test_cases/in and test_cases/out directories.")
