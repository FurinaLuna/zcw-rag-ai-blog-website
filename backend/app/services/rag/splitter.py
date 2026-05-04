import re


def split_text(text: str, chunk_size: int = 200, chunk_overlap: int = 50) -> list[str]:
    if not text.strip():
        return []

    paragraphs = re.split(r"\n\s*\n", text)

    chunks: list[str] = []
    current_chunk = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        if len(current_chunk) + len(para) <= chunk_size:
            current_chunk = (current_chunk + "\n\n" + para).strip()
        else:
            if current_chunk:
                chunks.append(current_chunk)
            if len(para) <= chunk_size:
                current_chunk = para
            else:
                sentences = re.split(r"(?<=[。！？.!?])\s*", para)
                for sent in sentences:
                    sent = sent.strip()
                    if not sent:
                        continue
                    if len(current_chunk) + len(sent) <= chunk_size:
                        current_chunk = (current_chunk + sent).strip()
                    else:
                        if current_chunk:
                            chunks.append(current_chunk)
                        current_chunk = sent
                chunks.append(current_chunk)
                current_chunk = ""

    if current_chunk:
        chunks.append(current_chunk)

    # Apply overlap
    if chunk_overlap > 0 and len(chunks) > 1:
        overlapped = []
        for i, chunk in enumerate(chunks):
            if i > 0:
                prev_end = chunks[i - 1][-chunk_overlap:] if len(chunks[i - 1]) > chunk_overlap else chunks[i - 1]
                chunk = prev_end + chunk
            overlapped.append(chunk)
        chunks = overlapped

    # Filter by size
    return [c for c in chunks if 50 <= len(c) <= 500]
