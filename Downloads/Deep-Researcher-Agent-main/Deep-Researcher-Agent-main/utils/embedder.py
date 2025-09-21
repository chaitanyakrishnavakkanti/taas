import pickle
import os
import numpy as np
from sentence_transformers import SentenceTransformer
import argparse
import re

AVAILABLE_MODELS = {
    "bge-small": "BAAI/bge-small-en-v1.5",
    "bge-base": "BAAI/bge-base-en-v1.5",
    "mpnet-qa": "multi-qa-MPNet-base-dot-v1"
}

def split_text_into_chunks(text, max_sentences=3):
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    chunks = []
    for para in paragraphs:
        sentences = re.split(r'(?<=[.!?]) +', para)
        for i in range(0, len(sentences), max_sentences):
            chunk_text = " ".join(sentences[i:i+max_sentences])
            if chunk_text:
                chunks.append({"text": chunk_text})
    return chunks

def load_chunks(pkl_file):
    if not os.path.exists(pkl_file):
        raise FileNotFoundError(f"Chunks file not found: {pkl_file}")
    with open(pkl_file, "rb") as f:
        return pickle.load(f)

def generate_embeddings(chunks, model_choice="mpnet-qa", save_path="embeddings/embeddings.pkl"):
    if model_choice not in AVAILABLE_MODELS:
        raise ValueError(f"Invalid model choice. Pick from: {list(AVAILABLE_MODELS.keys())}")

    model_name = AVAILABLE_MODELS[model_choice]
    print(f"🔹 Using embedding model: {model_name}")

    model = SentenceTransformer(model_name)
    embeddings = []

    for idx, chunk in enumerate(chunks):
        content = chunk.get("text")
        metadata = chunk.get("metadata", {})
        vector = model.encode(content, normalize_embeddings=True)
        embeddings.append({"vector": np.array(vector), "metadata": metadata, "text": content})
        if (idx + 1) % 5 == 0 or idx == len(chunks) - 1:
            print(f"✅ Embedded {idx+1}/{len(chunks)} chunks")

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "wb") as f:
        pickle.dump(embeddings, f)

    print(f"\n🎉 Saved {len(embeddings)} embeddings to {save_path}")
    return embeddings

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate embeddings for text chunks.")
    parser.add_argument("--model", default="mpnet-qa", choices=list(AVAILABLE_MODELS.keys()))
    parser.add_argument("--chunks", default=os.path.join(os.path.dirname(__file__), "../embeddings/chunks.pkl"))
    parser.add_argument("--save", default=os.path.join(os.path.dirname(__file__), "../embeddings/embeddings.pkl"))
    parser.add_argument("--source", help="Path to raw text file to split into chunks", default=None)
    args = parser.parse_args()

    # If a raw text source is provided, split it into paragraph-level chunks and save
    if args.source:
        with open(args.source, "r", encoding="utf-8") as f:
            text = f.read()
        chunks = split_text_into_chunks(text)
        os.makedirs(os.path.dirname(args.chunks), exist_ok=True)
        with open(args.chunks, "wb") as f:
            pickle.dump(chunks, f)
        print(f"✅ Created {len(chunks)} paragraph-level chunks at {args.chunks}")
    else:
        chunks = load_chunks(args.chunks)

    existing_embeddings = []
    existing_texts = set()

    if os.path.exists(args.save):
        with open(args.save, "rb") as f:
            existing_embeddings = pickle.load(f)
        existing_texts = set(e["text"] for e in existing_embeddings)
        print(f"✅ Loaded {len(existing_embeddings)} existing embeddings from {args.save}")

    new_chunks = [c for c in chunks if c.get("text") not in existing_texts]

    if new_chunks:
        print(f"🔹 Generating embeddings for {len(new_chunks)} new chunks")
        new_embeddings = generate_embeddings(new_chunks, model_choice=args.model, save_path=args.save)
        all_embeddings = existing_embeddings + new_embeddings
        with open(args.save, "wb") as f:
            pickle.dump(all_embeddings, f)
        print(f"🎉 Total embeddings now: {len(all_embeddings)}")
    else:
        print("✅ No new chunks to embed. All embeddings are up to date.")
