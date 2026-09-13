def chunk_text(pages: list[dict], chunk_size: int = 1000, overlap: int = 200) -> list[dict]:
    if overlap >= chunk_size:
        raise ValueError("Overlap must be smaller than chunk size")

    chunks = []

    for data in pages:
        page_number = data["page"]
        text = data["text"]

        start = 0

        while start < len(text):
            end = start + chunk_size

            chunk = text[start:end]

            chunks.append({
                "page": page_number,
                "text": chunk,
            })

            start += chunk_size - overlap

    return chunks