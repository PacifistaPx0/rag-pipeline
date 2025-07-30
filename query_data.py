import argparse

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

import os
import openai
from dotenv import load_dotenv

# load environment variables from .env file
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")


CHROMA_PATH = "gardens_chroma"

PROMPT_TEMPLATE = """
Answer the question based on the following context:

{context}

---

Answer the question: {question}
"""


def main():
    # Create CLI
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query text.")
    args = parser.parse_args()
    query_text = args.query_text

    # Prepare the DB.
    embedding_function = OpenAIEmbeddings()
    db = Chroma(
        persist_directory=CHROMA_PATH, embedding_function=embedding_function
    )

    # Search the DB.
    results = db.similarity_search_with_relevance_scores(query_text, k=3)
    if len(results) == 0 or results[0][1] < 0.7:
        print(f"Unable to find matching results.")
        return
    
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format_prompt(context=context_text, question=query_text)

    model = ChatOpenAI()
    response_text = model.invoke(prompt)

    sources = [doc.metadata.get("source", None) for doc, _score in results]
    
    # Format the output properly
    print("Response:")
    print("-" * 50)
    print(response_text.content)
    print("\nSources:")
    print("-" * 50)
    print(f"{sources}")


if __name__ == "__main__":
    main()
