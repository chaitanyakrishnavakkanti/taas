
import os
import pickle
from typing import List, Dict
from PyPDF2 import PdfReader
from tqdm import tqdm

def load_pdfs(folder_path: str) -> List[Dict[str, str]]:
    """Load all PDFs from folder_path. Returns list of {"filename","content"}."""
    docs = []
    if not os.path.isdir(folder_path):
        return docs
    for filename in sorted(os.listdir(folder_path)):
        if filename.lower().endswith(".pdf"):
            path = os.path.join(folder_path, filename)
            try:
                reader = PdfReader(path)
                pages_text = []
                for page in reader.pages:
                    txt = page.extract_text()
                    if txt:
                        pages_text.append(txt)
                text = " ".join(pages_text).strip()
                if text:
                    docs.append({"filename": filename, "content": text})
                else:
                    print(f"[warn] no text extracted from {filename}")
            except Exception as e:
                print(f"[error] failed to read {filename}: {e}")
    return docs

def load_texts(folder_path: str) -> List[Dict[str, str]]:
    """Load plain .txt files from folder_path."""
    docs = []
    if not os.path.isdir(folder_path):
        return docs
    for filename in sorted(os.listdir(folder_path)):
        if filename.lower().endswith(".txt"):
            path = os.path.join(folder_path, filename)
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read().strip()
                if text:
                    docs.append({"filename": filename, "content": text})
            except Exception as e:
                print(f"[error] failed to read {filename}: {e}")
    return docs

def chunk_text(text: str, chunk_size: int = 300, overlap: int = 50) -> List[str]:
    """
    Chunk text by words.
    chunk_size = number of words per chunk (default 300)
    overlap = number of overlapping words between chunks (default 50)
    """
    words = text.split()
    if not words:
        return []
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
       
        start = end - overlap
        if start < 0:
            start = 0
    return chunks

def docs_to_chunks(docs: List[Dict[str, str]], chunk_size: int = 300, overlap: int = 50) -> List[Dict]:
    """
    Convert list of docs into a list of chunk dicts:
    {"doc_id":..., "chunk_id":..., "text":...}
    """
    all_chunks = []
    for doc in docs:
        chunks = chunk_text(doc["content"], chunk_size=chunk_size, overlap=overlap)
        for i, ch in enumerate(chunks):
            all_chunks.append({
                "doc_id": doc["filename"],
                "chunk_id": f"{doc['filename']}_chunk_{i}",
                "text": ch
            })
    return all_chunks

def save_chunks(chunks: List[Dict], out_path: str = "embeddings/chunks.pkl"):
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "wb") as f:
        pickle.dump(chunks, f)
    print(f"[info] Saved {len(chunks)} chunks to {out_path}")

def load_chunks(path: str = "embeddings/chunks.pkl") -> List[Dict]:
    with open(path, "rb") as f:
        return pickle.load(f)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Ingest PDFs/TXT and create chunks")
    parser.add_argument("--data_dir", default="data", help="folder with PDFs/TXT")
    parser.add_argument("--out", default="embeddings/chunks.pkl", help="output chunks pickle")
    parser.add_argument("--chunk_size", type=int, default=300)
    parser.add_argument("--overlap", type=int, default=50)
    args = parser.parse_args()

    docs = load_pdfs(args.data_dir) + load_texts(args.data_dir)
    print(f"[info] Loaded {len(docs)} document(s) from {args.data_dir}")
    chunks = docs_to_chunks(docs, chunk_size=args.chunk_size, overlap=args.overlap)
    print(f"[info] Created {len(chunks)} chunk(s) (chunk_size={args.chunk_size}, overlap={args.overlap})")
    save_chunks(chunks, args.out)
