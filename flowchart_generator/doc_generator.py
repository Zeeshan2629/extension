from fpdf import FPDF
import google.generativeai as genai
import os
import sys

# Safe UTF-8 console printing
sys.stdout.reconfigure(encoding='utf-8')

# ⚠ Replace with your free-tier Gemini API key
API_KEY = "AIzaSyCDZOTswYpt_Ek8ItQpSeyC3RNHEh-hp0U"
genai.configure(api_key=API_KEY)


def generate_code_documentation(input_path="sample.py", output_path=None):
    # 1️⃣ Read input Python file
    try:
        with open(input_path, 'r', encoding='utf-8') as file:
            code_content = file.read()
    except FileNotFoundError:
        print(f"❌ File not found: {input_path}")
        return

    # 2️⃣ Initialize model with free-tier compatible Gemini model
    try:
        try:
            model = genai.GenerativeModel("models/gemini-2.5-flash")
        except Exception:
            # fallback to pro if flash fails
            model = genai.GenerativeModel("models/gemini-2.5-pro")

        # 3️⃣ Generate documentation
        response = model.generate_content(
            contents=[
                code_content,
                (
                    "Explain this Python code in a detailed, structured format. "
                    "Cover each function, logic, and code block. Identify inefficiencies, "
                    "and recommend optimizations. Write it as developer documentation. "
                    "Do not use markdown or formatting symbols."
                )
            ]
        )

    except Exception as e:
        print(f"❌ Error generating content: {e}")
        return

    # 4️⃣ Determine output PDF path
    if output_path is None:
        base = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(os.path.dirname(input_path), f"{base}_documentation.pdf")

    # 5️⃣ Generate PDF
    try:
        pdf = FPDF()
        pdf.add_page()

        # Use DejaVu font if available, otherwise fallback to Arial
        font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "fonts", "DejaVuSans.ttf"))
        if os.path.exists(font_path):
            pdf.add_font('DejaVu', '', font_path, uni=True)
            pdf.set_font("DejaVu", size=12)
        else:
            pdf.set_font("Arial", size=12)

        explanation = getattr(response, "text", str(response))
        pdf.multi_cell(0, 10, explanation)

        # Save PDF
        pdf.output(output_path)
        print(f"✅ PDF saved to: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Failed to save PDF: {e}")
        return
