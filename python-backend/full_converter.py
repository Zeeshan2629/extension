import ast
import os
from flowchart_generator.Converter import translation, drawer
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
                    lines.append("INPUT value")  # can't infer var name here
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
    import os
    font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "fonts", "NotoSans-Regular.ttf"))
    font_data = {"path": font_path, "size": size}

    with open("enter.txt", "w") as f:
        for line in pseudocode:
            f.write(line + "\n")

    chart_code, max_branch, max_y, layer_height, branch_width = translation(pseudocode, font_data)
    img = drawer(chart_code, max_branch, max_y, layer_height, branch_width, font_data)
    img.save(output)
    print(f"✅ Flowchart saved as '{output}'")

def main():
    if not os.path.exists("sample.py"):
        print("❌ Error: 'sample.py' not found.")
        return

    with open("sample.py", "r") as f:
        code = f.read()

    print("🔁 Converting Python to pseudocode...")
    pseudo = python_to_pseudocode(code)

    print("\n📝 Pseudocode:")
    for line in pseudo:
        print(" -", line)

    print("\n📊 Generating flowchart...")
    generate_flowchart(pseudo)

if __name__ == "__main__":
    main()
