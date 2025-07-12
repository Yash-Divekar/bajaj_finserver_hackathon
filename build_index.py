import os
import pdfplumber
from app.rag_pipeline import RAGPipeline

def overlapping_chunks(text, window=200, stride=100):
    """Split text into overlapping chunks of `window` words, moving by `stride` words."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), stride):
        chunk = " ".join(words[i:i+window])
        if len(chunk) > 40:
            chunks.append(chunk)
        if i + window >= len(words):
            break
    return chunks

pipeline = RAGPipeline()
all_chunks = []

for file in os.listdir("data"):
    if file.endswith(".pdf"):
        with pdfplumber.open(f"data/{file}") as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    all_chunks.extend(overlapping_chunks(text, window=200, stride=100))

pipeline.load_chunks(all_chunks)