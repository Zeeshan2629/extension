import pdfplumber

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts text content from a PDF file.
    Returns the text as a single string.
    """
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        if not text.strip():
            text = "[No readable text found in PDF.]"
    except Exception as e:
        text = f"[Error extracting text: {e}]"
    return text
