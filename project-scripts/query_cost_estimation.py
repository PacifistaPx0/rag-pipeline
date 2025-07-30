"""
Estimate the cost of query_data.py operations.
Following project cost monitoring patterns from cost_monitoring.py.
"""
import tiktoken
from dotenv import load_dotenv

load_dotenv()

def estimate_query_tokens(query_text: str, context_chunks: int = 3, 
                         chunk_size: int = 1000, encoding_name: str = "cl100k_base") -> dict:
    """Estimate token usage for a query operation."""
    try:
        encoding = tiktoken.get_encoding(encoding_name)
        
        # Input tokens: query + context + prompt template
        query_tokens = len(encoding.encode(query_text))
        
        # Context tokens (3 chunks of ~1000 tokens each by default)
        context_tokens = context_chunks * chunk_size
        
        # Prompt template tokens (static overhead)
        prompt_template = """
        Answer the question based on the following context:
        {context}
        ---
        Answer the question: {question}
        """
        template_tokens = len(encoding.encode(prompt_template))
        
        # Total input tokens
        input_tokens = query_tokens + context_tokens + template_tokens
        
        # Estimated output tokens (typical response length)
        output_tokens = 150  # Conservative estimate based on query complexity
        
        return {
            "query_tokens": query_tokens,
            "context_tokens": context_tokens,
            "template_tokens": template_tokens,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens
        }
        
    except Exception as e:
        print(f"Error estimating tokens: {e}")
        return {}

def calculate_query_cost(token_breakdown: dict, model: str = "gpt-3.5-turbo") -> dict:
    """Calculate costs for query operation."""
    # OpenAI pricing (per 1K tokens)
    pricing = {
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03}
    }
    
    if model not in pricing:
        model = "gpt-3.5-turbo"  # Default fallback
    
    rates = pricing[model]
    
    # Calculate costs
    input_cost = (token_breakdown["input_tokens"] / 1000) * rates["input"]
    output_cost = (token_breakdown["output_tokens"] / 1000) * rates["output"]
    total_cost = input_cost + output_cost
    
    return {
        "model": model,
        "input_cost": input_cost,
        "output_cost": output_cost,
        "total_cost": total_cost
    }

def estimate_embedding_query_cost(query_text: str) -> float:
    """Estimate cost for embedding the query text."""
    try:
        encoding = tiktoken.get_encoding("cl100k_base")
        query_tokens = len(encoding.encode(query_text))
        
        # text-embedding-3-small pricing
        embedding_cost_per_1k = 0.00002
        return (query_tokens / 1000) * embedding_cost_per_1k
        
    except Exception as e:
        print(f"Error estimating embedding cost: {e}")
        return 0.0

def analyze_query_cost(query_text: str, model: str = "gpt-3.5-turbo"):
    """Complete cost analysis for a query operation."""
    print("=== Query Cost Estimation ===\n")
    print(f"Query: '{query_text}'")
    print(f"Model: {model}")
    print("-" * 40)
    
    # Token breakdown
    tokens = estimate_query_tokens(query_text)
    if not tokens:
        print("Failed to estimate tokens")
        return
    
    print(f"Token Breakdown:")
    print(f"  Query tokens: {tokens['query_tokens']:,}")
    print(f"  Context tokens: {tokens['context_tokens']:,}")
    print(f"  Template tokens: {tokens['template_tokens']:,}")
    print(f"  Input tokens: {tokens['input_tokens']:,}")
    print(f"  Output tokens: {tokens['output_tokens']:,}")
    print(f"  Total tokens: {tokens['total_tokens']:,}")
    
    # LLM costs
    llm_costs = calculate_query_cost(tokens, model)
    print(f"\nLLM Costs:")
    print(f"  Input cost: ${llm_costs['input_cost']:.6f}")
    print(f"  Output cost: ${llm_costs['output_cost']:.6f}")
    print(f"  LLM total: ${llm_costs['total_cost']:.6f}")
    
    # Embedding costs
    embedding_cost = estimate_embedding_query_cost(query_text)
    print(f"\nEmbedding Costs:")
    print(f"  Query embedding: ${embedding_cost:.6f}")
    
    # Total operation cost
    total_cost = llm_costs['total_cost'] + embedding_cost
    print(f"\nTotal Query Cost: ${total_cost:.6f}")
    
    # Cost context following project patterns
    print(f"\n=== Cost Context ===")
    if total_cost < 0.001:
        print("Very low cost - safe to proceed")
    elif total_cost < 0.01:
        print("Low cost - proceed with confidence")
    elif total_cost < 0.10:
        print("Moderate cost - review before proceeding")
    else:
        print("High cost - consider shorter queries")
    
    # Usage projections
    print(f"\n=== Usage Projections ===")
    queries_per_dollar = 1.0 / total_cost if total_cost > 0 else float('inf')
    print(f"Queries per $1: {queries_per_dollar:.0f}")
    print(f"Cost per 100 queries: ${total_cost * 100:.4f}")
    print(f"Cost per 1000 queries: ${total_cost * 1000:.2f}")

def main():
    """Main function with example queries."""
    # Example queries of different complexities
    example_queries = [
        "Who is Alice?",
        "How does Alice meet the Mad Hatter?",
        "Describe the tea party scene and explain what happens between Alice and the characters there."
    ]
    
    for i, query in enumerate(example_queries, 1):
        print(f"\n{'='*50}")
        print(f"EXAMPLE {i}")
        print('='*50)
        analyze_query_cost(query)

if __name__ == "__main__":
    main()