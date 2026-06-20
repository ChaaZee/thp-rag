import numpy as np
from sentence_transformers import SentenceTransformer
import json
import numpy as np
from turbovec import IdMapIndex

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
    
DIMENSION = 1024
BIT_WIDTH = 4

index = IdMapIndex(dim=DIMENSION, bit_width=BIT_WIDTH)

dataset = load_chunks_from_jsonl("cleaned_rag_dataset.jsonl")
    
embedder = BGEEmbedder()

vector_list = []
id_list = []
metadata_dict = {}

for i, item in enumerate(dataset):
    unique_id = np.uint64(1000 + i)

    # Generate the embedding for the current chunk
    vector = embedder.embed_chunks([item["text"]])[0]

    vector_list.append(vector)
    id_list.append(unique_id)

    # Map the text and links back to that exact ID
    metadata_dict[int(unique_id)] ={
        "text": item["text"],
        "metadata": item["metadata"]
    }

# Bulk add vectors into turbovec
index.add_with_ids(np.array(vector_list), np.array(id_list, dtype=np.uint64))

# Save the turbovec binary index
index.write("thp_vectors.tvim")

# Save the metadata text store alongside it
with open("jump_metadata.json", "w", encoding="utf-8") as f:
    json.dump(metadata_dict, f, indent=4)

print("Saved vector index and text lookup database successfully.")