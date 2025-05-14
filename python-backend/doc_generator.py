from fpdf import FPDF
import google.generativeai as genai

API_KEY = "AIzaSyCmpVi6X-zA7SgpRWiD3Py_ElRsyeshoZU"
genai.configure(api_key=API_KEY)

def generate_code_documentation(input_path="sample.py", output_path="code_documentation.pdf"):
    with open(input_path, 'r') as file:
        code_content = file.read()

    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([
        code_content,
        "Explain this code in detail."
    ])

    pdf = FPDF()
    pdf.add_page()

    # ✅ Use Unicode-compatible TTF font
    font_path = "fonts/DejaVuSans.ttf"
    pdf.add_font("DejaVu", "", font_path, uni=True)
    pdf.set_font("DejaVu", size=12)

    # ✅ Write UTF-8 content
    pdf.multi_cell(0, 10, response.text)

    pdf.output(output_path)
    return output_path
