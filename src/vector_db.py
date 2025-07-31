from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")


CHROMA_PATH="gardens_chroma"


# Prepare the DB.
embedding_function = OpenAIEmbeddings()
vector_db = Chroma(
    persist_directory=CHROMA_PATH, embedding_function=embedding_function
)