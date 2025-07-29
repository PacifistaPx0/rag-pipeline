# RAG Pipeline Copilot Instructions

## Project Overview
This is a **Retrieval-Augmented Generation (RAG) pipeline** designed to provide intelligent feedback on markdown documents, specifically books. The system processes markdown content, creates vector embeddings, and enables conversational queries about the content.

## Architecture Components

### Core Files
- `main.py` - Entry point for the RAG pipeline application
- `create_database.py` - Vector database creation and document ingestion
- `data/input.md` - Source documents (currently contains "Gardens of the Moon" book)
- `.env` - Environment configuration for API keys and database settings

### Key Dependencies (Update Carefully)
```python
# Core RAG stack - these versions work together
python-dotenv==1.0.1     # Environment variables
langchain==0.2.2         # RAG framework
langchain-community==0.2.3  # Community integrations
langchain-openai==0.1.8  # OpenAI embeddings/LLM
unstructured==0.14.4     # Document parsing
chromadb==0.5.0          # Vector database
openai==1.31.1           # OpenAI API client
tiktoken==0.7.0          # Token counting for embeddings
```

## Development Workflow

### Environment Setup
```bash
# Python 3.12 required (see .python-version)
uv sync                  # Install dependencies with uv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install markdown parsing dependencies
pip install "unstructured[md]"

# Windows users: Install Visual C++ Build Tools before chromadb
```

### Key Environment Variables
- `OPENAI_API_KEY` - Required for embeddings and LLM
- `CHROMA_PERSIST_DIRECTORY` - Vector database storage location
- `CHROMA_COLLECTION_NAME` - Collection name for document chunks
- `CHUNK_SIZE` / `CHUNK_OVERLAP` - Text processing parameters

## Project Patterns

### Document Processing Flow
1. **Ingest**: Load markdown documents from `data/` directory
2. **Chunk**: Split documents using configurable chunk size/overlap
3. **Embed**: Create OpenAI embeddings for text chunks
4. **Store**: Persist vectors in ChromaDB with metadata
5. **Query**: Retrieve relevant chunks for user questions

### Vector Database Strategy
- Uses ChromaDB for local vector storage (see `chroma_*` in .gitignore)
- Persistent storage in `CHROMA_PERSIST_DIRECTORY`
- Metadata includes source file, chunk position, and content type

### Error Handling Considerations
- **ONNX Runtime**: ChromaDB dependency - use `conda install onnxruntime -c conda-forge` on macOS
- **Windows Build Tools**: Required for ChromaDB compilation
- **API Rate Limits**: Implement retry logic for OpenAI API calls

## Development Guidelines

### When Adding Dependencies
- **Test compatibility**: Newer LangChain versions may break the 0.2.x API
- **Pin versions**: This stack is sensitive to version mismatches
- **Check ChromaDB**: Often the most problematic dependency for builds

### Code Organization
- Keep document loaders in `create_database.py`
- Main query logic should go in `main.py`
- Use environment variables for all external service configuration
- Store processed documents in `data/` with clear naming

### Testing Large Documents
- The current `input.md` is 28k+ lines (full book)
- Chunk processing may be memory-intensive
- Consider batch processing for multiple documents

## Common Tasks

### Adding New Documents
1. Place markdown files in `data/` directory
2. Run `create_database.py` to process and embed
3. Test queries against new content in `main.py`

### Updating Dependencies
- **Caution**: Year-old requirements may have breaking changes
- Test incremental updates: LangChain 0.2.x → 0.3.x first
- Always test document loading pipeline after updates
- ChromaDB and ONNX runtime are most likely to cause build issues

### Debugging Vector Search
- Check ChromaDB collection contents and metadata
- Verify embedding dimensions match between ingestion/query
- Monitor token usage with tiktoken for cost optimization
