import faiss
import numpy as np

class VectorStore:
    """
    Simple FAISS-based vector store for semantic search.
    Stores text chunks and their embeddings for retrieval.
    """

    def __init__(self, embedding_dim: int):
        self.index = faiss.IndexFlatL2(embedding_dim)
        self.chunks = []

    def add(self, chunks, embeddings):
        """
        Adds new text chunks and embeddings to the store.
        """
        self.index.add(np.array(embeddings).astype('float32'))
        self.chunks.extend(chunks)

    def search(self, query_embedding, top_k=3):
        """
        Returns the top_k most similar text chunks to the query.
        """
        query_embedding = np.array(query_embedding).astype('float32')
        distances, indices = self.index.search(query_embedding, top_k)
        results = []
        for i, idx in enumerate(indices[0]):
            results.append({
                "chunk": self.chunks[idx],
                "score": float(distances[0][i])
            })
        return results
