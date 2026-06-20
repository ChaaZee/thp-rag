import json
import numpy as np
from turbovec import IdMapIndex
from sentence_transformers import SentenceTransformer

class BGEEmbedder:
    def __init__(self, model_name="BAAI/bge-large-en-v1.5"):
        """
        Initializes the BGE model. It automatically detects and uses GPU (CUDA/MPS) 
        if available, otherwise defaults to CPU.
        """
        print(f"Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)

    def embed_chunks(self, chunks: list[str]) -> np.ndarray:
        """
        Convert your dataset transcript chunks into embeddings.
        No special prefix instruction is needed for the documents themselves.
        """
        # normalize_embeddings=True ensures cosine similarity works via simple dot product
        embeddings = self.model.encode(chunks, normalize_embeddings=True, show_progress_bar=True)
        return np.array(embeddings)
    
    def embed_query(self, query: str) -> np.ndarray:
        """
        Convert a user's search query into an embedding.
        BGE v1.5 requires a specific instruction prefix for queries to optimize retrieval.
        """
        instructional_query = f"Represent this sentence for searching relevant passages: {query}"
        embedding = self.model.encode(instructional_query, normalize_embeddings=True)
        return np.array(embedding)
    
def load_chunks_from_jsonl(file_path: str) -> list[dict]:
    chunks = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            # Strip whitespace and skip empty lines if they exist
            cleaned_line = line.strip()
            if cleaned_line:
                chunk = json.loads(cleaned_line)
                chunks.append(chunk)
    return chunks



# 1. Load your index and metadata back up
loaded_index = IdMapIndex.load("thp_vectors.tvim")
with open("jump_metadata.json", "r") as f:
    loaded_metadata = json.load(f)

# 2. Vectorize the user's question
embedder = BGEEmbedder()
query_vector = embedder.embed_query("How do I fix my penultimate step?")


# 3. Query turbovec for the top matching ID
scores, matched_ids = loaded_index.search(np.array([query_vector]), k=1)
top_match_id = int(matched_ids[0][0])

# 4. Pull the text chunk instantly from your metadata store
result = loaded_metadata[str(top_match_id)]

print(f"Retrieved Document:\n{result['text']}\nSource: {result['metadata']['timestamp_link']}")