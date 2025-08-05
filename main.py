from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import tempfile
import os

# Langchain imports
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="RAG Pipeline Web Interface")

# Mount static files from frontend folder
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Pydantic models
class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    success: bool
    answer: str = ""
    sources: list = []
    message: str = ""

class UploadResponse(BaseModel):
    success: bool
    message: str
    filename: str = ""

# Global variable to store the current database
current_db = None
current_filename = None

PROMPT_TEMPLATE = """
Answer the question based on the following context, try to elaborate some more:

{context}

---

Answer the question: {question}
"""

def create_vector_database(file_path: str, db_path: str):
    """Create a vector database from a single markdown file"""
    # Load the document
    loader = TextLoader(file_path, encoding='utf-8')
    documents = loader.load()
    
    # Split the text
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    
    # Create vector store
    embedding_function = OpenAIEmbeddings()
    db = Chroma.from_documents(
        chunks, 
        embedding_function, 
        persist_directory=db_path
    )
    
    return db

def query_rag(query_text: str, db: Chroma):
    """Query the RAG system and return formatted results"""
    # Search the database
    results = db.similarity_search_with_relevance_scores(query_text, k=3)
    
    if len(results) == 0 or results[0][1] < 0.7:
        return {
            "answer": "Unable to find relevant information in the document to answer your question.",
            "sources": []
        }
    
    # Prepare context
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    
    # Create prompt
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    
    # Get response from OpenAI
    model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    response = model.invoke(prompt)
    
    # Format sources
    sources = []
    for doc, score in results:
        sources.append({
            "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
            "score": score,
            "metadata": doc.metadata
        })
    
    return {
        "answer": response.content,
        "sources": sources
    }

@app.get("/")
async def read_root():
    """Serve the main HTML page"""
    return FileResponse("frontend/index.html")

@app.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Handle file upload and create vector database"""
    global current_db, current_filename
    
    try:
        # Validate file type
        if not file.filename.lower().endswith('.md'):
            raise HTTPException(status_code=400, detail="Only Markdown (.md) files are supported")
        
        # Validate file size (2MB limit)
        content = await file.read()
        if len(content) > 2 * 1024 * 1024:  # 2MB
            raise HTTPException(status_code=400, detail="File size must be under 2MB")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.md', delete=False) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Create temporary directory for database
            temp_db_dir = tempfile.mkdtemp()
            
            # Create vector database from the uploaded file
            current_db = create_vector_database(temp_file_path, temp_db_dir)
            current_filename = file.filename
            
            return UploadResponse(
                success=True,
                message="File processed successfully",
                filename=file.filename
            )
            
        except Exception as e:
            # Clean up on error
            if current_db:
                current_db = None
            raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
        
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/query", response_model=QueryResponse)
async def query_document(request: QueryRequest):
    """Handle queries against the uploaded document"""
    global current_db
    
    try:
        if not current_db:
            raise HTTPException(status_code=400, detail="No document uploaded. Please upload a document first.")
        
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Query the RAG system
        result = query_rag(request.query, current_db)
        
        return QueryResponse(
            success=True,
            answer=result["answer"],
            sources=result["sources"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return QueryResponse(
            success=False,
            message=f"Query failed: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
