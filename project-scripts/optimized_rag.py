# optimized_rag.py

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
import time

import os
import openai
from dotenv import load_dotenv

# load environment variables from .env file
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

PROMPT_TEMPLATE = """
Answer the question based on the following context, try to elaborate some more:

{context}

---

Answer the question: {question}
"""

start = time.time()

# === 1. Load persisted Chroma once (NO reloading per query) ===
PERSIST_DIR = "chroma"
embedding_model = OpenAIEmbeddings()

print("[INFO] Loading Chroma vector store...")
vectorstore = Chroma(persist_directory=PERSIST_DIR, embedding_function=embedding_model)

# === 2. Configure retriever with MMR and top-k ===
retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": 3, "score_threshold": 0.8})

# === 3. Create streaming or non-streaming LLM ===
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)


# set up prompt template
custom_prompt_template = PromptTemplate(
    template=PROMPT_TEMPLATE,
    input_variables=["context", "question"]
)

def format_documents(docs):
    return "\n\n---\n\n".join(doc.page_content for doc in docs)

# === 5. Run RAG Loop ===
print("\n=== Ready for questions. Type 'exit' to quit ===\n")

# while True:
query = "who is hatter?" # input("🧠 Ask: ").strip()
# if query.lower() == "exit":
#     break



try:
    # retrieve relevnt documents
    source_documents = retriever.invoke(query)

    if not source_documents:
        print("unable to find matching results.")
        # continue

    # format context from retrieved documents
    context = format_documents(source_documents)

    # create prompt using template
    prompt = custom_prompt_template.format(context=context, question=query)

    # invoke llm 
    response = llm.invoke(prompt)

    end = time.time()
    
    # extract answer from response
    answer = response.content if hasattr(response, 'content') else str(response)

    print("\n💬 Answer:")
    print(answer)

    print("\n📄 Sources:")
    for i, doc in enumerate(source_documents, 1):
        print(f"{i} - {doc.metadata.get('source', 'unknown')}")

    print(f"\n⏱️ Total response time: {round(end - start, 2)}s\n")

except Exception as e:
    print(f"Error processing query: {e}")
    # continue
