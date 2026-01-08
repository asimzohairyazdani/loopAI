# RAG POC - Retrieval Augmented Generation for Financial Data

A proof-of-concept application that uses Retrieval Augmented Generation (RAG) to answer natural language questions about financial holdings and trading data. This project combines FAISS vector search with the Mistral language model running locally via Ollama.

## What This Does

Ever wanted to ask questions about your financial portfolio in plain English instead of writing SQL queries? That's what this RAG system does. It takes your CSV data (holdings, trades, etc.), converts it into vectors, and lets you query it using natural language. The Mistral LLM provides context-aware answers based on what it finds in your data.

Example questions you can ask:
- "What are the main holdings in the portfolio?"
- "Tell me about the securities in the Garfield fund"
- "Which bonds are in the portfolio?"
- "What trading activity has occurred?"

## Getting Started

### Prerequisites

Before you start, make sure you have:
- Python 3.9+
- [Ollama](https://ollama.ai) installed and running on your machine
- A terminal/command line (zsh, bash, or similar)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/rag-poc.git
   cd rag-poc
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ensure Mistral is available locally** (see section below)

## Setting Up Mistral Locally with Ollama

This project uses [Ollama](https://ollama.ai) to run the Mistral model locally. This means everything runs on your machine—no API calls, no costs, and your data stays private.

### Quick Setup

1. **Download and install Ollama** from [ollama.ai](https://ollama.ai)

2. **Pull the Mistral model**
   ```bash
   ollama pull mistral
   ```
   This downloads the model (~4GB). First time might take a few minutes depending on your internet.

3. **Start Ollama** (if not already running)
   ```bash
   ollama serve
   ```
   Keep this running in a separate terminal while you use the RAG system.

4. **Verify it's working**
   ```bash
   ollama run mistral "Say hello"
   ```
   If you see a response, you're all set!

## Building the Vector Index

Before you can query your data, you need to build the FAISS index from your CSV files:

```bash
python -m scripts.build_index
```

This script reads your `data/holdings.csv` and `data/trades.csv`, converts them into vector embeddings, and creates a FAISS index that the RAG system uses for fast similarity search.

## Running the API

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`. You can also check out the interactive docs at `http://localhost:8000/docs`.

### Making Requests

Use the `/chat` endpoint to ask questions:

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the main holdings in the portfolio?"}'
```

Or use Python:
```python
import requests

response = requests.post(
    "http://localhost:8000/chat",
    json={"question": "What are the main holdings?"}
)
print(response.json()["answer"])
```

## Project Structure

```
rag-poc/
├── app/
│   ├── api/              # API routes
│   ├── services/         # Core RAG logic
│   │   ├── ingestion.py     # CSV loading
│   │   ├── rag.py           # RAG orchestration
│   │   ├── llm.py           # LLM interactions
│   │   └── vectorstore.py   # FAISS management
│   └── core/             # Configuration & logging
├── scripts/
│   └── build_index.py    # Index building script
├── data/
│   ├── holdings.csv      # Your holdings data
│   └── trades.csv        # Your trades data
├── faiss_index/          # Generated index (don't edit)
└── requirements.txt
```

## How It Works (Under the Hood)

1. **Ingestion**: CSV files are loaded and processed into documents
2. **Embedding**: Documents are converted to vectors using sentence-transformers
3. **Indexing**: Vectors are indexed in FAISS for fast similarity search
4. **Query**: When you ask a question, it's converted to a vector
5. **Retrieval**: Similar documents are found in the FAISS index
6. **Generation**: Mistral LLM generates an answer based on retrieved documents

## Configuration

Edit `app/core/config.py` to customize:
- Data file paths
- FAISS index location
- Ollama model and endpoint
- Other settings

## Testing

Check out `TEST_QUESTIONS.md` for example questions and expected behaviors to test your setup.

## Troubleshooting

### "Connection refused" when querying
Make sure Ollama is running! In another terminal:
```bash
ollama serve
```

### "Mistral not found"
Pull the model:
```bash
ollama pull mistral
```

### Index build fails
- Make sure your CSV files exist in the `data/` folder
- Check file paths in `app/core/config.py`
- Verify the CSV format matches what the ingestion script expects

### API returns empty answers
The vector search might not be finding relevant documents. Try:
- Rebuilding the index with more context
- Checking your CSV data for completeness
- Adjusting similarity thresholds in the code

## Future Enhancements

- Support for different LLM models
- Better prompt engineering
- Semantic caching for faster responses
- Support for additional file formats (PDF, Excel, etc.)
- Web UI for easier interaction

## License

MIT - feel free to use this however you like

## Contributing

Found a bug? Have ideas? Open an issue or submit a PR!

---

**Note**: This is a POC (Proof of Concept). In production, you'd want to add authentication, error handling, monitoring, and scale the vector store appropriately for larger datasets.
