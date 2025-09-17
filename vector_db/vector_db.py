import os
from typing import Dict, List

os.environ["TOKENIZERS_PARALLELISM"] = "false"

try:
    import chromadb
except ImportError as exc:
    raise ImportError(
        "chromadb is required. Install with: pip install chromadb"
    ) from exc

try:
    from sentence_transformers import SentenceTransformer
except ImportError as exc:
    raise ImportError(
        "sentence-transformers is required. Install with: pip install sentence-transformers"
    ) from exc


class TermSearch:
    """
    Reusable semantic search helper for NAMASTE medical terms stored in ChromaDB.
    """

    def __init__(
        self, db_path: str = "./namaste_db", collection_name: str = "namaste"
    ) -> None:
        # Load embedding model
        self.model_name = "all-MiniLM-L6-v2"
        self.model = SentenceTransformer(self.model_name)

        # Initialize persistent Chroma client and collection
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(
            name=collection_name, metadata={"hnsw:space": "cosine"}
        )

    def find_similar(self, query: str, top_k: int = 5) -> List[Dict[str, object]]:
        """
        Find the top_k most similar terms given a text query.

        Returns a list of dictionaries with keys: code, display, distance.
        """
        if not query or not query.strip():
            return []

        embedding = self.model.encode([query], normalize_embeddings=True)[0].tolist()

        # This part of the provided code had a small bug, so it's been corrected
        # to use the `query` variable from the function's arguments.
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        ids = results.get("ids", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        formatted: List[Dict[str, object]] = []
        for idx, code in enumerate(ids):
            meta = metadatas[idx] if idx < len(metadatas) else {}
            distance = float(distances[idx]) if idx < len(distances) else None
            formatted.append(
                {
                    "code": code,
                    "display": meta.get("display"),
                    "distance": distance,
                }
            )

        return formatted


if __name__ == "__main__":
    # Simple demo usage
    search = TermSearch()
    example_query = "fever and cough"
    results = search.find_similar(example_query, top_k=5)
    print(f"Query: '{example_query}'")
    for i, r in enumerate(results, 1):
        print(f"{i}. code={r['code']} display={r['display']} distance={r['distance']}")
