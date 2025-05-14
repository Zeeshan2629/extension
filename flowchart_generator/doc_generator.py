from fpdf import FPDF
import google.generativeai as genai
import os

# 🔐 Secure this key properly in production
API_KEY = "AIzaSyCmpVi6X-zA7SgpRWiD3Py_ElRsyeshoZU"
genai.configure(api_key=API_KEY)

def generate_code_documentation(input_path="sample.py", output_path=None):
    try:
        # Read code from the input file
        with open(input_path, 'r', encoding='utf-8') as file:
            code_content = file.read()
    except FileNotFoundError:
        print(f" File not found: {input_path}")
        return

    # Generate explanation using Gemini
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([
        code_content,
        "Explain this code in detail."
    ])

    # Auto-generate output path if not provided
    if output_path is None:
        base = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(os.path.dirname(input_path), f"{base}_documentation.pdf")

    pdf = FPDF()
    pdf.add_page()

    # Add Unicode font
    font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "fonts", "DejaVuSans.ttf"))
    pdf.add_font('DejaVu', '', font_path, uni=True)
    pdf.set_font("DejaVu", size=12)

    # Add response text
    try:
        pdf.multi_cell(0, 10, response.text)
        pdf.output(output_path)
        print(f" PDF saved to: {output_path}")
        return output_path
    except Exception as e:
        print(f" Failed to save PDF: {e}")
        return
