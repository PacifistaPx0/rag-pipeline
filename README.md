# RAG Pipeline

A **Retrieval-Augmented Generation (RAG) pipeline** for querying markdown documents using OpenAI embeddings and ChromaDB vector storage. Features both command-line and web interfaces for document-based question answering.

## Features

- **Document Processing**: Automated chunking and embedding of markdown files
- **Vector Storage**: ChromaDB database for fast similarity search
- **Web Interface**: Upload documents and ask questions through your browser
- **Command Line**: Direct terminal access for automation
- **Cost Monitoring**: Built-in token and API cost estimation tools

## Quick Start

### 1. Installation

```bash
# Clone and setup
git clone <repository-url>
cd rag-pipeline
uv sync

# Configure environment
cp .env.example .env
# Add your OpenAI API key to .env
```

### 2. Web Interface (Recommended)

```bash
# Start the web server
python main.py

# Open in browser
http://localhost:8000
```

**Using the Web Interface:**
1. Upload a markdown file (max 2MB)
2. Click "Process File" to create embeddings
3. Ask questions about your document
4. View answers with source attribution

### 3. Command Line Interface

```bash
# Create database from documents
python src/create_database.py

# Query documents
python src/query_data.py "Your question here"

# Interactive mode
python project-scripts/optimized_rag.py
```

## Project Structure

```
rag-pipeline/
├── main.py                    # Web interface server
├── frontend/                  # Web UI files
│   ├── index.html            # Upload and query interface
│   └── script.js             # Frontend functionality
├── src/                      # Core pipeline modules
│   ├── create_database.py    # Vector database creation
│   ├── query_data.py         # Command-line query interface
│   └── vector_db.py          # Database utilities
├── data/                     # Example documents
│   ├── books/                # Gardens of the Moon
│   └── books2/               # Alice in Wonderland
├── project-scripts/          # Analysis and monitoring tools
│   ├── cost_monitoring.py    # Database creation cost estimation
│   ├── query_cost_estimation.py  # Query operation cost analysis
│   └── optimized_rag.py      # Performance-optimized query loop
├── chroma/                   # ChromaDB storage (generated)
└── .env                     # Environment configuration
```

## Requirements

- **Python 3.12+**
- **OpenAI API Key** for embeddings and LLM
- **Dependencies**: FastAPI, LangChain, ChromaDB, OpenAI

## Configuration

Edit `.env` file:
```bash
OPENAI_API_KEY=sk-your-key-here
```

## Cost Information

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

## Development

### Adding New Documents

1. Place markdown files in `data` directory
2. Update `DATA_PATH` in `.env` if needed
3. Run `python src/create_database.py`
4. Test with `python src/query_data.py "test query"`

## License

This project is for educational purposes. Source documents may have their own licenses (e.g., Project Gutenberg for Alice in Wonderland).
