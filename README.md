# Smart Memory + Chat System

A production-grade AI system where memory is the core intelligence. It automatically decides whether to SAVE, SKIP, or MERGE user inputs into structured memory using a hybrid RAG approach (Vector + Graph).

## 🚀 Features
- **Memory Decision Engine**: Automatically classifies inputs into `saved`, `skipped`, or `merged`.
- **Hybrid RAG**: Combines vector-based retrieval (ChromaDB) and graph-based relationships (SQLite).
- **Entity & Relation Extraction**: Automatically builds a knowledge graph from your conversations.
- **Memory Merging**: Semantically similar memories are merged to prevent redundancy.
- **Memory-Aware Chat**: Response generation uses retrieved memories for personalization.

## 🛠️ Tech Stack
- **Backend**: FastAPI, SQLAlchemy, SQLite, ChromaDB, OpenAI API.
- **Frontend**: Streamlit, Pyvis (Graph Visualization).
- **LLM**: GPT-4o, text-embedding-3-small.

## 📁 Project Structure
```
smart-memory-system/
├── backend/
│   ├── main.py            # FastAPI endpoints
│   ├── models.py          # SQLAlchemy models
│   ├── schemas.py         # Pydantic schemas
│   ├── database.py       # DB connection
│   ├── vector_store.py    # ChromaDB integration
│   ├── llm_service.py     # OpenAI integration
│   └── memory_service.py  # Core memory logic
├── frontend/
│   ├── main.py            # Streamlit main app
│   └── pages/             # Chat, Vault, Graph pages
├── requirements.txt
└── .env                   # Environment variables
```

## ⚙️ Setup Instructions

1. **Clone the repository** (or use the provided files).
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Set up Environment Variables**:
   Create a `.env` file in the root directory (use `.env.example` as a template):
   ```env
   OPENAI_API_KEY=your_openai_api_key
   DATABASE_URL=sqlite:///./data/memories.db
   CHROMA_DB_PATH=./data/chroma_db
   MODEL_NAME=gpt-4o
   EMBEDDING_MODEL=text-embedding-3-small
   ```
4. **Create the data directory**:
   ```bash
   mkdir data
   ```
5. **Run the Backend**:
   ```bash
   python -m backend.main
   ```
6. **Run the Frontend**:
   ```bash
   streamlit run frontend/main.py
   ```

## 🧪 Test Cases
- **Save**: "I am a software engineer" → `saved`
- **Skip**: "Translate hello to Spanish" → `skipped`
- **Merge**: "I am a developer" (after saving engineer) → `merged`
- **Graph**: "I work at TCS in Delhi" → Extracted entities: User, TCS, Delhi. Relationships: User → WORKS_AT → TCS, User → LIVES_IN → Delhi.
