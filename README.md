# Company RAG Pipeline (Ollama + ChromaDB)

A local, privacy-friendly Retrieval-Augmented Generation (RAG) system for answering questions about company documents (HR policies, payroll, IT security, benefits, onboarding, etc.). Everything runs locally using **Ollama** for embeddings/LLM and **ChromaDB** as the vector store — no external API keys required.

## Features

- 📄 Ingests `.txt` company documents and splits them into overlapping chunks
- 🧠 Generates embeddings locally using `nomic-embed-text` via Ollama
- 🗄️ Stores embeddings in a persistent ChromaDB collection (cosine similarity)
- 🔍 Retrieves relevant chunks using similarity search with a score threshold
- 💬 Generates grounded answers using `llama3.2` via Ollama
- 🔁 Supports multi-turn conversations with history-aware query rewriting

## Project Structure

```
.
├── docs/                       # Your company .txt documents go here
├── db/
│   └── chroma_db/              # Persisted vector store (auto-created)
├── ingestion_pipeline.py        # Load, chunk, embed, and store documents
├── retriveal_pipeline.py        # Test retrieval against the vector store
├── answer_generation.py         # Single-turn RAG question answering
├── history_aware_generation.py  # Multi-turn conversational RAG chatbot
└── README.md
```

## Requirements

- Python 3.9+
- [Ollama](https://ollama.com) installed and running locally
- Pull the required models:
  ```bash
  ollama pull llama3.2
  ollama pull nomic-embed-text
  ```
- Python packages:
  ```bash
  pip install python-dotenv langchain-chroma langchain-core langchain-community langchain-text-splitters langchain-ollama
  ```

## Setup

1. Make sure Ollama is running:
   ```bash
   ollama serve
   ```
2. Create a `docs/` folder in the project root and add your company `.txt` files (HR policies, payroll info, IT security guidelines, benefits docs, onboarding guides, etc.).
3. (Optional) Create a `.env` file for any environment variables your setup requires — it's loaded automatically via `load_dotenv()`.

## Pipeline Overview

```
docs/*.txt
    │
    ▼
Document Loading (DirectoryLoader + TextLoader)
    │
    ▼
Text Chunking (RecursiveCharacterTextSplitter, 1000 chars, 200 overlap)
    │
    ▼
Embedding Generation (OllamaEmbeddings: nomic-embed-text)
    │
    ▼
ChromaDB Vector Store (db/chroma_db, cosine similarity)
    │
    ▼
Retrieval (similarity_score_threshold, k=5, threshold=0.3)
    │
    ▼
Context-Augmented Prompt
    │
    ▼
LLM Generation (ChatOllama: llama3.2)
    │
    ▼
Grounded Answer
```

## Usage

### 1. Ingest Documents — `ingestion_pipeline.py`

Loads all `.txt` files from `docs/`, splits them into chunks, generates embeddings, and persists them to `db/chroma_db`.

```bash
python ingestion_pipeline.py
```

- If `db/chroma_db` already exists, the script skips re-processing and simply loads the existing vector store, printing the number of stored documents.
- If it doesn't exist, it loads documents, prints previews of the first 2 documents and first 5 chunks, then builds and saves the vector store.

### 2. Test Retrieval — `retriveal_pipeline.py`

Runs a sample query against the vector store and prints the retrieved chunks. Useful for verifying that ingestion worked and tuning the retriever.

```bash
python retriveal_pipeline.py
```

- Uses `search_type="similarity_score_threshold"` with `k=5` and `score_threshold=0.3` — only chunks with cosine similarity ≥ 0.3 are returned.
- Includes a bank of 20 synthetic test questions (HR, payroll, IT security, benefits, onboarding) you can swap into the `query` variable to test retrieval across topics.

### 3. Single-Turn Q&A — `answer_generation.py`

Retrieves relevant chunks for a single query and generates one grounded answer with `llama3.2`.

```bash
python answer_generation.py
```

- Prints the retrieved context documents, then the model's generated answer.
- Edit the `query` variable to ask a different question.

### 4. Conversational Chatbot — `history_aware_generation.py`

An interactive CLI chatbot that remembers conversation history and rewrites follow-up questions into standalone, searchable queries before retrieval.

```bash
python history_aware_generation.py
```

```
Ask me questions! Type 'quit' to exit.

Your question: How many days of annual leave do employees get?
...
Answer: ...

Your question: What about for senior employees?
Searching for: How many days of annual leave do senior employees get?
...
```

Type `quit` to exit. Conversation history is kept in memory only and is not persisted between runs.

## Configuration Reference

| Setting | Where | Default |
|---|---|---|
| Documents directory | `ingestion_pipeline.py` → `load_documents()` | `docs` |
| Vector store path | all scripts → `persistent_directory` | `db/chroma_db` |
| Embedding model | `OllamaEmbeddings(model=...)` | `nomic-embed-text` |
| Chat/generation model | `ChatOllama(model=...)` | `llama3.2` |
| Chunk size / overlap | `split_documents()` | `1000` / `200` |
| Retriever type | `retriveal_pipeline.py`, `answer_generation.py` | `similarity_score_threshold` |
| Retrieval k / threshold | same | `5` / `0.3` |
| Conversational retriever k | `history_aware_generation.py` | `3` (plain similarity) |

## Notes & Tips

- **Re-running ingestion**: Delete the `db/chroma_db` folder if you want to rebuild the vector store from scratch (e.g., after updating documents).
- **Score threshold tuning**: If retrieval returns too few or too many results, adjust `score_threshold` in the retriever — lower it to get more (possibly less relevant) results, raise it for stricter matches.
- **Grounded answers only**: All generation prompts instruct the model to answer strictly from retrieved documents and to say so if the answer isn't found, reducing hallucinations.
- **All local**: No data leaves your machine — embeddings and generation both run through your local Ollama instance.

## Future Improvements

- Hybrid search (vector + keyword)
- Re-ranking models
- Citation-based responses
- Multi-document question answering
- Real-time document updates
- Persistent conversational memory
- Web UI (e.g., Streamlit)

## Author

Yogesh Dhananjay Meka
MS in Data Science, University of North Texas
