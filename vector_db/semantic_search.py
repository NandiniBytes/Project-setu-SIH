import os
import sys
import json
from typing import Dict, List, Tuple

os.environ["TOKENIZERS_PARALLELISM"] = "false"

try:
    import chromadb
except ImportError as exc:
    print("chromadb is required. Install with: pip install chromadb", file=sys.stderr)
    raise

try:
    from sentence_transformers import SentenceTransformer
except ImportError as exc:
    print(
        "sentence-transformers is required. Install with: pip install sentence-transformers",
        file=sys.stderr,
    )
    raise

try:
    from fhir.resources.codesystem import CodeSystem
except ImportError as exc:
    print("fhir.resources is required. Install with: pip install fhir.resources", file=sys.stderr)
    raise


def load_codesystem(path: str) -> CodeSystem:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Input file not found: {path}")

    # Use fhir.resources to parse and validate the FHIR CodeSystem JSON
    codesystem = CodeSystem.parse_file(path, content_type="application/json")
    if not getattr(codesystem, "concept", None):
        raise ValueError("No concepts found in the provided CodeSystem")
    return codesystem


def flatten_concepts(concepts: List[Dict]) -> List[Tuple[str, str, str]]:
    """
    Returns a flat list of tuples: (code, display, definition)
    Handles nested CodeSystem.concept recursively.
    """
    flattened: List[Tuple[str, str, str]] = []

    def dfs(items: List[Dict]) -> None:
        for item in items or []:
            code = getattr(item, "code", None)
            display = getattr(item, "display", None)
            definition = getattr(item, "definition", None)

            if code and display:
                flattened.append((code, display, definition or ""))

            # Recurse into nested concepts if present
            child_concepts = getattr(item, "concept", None)
            if child_concepts:
                dfs(child_concepts)

    dfs(concepts)
    return flattened


def main() -> None:
    input_path = os.path.join(os.getcwd(), "CodeSystem-NAMASTE.json")
    db_path = os.path.join(".", "namaste_db")
    collection_name = "namaste"

    # Load FHIR CodeSystem
    codesystem = load_codesystem(input_path)

    # Prepare model
    model_name = "all-MiniLM-L6-v2"
    model = SentenceTransformer(model_name)

    # Initialize persistent Chroma client and collection
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_or_create_collection(name=collection_name, metadata={"hnsw:space": "cosine"})

    # Extract and flatten concepts
    concepts = flatten_concepts(codesystem.concept)

    # Deduplicate by code while preserving first occurrence
    seen: set = set()
    ids: List[str] = []
    documents: List[str] = []
    metadatas: List[Dict[str, str]] = []

    for code, display, definition in concepts:
        if code in seen:
            continue
        seen.add(code)

        text_parts = [display]
        if definition:
            text_parts.append(definition)
        text = ": ".join(text_parts)

        ids.append(code)
        documents.append(text)
        metadatas.append({"display": display})

    if not ids:
        print("No valid concepts with codes to process.")
        return

    # Encode in reasonably sized batches to manage memory
    batch_size = 256
    total_added = 0
    for start in range(0, len(ids), batch_size):
        end = start + batch_size
        batch_docs = documents[start:end]
        batch_ids = ids[start:end]
        batch_metas = metadatas[start:end]

        embeddings = model.encode(batch_docs, normalize_embeddings=True).tolist()

        # Add to ChromaDB
        collection.add(ids=batch_ids, embeddings=embeddings, metadatas=batch_metas)
        total_added += len(batch_ids)

    print(f"Successfully processed and saved {total_added} medical terms to {db_path} (collection '{collection_name}').")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)