import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import pipeline

EMBEDDINGS_FILE = "../embeddings/embeddings.pkl"
MODEL_NAME = "multi-qa-MPNet-base-dot-v1"
SUMMARIZER_MODEL = "facebook/bart-large-cnn"

def load_embeddings(file_path=EMBEDDINGS_FILE):
    with open(file_path, "rb") as f:
        embeddings = pickle.load(f)
    vectors = np.array([e["vector"] for e in embeddings])
    texts = [e["text"] for e in embeddings]
    return embeddings, vectors, texts

def retrieve(query, vectors, texts, model, top_n=5):
    query_vector = model.encode(query, normalize_embeddings=True)
    similarities = cosine_similarity([query_vector], vectors)[0]
    top_indices = similarities.argsort()[-top_n:][::-1]
    results = [(texts[i], similarities[i]) for i in top_indices]
    return results

def summarize_chunks(chunks, summarizer, max_length=150):
    combined_text = " ".join([text for text, _ in chunks])
    if len(combined_text.split()) > 1000:
        combined_text = " ".join(combined_text.split()[:1000])
    summary = summarizer(combined_text, max_length=max_length, min_length=40, do_sample=False)
    return summary[0]['summary_text']

if __name__ == "__main__":
    embeddings, vectors, texts = load_embeddings()
    model = SentenceTransformer(MODEL_NAME)
    summarizer = pipeline("summarization", model=SUMMARIZER_MODEL)

    print("✅ Retriever loaded. Type your query or 'exit' to quit.")

    while True:
        query = input("\nEnter your query: ")
        if query.lower() == "exit":
            break

        top_chunks = retrieve(query, vectors, texts, model, top_n=5)

        print("\nTop relevant chunks:")
        for text, score in top_chunks:
            print(f"- {text} (score: {score:.4f})")

        summary = summarize_chunks(top_chunks, summarizer)
        print("\nAnswer:")
        print(summary)
