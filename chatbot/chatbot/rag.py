# chatbot/rag.py
from embedder import embed_chunks
from gemini_client import generate_answer

def answer_question(query, store, top_k=3):
    """
    Retrieves relevant chunks and uses Gemini to answer.
    Returns dict: {"answer": str, "context_used": [{chunk, score}, ...]}
    """
    # 1) embed query
    q_embed = embed_chunks([query])  # returns numpy array shape (1, dim)

    # 2) retrieve from store
    results = store.search(q_embed, top_k=top_k)

    # 3) build context and prompt
    context = "\n\n".join([r["chunk"] for r in results])
    prompt = f"""You are an assistant that answers using the provided document context. If the answer is not present, reply: "I couldn't find that information in the document. but give a relevant answer, also frame the answer nicely, if asked to code, please provide the code. dont make text bold"

Context:
{context}

Question: {query}
Answer:"""

    # 4) call Gemini
    answer = generate_answer(prompt)

    return {"answer": answer, "context_used": results}
