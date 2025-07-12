import os
import pickle
import faiss
from sentence_transformers import SentenceTransformer

class RAGPipeline:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.chunks = []
        self.index = None

    def load_chunks(self, chunks):
        self.chunks = chunks
        embeddings = self.model.encode(chunks)
        self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(embeddings)
        with open("app/cache/chunks.pkl", "wb") as f:
            pickle.dump({"chunks": chunks, "embeddings": embeddings}, f)

    def load_existing_index(self):
        with open("app/cache/chunks.pkl", "rb") as f:
            data = pickle.load(f)
            self.chunks = data["chunks"]
            embeddings = data["embeddings"]
            self.index = faiss.IndexFlatL2(embeddings.shape[1])
            self.index.add(embeddings)

    def query(self, question, top_k=10):
        q_embedding = self.model.encode([question])
        D, I = self.index.search(q_embedding, top_k)
        return [self.chunks[i] for i in I[0]]

    def highlight_answer(self, answer, retrieved_chunks):
        """Highlight the chunk(s) containing the answer or its key phrases."""
        answer_lower = answer.lower()
        highlights = []
        for chunk in retrieved_chunks:
            if any(phrase in chunk.lower() for phrase in answer_lower.split()):
                highlights.append(f"**[HIT]** {chunk}")
            else:
                highlights.append(chunk)
        return highlights