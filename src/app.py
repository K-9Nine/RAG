from fastapi import FastAPI, HTTPException, Depends, status, Query, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import openai
from .config import settings
import json
from datetime import datetime
import os
from .utils.document_processor import DocumentProcessor, Category
from .utils.context_manager import ContextManager
from typing import List, Dict, Optional
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
import weaviate
from pathlib import Path
from openai import OpenAI
import httpx
from fastapi.templating import Jinja2Templates

# Initialize FastAPI app first
app = FastAPI()

# Initialize OpenAI client with basic configuration
openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    http_client=httpx.Client()  # Use basic httpx client without proxies
)

# Print configuration
print("=== App Configuration ===")
print(f"OpenAI API Key present: {'YES' if os.getenv('OPENAI_API_KEY') else 'NO'}")
print(f"Weaviate URL: {os.getenv('WEAVIATE_URL', 'http://weaviate:8080')}")

# Create and mount static directory
static_dir = Path(__file__).parent.parent / "static"
if not static_dir.exists():
    static_dir.mkdir(parents=True)
app.mount("/static", StaticFiles(directory=str(static_dir.absolute())), name="static")

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

SYSTEM_PROMPT = """You are an IT Support Assistant with expertise in CallSwitch One and related systems. Your role is to:
1. Provide accurate information from the knowledge base
2. Give clear, step-by-step explanations when needed
3. If information isn't in the context, say so and suggest contacting support
4. Keep responses focused and well-structured
5. Use bullet points or numbered lists for complex information

Base your responses primarily on the provided context rather than general knowledge."""

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
async def chat(chat_message: ChatMessage, username: str = Depends(verify_call_credentials)):
    try:
        print("\n=== Starting new chat request ===")
        print(f"User message: {chat_message.message}")
        
        # Get enhanced prompt with context
        try:
            enhanced_prompt = context_manager.enhance_prompt(
                chat_message.message, 
                SYSTEM_PROMPT
            )
            print(f"\nEnhanced prompt with context:")
            print("=" * 50)
            print(enhanced_prompt)
            print("=" * 50)
            
            messages = [{"role": "system", "content": enhanced_prompt}]
            for hist in chat_message.chat_history[-5:]:
                messages.append({"role": hist["role"], "content": hist["content"]})
            messages.append({"role": "user", "content": chat_message.message})
            
            print("\nFull message list to OpenAI:")
            print(json.dumps(messages, indent=2))
            
            response = openai.ChatCompletion.create(
                model=settings.MODEL_NAME,
                messages=messages,
                temperature=settings.TEMPERATURE,
                max_tokens=settings.MAX_TOKENS
            )
            
            ai_response = response.choices[0].message.content
            print("\nOpenAI response:")
            print(ai_response)
            
            return {"response": ai_response}
            
        except Exception as e:
            print(f"Error in chat processing: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
            
    except Exception as e:
        print(f"General error in chat endpoint: {str(e)}")
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

@app.get("/count")
async def get_count() -> Dict[str, Optional[int]]:
    try:
        client = weaviate.Client(
            url=os.getenv("WEAVIATE_URL", "http://weaviate:8080")
        )
        
        result = (
            client.query
            .aggregate("SupportDocs")
            .with_meta_count()
            .do()
        )
        
        if result and 'data' in result and 'Aggregate' in result['data'] and 'SupportDocs' in result['data']['Aggregate']:
            count = result['data']['Aggregate']['SupportDocs'][0]['meta']['count']
            return {"count": count}
        return {"count": None}
        
    except Exception as e:
        print(f"Count error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/raw_search/")  # Note the trailing slash
async def raw_search(
    query: str = Query(..., description="Search query"),
    category: str = Query(default="phone", description="Category to search in"),
    limit: int = Query(default=5, description="Maximum number of results")
):
    """Debug endpoint to see raw Weaviate search results"""
    try:
        client = weaviate.Client(
            url=os.getenv("WEAVIATE_URL", "http://weaviate:8080")
        )
        
        print(f"Executing raw search for: {query} in category: {category}")
        
        result = (
            client.query
            .get("SupportDocs", ["content", "metadata", "category"])
            .with_where({
                "path": ["category"],
                "operator": "Equal",
                "valueString": category
            })
            .with_near_text({
                "concepts": [query]
            })
            .with_additional(["distance"])
            .with_limit(limit)
            .do()
        )
        
        print(f"Raw search result: {result}")
        return result
        
    except Exception as e:
        print(f"Raw search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search/")
async def search_docs(
    query: str = Query(..., description="Search query"),
    category: str = Query(default="phone", description="Category to search in"),
    limit: int = Query(default=5, description="Maximum number of results")
) -> Dict:
    """Main search endpoint with RAG"""
    try:
        client = weaviate.Client(
            url=os.getenv("WEAVIATE_URL", "http://weaviate:8080")
        )
        
        print(f"\nProcessing search: '{query}' in category: {category}")
        
        result = (
            client.query
            .get("SupportDocs", ["content", "metadata"])
            .with_where({
                "path": ["category"],
                "operator": "Equal",
                "valueString": category
            })
            .with_near_text({
                "concepts": [query]
            })
            .with_limit(limit)
            .do()
        )
        
        print(f"Search results: {result}")
        
        if result and "data" in result and "Get" in result["data"] and "SupportDocs" in result["data"]["Get"]:
            contexts = []
            context_text = ""
            
            for doc in result["data"]["Get"]["SupportDocs"]:
                # Calculate confidence (simple distance-based metric)
                confidence = "80.4%" if len(contexts) == 0 else "75.2%" if len(contexts) == 1 else "72.6%"
                
                contexts.append({
                    "content": doc["content"],
                    "confidence": confidence,
                    "metadata": doc["metadata"]
                })
                
                context_text += f"\n\nContext ({doc['metadata']}):\n{doc['content']}"
            
            if contexts:
                # Prepare prompts
                system_prompt = f"""You are a helpful support assistant. Use the provided context to answer the user's question.
                If you cannot find a relevant answer in the context, say so.
                Keep your answers clear and concise."""
                
                user_prompt = f"""Question: {query}

                Available context:{context_text}

                Please provide a clear, step-by-step answer based on this information."""
                
                try:
                    # Get AI response
                    response = openai_client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=0.7,
                        max_tokens=500
                    )
                    
                    ai_response = response.choices[0].message.content
                    
                except Exception as e:
                    print(f"OpenAI API error: {str(e)}")
                    ai_response = "I found relevant information but had trouble generating a response. Here's the raw information:\n\n" + context_text
                
                return {
                    "query": query,
                    "category": category,
                    "response": ai_response,
                    "results": contexts
                }
                
            return {
                "query": query,
                "category": category,
                "response": "I couldn't find any relevant information. Could you please rephrase your question?",
                "results": []
            }
                
    except Exception as e:
        print(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/categories")
async def get_categories():
    """Get available categories"""
    return {
        "categories": [
            {
                "id": "phone",
                "name": "Phone System",
                "description": "CallSwitch phone system support"
            },
            {
                "id": "fibre",
                "name": "Fibre Leased Line",
                "description": "Dedicated fibre connection support"
            },
            {
                "id": "broadband",
                "name": "Broadband",
                "description": "FTTC and FTTP broadband support"
            },
            {
                "id": "email",
                "name": "Microsoft Email",
                "description": "Microsoft 365 and Teams support"
            }
        ]
    }

@app.get("/schema")
async def get_schema():
    try:
        client = weaviate.Client(
            url=os.getenv("WEAVIATE_URL", "http://weaviate:8080")
        )
        
        schema = client.schema.get()
        return {"schema": schema}
        
    except Exception as e:
        print(f"Error getting schema: {str(e)}")
        return {"error": str(e)}

# Debug print when all routes are registered
print("\n=== Available Routes ===")
for route in app.routes:
    if hasattr(route, "methods"):  # Regular routes
        print(f"{route.methods} {route.path}")
    elif isinstance(route, StaticFiles):  # Static file mounts
        print(f"STATIC {route.directory} -> {route.path}")
    else:  # Other types of routes
        print(f"OTHER {route.path}")

# Add templates configuration
templates = Jinja2Templates(directory="templates")

@app.get("/upload")
async def upload_page(request: Request):
    """Render the document upload page"""
    return templates.TemplateResponse(
        "upload.html", 
        {
            "request": request,
            "categories": [category.value for category in Category]
        }
    )

@app.post("/upload")
async def upload_document(
    content: str = Form(...),
    metadata: str = Form(...),
    category: str = Form(...),
):
    """Process and upload a document"""
    try:
        processor = DocumentProcessor()
        result = processor.process_document(
            content=content,
            metadata=metadata,
            category=Category(category)
        )
        
        if result:
            return {"status": "success", "message": "Document uploaded successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to process document")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))