import sys
import os
from full_converter import main as flow_main
from doc_generator import generate_code_documentation

if len(sys.argv) < 3:
    print(" Usage: python run.py <mode> <input_file>")
    sys.exit(1)

mode = sys.argv[1]
input_file = sys.argv[2]

if not os.path.exists(input_file):
    print(f" Error: '{input_file}' not found.")
    sys.exit(1)


if mode == "flowchart":
    flow_main(input_file)
elif mode == "doc":
    generate_code_documentation(input_file)
