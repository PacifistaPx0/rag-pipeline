from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

import openai
import os
import shutil

from dotenv import load_dotenv


# load environment variables from .env file
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

CHROMA_PATH = "chroma"
# Updated to use smaller Alice in Wonderland book for initial testing
DATA_PATH = "data/books2"


def main():
    generate_data_store()

def generate_data_store():
    documents = load_documents()
    chunks = split_text(documents)
    save_to_chroma(chunks)

def load_documents():
    """Load all markdown documents from the configured data path."""
    loader = DirectoryLoader(DATA_PATH, glob="*.md")
    documents = loader.load()
    print(f"Loaded {len(documents)} documents from {DATA_PATH}")
    return documents

def split_text(documents: list[Document]) -> list[Document]:
    """Split documents into chunks for vector embedding."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")

    # Show sample chunk for verification
    if len(chunks) > 10:
        document = chunks[10]
        print(f"\nSample chunk (10th):")
        print(f"Content preview: {document.page_content[:200]}...")
        print(f"Metadata: {document.metadata}")

    return chunks

def save_to_chroma(chunks: list[Document]):
    """Save document chunks to ChromaDB vector store."""
    # Clear out existing database
    if os.path.exists(CHROMA_PATH):
        print(f"Clearing existing database at {CHROMA_PATH}")
        shutil.rmtree(CHROMA_PATH)

    # Create new Chroma vector store
    print("Creating embeddings and saving to ChromaDB...")
    db = Chroma.from_documents(
        chunks, OpenAIEmbeddings(), persist_directory=CHROMA_PATH
    )
    
    db.persist()
    print(f"Saved {len(chunks)} chunks to {CHROMA_PATH}.")




if __name__ == "__main__":
    main()