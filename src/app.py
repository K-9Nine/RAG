from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import openai
from .config import settings
import json
from datetime import datetime
import os
from .utils.document_processor import DocumentProcessor
from .utils.context_manager import ContextManager
from typing import List, Dict, Optional
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

# Initialize the client
openai.api_key = settings.OPENAI_API_KEY

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBasic()

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = "testuser"
    correct_password = "testpass123"
    is_correct_username = secrets.compare_digest(credentials.username.encode("utf8"), correct_username.encode("utf8"))
    is_correct_password = secrets.compare_digest(credentials.password.encode("utf8"), correct_password.encode("utf8"))
    
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

class ChatMessage(BaseModel):
    message: str
    user_id: str
    chat_history: list = []

SYSTEM_PROMPT = """You are an IT Support Assistant. Your role is to:
1. Help users troubleshoot technical issues
2. Provide clear, step-by-step solutions
3. If you're not completely sure about an answer, say so and recommend escalating to human support
4. Keep responses concise and focused

Knowledge base context will be provided in subsequent messages if relevant."""

# Near the top after loading environment variables
print(f"API Key loaded: {'YES' if openai.api_key else 'NO'}")

# Mount static files AFTER defining API routes
@app.get("/")
async def root(username: str = Depends(verify_credentials)):
    return FileResponse('static/index.html')

@app.get("/api/test")
async def test():
    return {"message": "API is working"}

# Initialize document processor and context manager
doc_processor = DocumentProcessor(collection_name=settings.COLLECTION_NAME)
context_manager = ContextManager(doc_processor)

@app.post("/api/chat")
async def chat(chat_message: ChatMessage, username: str = Depends(verify_credentials)):
    try:
        print("\n=== Starting new chat request ===")
        print(f"User message: {chat_message.message}")
        
        # Get enhanced prompt with context
        try:
            enhanced_prompt = context_manager.enhance_prompt(
                chat_message.message, 
                SYSTEM_PROMPT
            )
            print(f"Enhanced prompt: {enhanced_prompt}")
        except Exception as context_error:
            print(f"Error getting context: {str(context_error)}")
            raise HTTPException(status_code=500, detail=f"Context error: {str(context_error)}")
        
        messages = [{"role": "system", "content": enhanced_prompt}]
        for hist in chat_message.chat_history[-5:]:
            messages.append({"role": hist["role"], "content": hist["content"]})
        messages.append({"role": "user", "content": chat_message.message})
        
        print("Messages to send:", messages)
        
        try:
            response = openai.ChatCompletion.create(
                model=settings.MODEL_NAME,
                messages=messages,
                temperature=settings.TEMPERATURE,
                max_tokens=settings.MAX_TOKENS
            )
            
            ai_response = response.choices[0].message.content
            print("Got OpenAI response:", ai_response)
            
            if not ai_response:
                raise ValueError("Empty response from OpenAI")
            
            # Log the chat
            log_chat(chat_message.user_id, chat_message.message, ai_response)
            
            return {"response": ai_response}
            
        except Exception as api_error:
            print(f"OpenAI API error details: {type(api_error).__name__}: {str(api_error)}")
            raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(api_error)}")
            
    except Exception as e:
        print(f"General error in chat endpoint: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def log_chat(user_id: str, question: str, answer: str):
    """Enhanced logging with JSON format and timestamps"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id,
        "question": question,
        "answer": answer
    }
    
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    # Log to JSON file
    log_file = f"logs/chat_logs_{datetime.now().strftime('%Y%m')}.json"
    try:
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        print(f"Logging error: {str(e)}")

# Mount static files for other static content (CSS, JS, etc)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/api/test-openai")
async def test_openai():
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say hello"}],
            max_tokens=10
        )
        return {"status": "success", "response": response.choices[0].message.content}
    except Exception as e:
        return {"status": "error", "message": str(e)}

class Document(BaseModel):
    content: str
    metadata: str

@app.post("/api/load-documents")
async def load_documents(documents: List[Document]):
    try:
        doc_list = [{"content": doc.content, "metadata": doc.metadata} for doc in documents]
        doc_processor.add_documents(doc_list)
        return {"status": "success", "message": f"Added {len(documents)} documents"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Check Weaviate connection
        doc_processor.client.schema.get()
        # Check OpenAI connection
        openai.models.list()
        return {"status": "healthy", "message": "All services operational"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")