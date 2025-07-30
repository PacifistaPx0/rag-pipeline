from langchain_openai import OpenAIEmbeddings
from langchain.evaluation import load_evaluator
from dotenv import load_dotenv
import openai
import os

# load environment variables from .env file
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")


def main():
    # Get embedding for a word
    embedding_function = OpenAIEmbeddings()
    vector = embedding_function.embed_query("apple")
    print(f"Vector for 'apple': {vector[:5]}...")
    print(f"Vector length: {len(vector)}")

    # compare vector of two words
    evaluator = load_evaluator("pairwise_embedding_distance")
    words = ("apple", "iphone")
    x = evaluator.evaluate_string_pairs(
        prediction=words[0], 
        prediction_b=words[1]
    )
    
    print(f"Comparing ({words[0]}, {words[1]}): {x}")



if __name__ == "__main__":
    main()


"""
Calculating manually with eucladian distance and cosine similarity




import numpy as np
from scipy.spatial.distance import cosine

# load environment variables from .env file
load_dotenv()

def main():
    # Get embedding for a word
    embedding_function = OpenAIEmbeddings()
    
    # Get embeddings for both words
    apple_vector = embedding_function.embed_query("apple")
    iphone_vector = embedding_function.embed_query("iphone")
    
    print(f"Vector for 'apple': {apple_vector[:5]}... (length: {len(apple_vector)})")
    print(f"Vector for 'iphone': {iphone_vector[:5]}... (length: {len(iphone_vector)})")
    
    # Calculate cosine similarity (1 = identical, 0 = orthogonal, -1 = opposite)
    cosine_similarity = 1 - cosine(apple_vector, iphone_vector)
    print(f"Cosine similarity between 'apple' and 'iphone': {cosine_similarity:.4f}")
    
    # Calculate Euclidean distance
    euclidean_distance = np.linalg.norm(np.array(apple_vector) - np.array(iphone_vector))
    print(f"Euclidean distance between 'apple' and 'iphone': {euclidean_distance:.4f}")

"""