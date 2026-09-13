import pdfplumber

def extract_text(file_path: str) -> list[dict]:
    result = []

    with pdfplumber.open(file_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            page_text = page.extract_text()

            if page_text:
                result.append({
                    "page": page_number,
                    "text": page_text,
                })

    return result