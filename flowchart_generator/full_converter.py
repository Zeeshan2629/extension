import ast
import os
from Converter import translation, drawer
from PIL import ImageFont

def python_to_pseudocode(code):
    tree = ast.parse(code)
    pseudocode = []

    def parse_node(node, level=0):
        lines = []

        if isinstance(node, ast.FunctionDef):
            args = ", ".join([arg.arg for arg in node.args.args])
            lines.append(f"FUNCTION {node.name.upper()}({args})")
            for stmt in node.body:
                lines.extend(parse_node(stmt, level + 1))
            lines.append("ENDFUNCTION")

        elif isinstance(node, ast.If):
            condition = ast.unparse(node.test).strip()
            lines.append(f"IF {condition} THEN")
            for stmt in node.body:
                lines.extend(parse_node(stmt, level + 1))
            if node.orelse:
                lines.append("ELSE")
                for stmt in node.orelse:
                    lines.extend(parse_node(stmt, level + 1))
            lines.append("ENDIF")

        elif isinstance(node, ast.For):
            if isinstance(node.iter, ast.Call) and isinstance(node.iter.func, ast.Name) and node.iter.func.id == "range":
                range_args = node.iter.args
                if len(range_args) == 1:
                    start, end = "0", ast.unparse(range_args[0])
                else:
                    start, end = ast.unparse(range_args[0]), ast.unparse(range_args[1])
                target = ast.unparse(node.target)
                lines.append(f"FOR {target} <- {start} TO {end}")
                for stmt in node.body:
                    lines.extend(parse_node(stmt, level + 1))
                lines.append(f"NEXT {target}")

        elif isinstance(node, ast.While):
            condition = ast.unparse(node.test).strip()
            lines.append(f"WHILE {condition} DO")
            for stmt in node.body:
                lines.extend(parse_node(stmt, level + 1))
            lines.append("ENDWHILE")

        elif isinstance(node, ast.Expr):
            if isinstance(node.value, ast.Call):
                func_name = getattr(node.value.func, 'id', '')
                if func_name == "print":
                    args = [ast.unparse(arg) for arg in node.value.args]
                    for arg in args:
                        lines.append(f"OUTPUT {arg}")
                elif func_name == "input":
                    lines.append("INPUT value")
                else:
                    lines.append(f"Call {func_name}")

        elif isinstance(node, ast.Assign):
            target = ast.unparse(node.targets[0])
            value = ast.unparse(node.value)
            lines.append(f"{target} = {value}")

        elif isinstance(node, ast.Return):
            value = ast.unparse(node.value) if node.value else ""
            lines.append(f"RETURN {value}")

        return lines

    for node in tree.body:
        pseudocode.extend(parse_node(node))

    return ["START"] + pseudocode + ["STOP"]

def generate_flowchart(pseudocode, font_path="./fonts/NotoSans-Regular.ttf", size=20, output="flowchart.png"):
    font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "fonts", "NotoSans-Regular.ttf"))
    font_data = {"path": font_path, "size": size}

    # Save pseudocode to intermediate file (optional for debugging)
    with open("enter.txt", "w", encoding="utf-8") as f:
        for line in pseudocode:
            f.write(line + "\n")

    chart_code, max_branch, max_y, layer_height, branch_width = translation(pseudocode, font_data)
    img = drawer(chart_code, max_branch, max_y, layer_height, branch_width, font_data)
    img.save(output)
    print(f"[SUCCESS] Flowchart saved as '{output}'")

def main(input_file="sample.py"):
    input_file = os.path.abspath(input_file)
    if not os.path.exists(input_file):
        print(f"[ERROR] '{input_file}' not found.")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        code = f.read()

    print("[INFO] Converting Python to pseudocode...")
    pseudo = python_to_pseudocode(code)

    print("\n[PSEUDOCODE]:")
    for line in pseudo:
        print(" -", line)

    print("\n[INFO] Generating flowchart...")

    # Save output next to input file
    base = os.path.splitext(os.path.basename(input_file))[0]
    output_name = f"{base}_flowchart.png"
    output_path = os.path.join(os.path.dirname(input_file), output_name)

    generate_flowchart(pseudo, output=output_path)
