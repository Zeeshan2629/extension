from sentence_transformers import SentenceTransformer
import numpy as np

# Load once globally
model = SentenceTransformer("all-MiniLM-L6-v2")

def chunk_text(text, max_length=500):
    """
    Splits long text into smaller chunks of ~500 characters.
    Returns a list of text chunks.
    """
    lines = text.split('\n')
    chunks, current = [], ""

    for line in lines:
        if len(current) + len(line) < max_length:
            current += line + " "
        else:
            chunks.append(current.strip())
            current = line + " "
    if current:
        chunks.append(current.strip())
    return chunks


def embed_chunks(chunks):
    """
    Creates vector embeddings for each text chunk.
    Returns numpy array of embeddings.
    """
    embeddings = model.encode(chunks)
    return np.array(embeddings)
