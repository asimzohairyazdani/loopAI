
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATA_DIR = os.path.join(BASE_DIR, "data")
HOLDINGS_FILE = os.path.join(DATA_DIR, "holdings.csv")
TRADES_FILE = os.path.join(DATA_DIR, "trades.csv")

FAISS_INDEX_PATH = os.path.join(BASE_DIR, "faiss_index")
FAISS_DIR = FAISS_INDEX_PATH  # For backwards compatibility

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL = "mistral"

FALLBACK_RESPONSE = "Sorry can not find the answer"

# Retrieval tuning - Industry best practices for RAG
TOP_K = 15  # Retrieve more candidates for ranking
SIMILARITY_THRESHOLD = 2.0  # Distance threshold for FAISS (L2 norm). 2.0 is good for semantic search
MIN_RELEVANT_DOCS = 1  # Minimum number of docs to proceed (at least 1)
