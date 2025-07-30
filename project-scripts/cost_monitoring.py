"""
Estimate the cost of creating the ChromaDB vector database.
Run this before create_database.py to predict costs.
"""
import os
import tiktoken
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def estimate_file_tokens(file_path: str, encoding_name: str = "cl100k_base") -> int:
    """Estimate token count for a markdown file."""
    try:
        encoding = tiktoken.get_encoding(encoding_name)
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        tokens = len(encoding.encode(content))
        return tokens
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return 0

def estimate_embedding_cost(total_tokens: int, model: str = "text-embedding-3-small") -> float:
    """Calculate OpenAI embedding cost."""
    pricing = {
        "text-embedding-3-small": 0.00002,  # per 1K tokens
        "text-embedding-3-large": 0.00013   # per 1K tokens
    }
    
    cost_per_1k = pricing.get(model, pricing["text-embedding-3-small"])
    return (total_tokens / 1000) * cost_per_1k

def main():
    # Check current DATA_PATH configuration
    data_path = "data/books"  # From create_database.py
    
    print("=== ChromaDB Creation Cost Estimation ===\n")
    
    # Check if data directory exists
    if not os.path.exists(data_path):
        print(f"  Directory '{data_path}' not found!")
        print(" Available data files:")
        if os.path.exists("data"):
            for file in Path("data").glob("*.md"):
                print(f"   - {file}")
        print(f"\n Update DATA_PATH in create_database.py or move files to {data_path}/")
        return
    
    # Process all markdown files
    total_tokens = 0
    file_count = 0
    
    for md_file in Path(data_path).glob("*.md"):
        tokens = estimate_file_tokens(str(md_file))
        total_tokens += tokens
        file_count += 1
        print(f" {md_file.name}: {tokens:,} tokens")
    
    if file_count == 0:
        print(f" No .md files found in {data_path}")
        return
    
    # Calculate chunks and costs
    chunk_size = 1000  # From create_database.py
    chunk_overlap = 200
    estimated_chunks = max(1, total_tokens // (chunk_size - chunk_overlap))
    
    # Embedding cost calculation
    embedding_cost = estimate_embedding_cost(total_tokens)
    
    print(f"\n=== Processing Summary ===")
    print(f" Total files: {file_count}")
    print(f" Total tokens: {total_tokens:,}")
    print(f" Estimated chunks: {estimated_chunks:,}")
    print(f" Embedding cost: ${embedding_cost:.6f}")
    
    # Cost context
    print(f"\n=== Cost Context ===")
    if embedding_cost < 0.001:
        print(" Very low cost - safe to proceed")
    elif embedding_cost < 0.01:
        print(" Low cost - proceed with confidence")
    elif embedding_cost < 0.10:
        print("  Moderate cost - review before proceeding")
    else:
        print("  High cost - consider chunking strategy")
    
    print(f" Cost comparison: ~{embedding_cost/0.005:.1f}x the price of a coffee")

if __name__ == "__main__":
    main()