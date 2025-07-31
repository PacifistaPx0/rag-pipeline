# RAG Pipeline

A **Retrieval-Augmented Generation (RAG) pipeline** for querying markdown documents using OpenAI embeddings and ChromaDB vector storage. Built for learning and experimentation with document-based question answering.

## Overview

This project processes markdown documents (books, articles, etc.) into searchable vector embeddings, enabling natural language queries about the content. Currently configured with "Alice's Adventures in Wonderland" and "Gardens of the Moon" as example datasets.

## Features

- **Document Processing**: Automated chunking and embedding of markdown files
- **Vector Storage**: Persistent ChromaDB database for fast similarity search
- **Query Interface**: Natural language questions with contextual answers
- **Cost Monitoring**: Built-in token and API cost estimation tools
- **Multiple Search Strategies**: Support for similarity search and MMR (Maximal Marginal Relevance)

## Project Structure

```
rag-pipeline/
├── src/                        # Core pipeline modules
│   ├── create_database.py      # Vector database creation
│   ├── query_data.py          # Query interface
│   └── vector_db.py           # Database utilities
├── data/                      # Source documents
│   ├── books/                 # Gardens of the Moon
│   └── books2/               # Alice in Wonderland
├── project-scripts/          # Analysis and monitoring tools
│   ├── cost_monitoring.py    # Database creation cost estimation
│   ├── query_cost_estimation.py  # Query operation cost analysis
│   └── optimized_rag.py      # Performance-optimized query loop
├── chroma/                   # ChromaDB storage (generated)
└── .env                     # Environment configuration
```

## Requirements

- **Python 3.12+** (see `.python-version`)
- **OpenAI API Key** for embeddings and LLM
- **Visual C++ Build Tools** (Windows) for ChromaDB compilation

### Dependencies

```python
python-dotenv==1.0.1     # Environment variables
langchain==0.2.2         # RAG framework
langchain-community==0.2.3  # Community integrations
langchain-openai==0.1.8  # OpenAI embeddings/LLM
unstructured==0.14.4     # Document parsing
chromadb==0.5.0          # Vector database
openai==1.31.1           # OpenAI API client
tiktoken==0.7.0          # Token counting
onnxruntime==1.17.1      # ChromaDB dependency
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd rag-pipeline
   ```

2. **Set up Python environment**
   ```bash
   # Using uv (recommended)
   uv sync
   
   # Or using pip
   pip install -r requirements.txt
   pip install "unstructured[md]"
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key
   ```

4. **Windows users only**
   - Install Microsoft Visual C++ Build Tools
   - Install ONNX Runtime before ChromaDB: `pip install onnxruntime`

## Usage

### 1. Create Vector Database

Process your markdown documents into embeddings:

```bash
# Estimate costs first (optional)
python project-scripts/cost_monitoring.py

# Create the database
python src/create_database.py
```

### 2. Query Documents

Ask questions about your documents:

```bash
# Basic query
python src/query_data.py "Who is Alice?"

# Using different ChromaDB collections
python src/query_data.py "What is the Malazan world?" --chroma-path chroma_gardens
```

### 3. Interactive Query Loop

For continuous querying:

```bash
python project-scripts/optimized_rag.py
```

## Configuration

### Environment Variables (.env)

```bash
# Required
OPENAI_API_KEY=sk-your-key-here

# Optional - Database settings
CHROMA_PERSIST_DIRECTORY=chroma
CHROMA_COLLECTION_NAME=rag_documents

# Optional - Processing parameters
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
DATA_PATH=data/books2
```

### Document Processing

- **Chunk Size**: Default 1000 tokens with 200 token overlap
- **Embedding Model**: text-embedding-3-small (OpenAI)
- **LLM Model**: gpt-3.5-turbo for cost efficiency

## Cost Analysis

### Typical Costs (using gpt-3.5-turbo)

- **Database Creation**: $0.50-2.00 per book (one-time)
- **Simple Query**: ~$0.002-0.003 per query
- **Complex Query**: ~$0.004-0.006 per query
- **Per 1000 queries**: ~$2.00-6.00

### Cost Monitoring Tools

```bash
# Estimate database creation costs
python project-scripts/cost_monitoring.py

# Analyze query operation costs
python project-scripts/query_cost_estimation.py
```

## Performance

### Database Creation
- **Alice in Wonderland**: ~28k lines, ~$0.50, 2-3 minutes
- **Gardens of the Moon**: ~45k lines, ~$1.20, 4-5 minutes

### Query Performance
- **Database Loading**: 2-4 seconds (ChromaDB initialization)
- **Vector Search**: 0.1-0.5 seconds (similarity search)
- **LLM Response**: 3-8 seconds (OpenAI API call)
- **Total**: 5-12 seconds per query

## Troubleshooting

### Common Issues

1. **ChromaDB Installation Fails**
   - Windows: Install Visual C++ Build Tools first
   - macOS: Use `conda install onnxruntime -c conda-forge`

2. **Segmentation Fault**
   - Usually ONNX Runtime compatibility issue
   - Try: `pip install --upgrade onnxruntime`

3. **High API Costs**
   - Reduce chunk size: `CHUNK_SIZE=500`
   - Use fewer chunks: modify `k=2` in similarity search
   - Increase relevance threshold: `score_threshold=0.8`

4. **Slow Query Performance**
   - Use persistent ChromaDB storage (check `CHROMA_PERSIST_DIRECTORY`)
   - Consider using MMR search for better result diversity

## Development

### Adding New Documents

1. Place markdown files in `data` directory
2. Update `DATA_PATH` in `.env` if needed
3. Run `python src/create_database.py`
4. Test with `python src/query_data.py "test query"`

### Dependency Updates

⚠️ **Warning**: This stack is sensitive to version mismatches

- Test LangChain updates incrementally (0.2.x → 0.3.x)
- ChromaDB often causes build issues on updates
- Always test document loading pipeline after updates

## Learning Resources

This project demonstrates:
- **Vector Embeddings**: Converting text to numerical representations
- **Similarity Search**: Finding relevant document chunks
- **Prompt Engineering**: Crafting effective LLM prompts
- **Cost Optimization**: Balancing quality vs API costs
- **Document Processing**: Chunking strategies for large texts

## License

This project is for educational purposes. Source documents may have their own licenses (e.g., Project Gutenberg for Alice in Wonderland).
