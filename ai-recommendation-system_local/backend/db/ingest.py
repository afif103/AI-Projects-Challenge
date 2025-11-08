# backend/db/ingest.py
import json
from pathlib import Path
from backend.db.vector_store import get_vector_store

def ingest_sample_data():
    data_path = Path(__file__).parent.parent.parent / "data" / "sample_items.json"
    if not data_path.exists():
        print(f"Data file not found: {data_path}")
        return

    with open(data_path) as f:
        items = json.load(f)

    texts = [f"{item['title']} - {item['description']}" for item in items]
    metadatas = [{"id": item["id"], "title": item["title"], **item.get("tags", {})} for item in items]

    vector_store = get_vector_store()
    vector_store.add_texts(texts=texts, metadatas=metadatas)
    print(f"Indexed {len(texts)} items into vector DB.")

if __name__ == "__main__":
    ingest_sample_data()