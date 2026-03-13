import pypdf
import io

def parse_pdf(file_bytes: bytes) -> str:
    """
    Extract text from PDF bytes.
    """
    pdf_reader = pypdf.PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text.strip()

def format_score(score: float) -> str:
    """
    Format score for display.
    """
    return f"{score:.1f}/100"
