import ollama
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



# Load your index and metadata back up
loaded_index = IdMapIndex.load("thp_vectors.tvim")
with open("jump_metadata.json", "r") as f:
    loaded_metadata = json.load(f)

# Vectorize the user's question
embedder = BGEEmbedder()

# Construct the LLM Prompt
system_prompt = (
"You are an elite sports science and vertical jump training assistant, who has help many athletes increase their vertical jump height, some even reaching 50-inch vertical jumps. "
"Your task is to answer the user's question accurately based on the provided trancscript context. "
"If the context does not contain the answer, politely state that your don't know based on the data provided. "
"Keep your tone analytical, precise, and motivating. "
)

user_question = ""

print("\nStreaming response from Hermes 3...")
print("-"*50)

CHUNK_OFFSET = 3
SEARCH_DEPTH = 1

while True:
    user_question = input("Enter your question (or 'exit' to quit): ")
    if user_question == 'exit':
            break

    query_vector = embedder.embed_query(user_question)

    # Query turbovec for the top matching ID
    scores, matched_ids = loaded_index.search(np.array([query_vector]), k=4)
    top_match_ids = [int(i) for i in matched_ids[0]]

    for i in range(SEARCH_DEPTH):
        for j in range(len(top_match_ids)):
            query_vector = embedder.embed_query(loaded_metadata[str(top_match_ids[j])]['text'])
            scores, ids = loaded_index.search(np.array([query_vector]), k=4)
            top_ids = [int(i) for i in ids[0]]
            top_match_ids.extend(top_ids)

    context = []
    sources = []

    # Pull the text chunk instantly from your metadata store
    for rank, match_id in enumerate(top_match_ids):
        text = ""

        for i in range(match_id - CHUNK_OFFSET, match_id + CHUNK_OFFSET + 1):
            if i < 0 or i >= len(loaded_metadata):
                continue

            result = loaded_metadata[str(i)]

            if i == match_id - CHUNK_OFFSET:
                sources.append(result['metadata']['timestamp_link'])

            text += result['text'] + " "


        # Formate each chunk nicely so the LLM sees them clearly separated
        context.append(text.strip())
        sources.append(result['metadata']['timestamp_link'])

    # Combine all the context into a single string
    combined_context = "\n\n".join(context)

    user_prompt = f"""
    Context from training videos:
    \"\"\"
    {combined_context}
    \"\"\"

    User Question: {user_question}

    Provide a direct answer. At the very end of your response, provide the source video citation link like this: '[Source Video Link](url)'.
    """

    #print(combined_context + "\n" + "-" * 50)

    # Call Hermes 3 via Ollama
    response = ollama.chat(
        model="hermes3:8b", 
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        stream=True,
        options={
            "top_p": 0.9,              # Nucleus sampling: only consider tokens with a cumulative probability of at least 0.9
            "top_k": 40,               # Limits the number of tokens to consider at each step
            "temperature": 0.7,        # Controls the creativity of the generated text
            "num_ctx": 4096            # Maximum context length
        }
    )
    
    # Print the streamed response tokens in real-time
    for chunk in response:
        print(chunk['message']['content'], end='', flush=True)
    print("\n" + "-" * 50)

    # Also print your exact citation link just in case the LLM formatting varies
    print(f"Verified Reference Link: {sources}")