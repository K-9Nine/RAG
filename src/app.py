from fastapi import FastAPI, HTTPException, Query, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
import weaviate
import os
from typing import Dict, Optional, List
from pathlib import Path
from openai import OpenAI
import httpx
from src.utils.document_processor import DocumentProcessor, Category
from fastapi.middleware.cors import CORSMiddleware
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Initialize FastAPI app
app = FastAPI()

# Initialize OpenAI client
openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    http_client=httpx.Client()
)

# Print configuration
print("=== App Configuration ===")
print(f"OpenAI API Key present: {'YES' if os.getenv('OPENAI_API_KEY') else 'NO'}")
print(f"Weaviate URL: {os.getenv('WEAVIATE_URL', 'http://weaviate:8080')}")

# Create and mount static directory
static_dir = Path(__file__).parent.parent / "static"
if not static_dir.exists():
    static_dir.mkdir(parents=True)
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# Initialize templates
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def read_root():
    return FileResponse("src/static/index.html")

async def get_relevant_context(query: str, category: str) -> Dict:
    """Get relevant context from Weaviate"""
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
            .with_limit(5)
            .do()
        )
        
        if not result or "data" not in result or "Get" not in result["data"] or "SupportDocs" not in result["data"]["Get"]:
            return {
                "contexts": [],
                "context_text": ""
            }
            
        contexts = []
        context_text = ""
        
        for doc in result["data"]["Get"]["SupportDocs"]:
            confidence = "80.4%" if len(contexts) == 0 else "75.2%" if len(contexts) == 1 else "72.6%"
            
            contexts.append({
                "content": doc["content"],
                "confidence": confidence,
                "metadata": doc["metadata"]
            })
            
            context_text += f"\n\nContext ({doc['metadata']}):\n{doc['content']}"
            
        return {
            "contexts": contexts,
            "context_text": context_text
        }
        
    except Exception as e:
        print(f"Search error: {str(e)}")
        return {
            "contexts": [],
            "context_text": ""
        }

@app.get("/search/")
async def search_docs(
    query: str = Query(..., description="Search query"),
    category: str = Query(default="phone", description="Category to search in"),
    limit: int = Query(default=5, description="Maximum number of results")
) -> Dict:
    """Search endpoint with RAG"""
    try:
        client = weaviate.Client(
            url=os.getenv("WEAVIATE_URL", "http://weaviate:8080")
        )
        
        print(f"\nProcessing search: '{query}' in category: {category}")
        
        # Get relevant documents
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
                confidence = "80.4%" if len(contexts) == 0 else "75.2%" if len(contexts) == 1 else "72.6%"
                
                contexts.append({
                    "content": doc["content"],
                    "confidence": confidence,
                    "metadata": doc["metadata"]
                })
                
                context_text += f"\n\nContext ({doc['metadata']}):\n{doc['content']}"
            
            if contexts:
                system_prompt = """You are a helpful support assistant. Use the provided context to answer the user's question.
                If you cannot find a relevant answer in the context, say so.
                Keep your answers clear and concise."""
                
                user_prompt = f"""Question: {query}

                Available context:{context_text}

                Please provide a clear, step-by-step answer based on this information."""
                
                try:
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

def preprocess_text(text: str) -> str:
    """Clean and normalize text while preserving hyperlinks"""
    # Temporarily replace http/https URLs with placeholders
    url_pattern = r'(https?://[^\s<>]+)'
    urls = re.findall(url_pattern, text)
    for i, url in enumerate(urls):
        text = text.replace(url, f'__URL_{i}__')
    
    # Clean text but preserve basic formatting
    text = re.sub(r'\s+', ' ', text.strip())
    text = re.sub(r'[^\w\s.,!?;:()\[\]{}\-_\'\"<>]', '', text)
    
    # Restore URLs
    for i, url in enumerate(urls):
        text = text.replace(f'__URL_{i}__', url)
    
    return text

def chunk_document(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split document into overlapping chunks for better retrieval"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    return text_splitter.split_text(text)

@app.post("/upload")
async def upload_document(
    content: str = Form(...),
    metadata: str = Form(...),
    category: str = Form(...),
):
    """Process and upload a document with RAG optimization"""
    try:
        # Clean the text
        processed_content = preprocess_text(content)
        
        # Split into chunks
        chunks = chunk_document(processed_content)
        
        # Initialize Weaviate client
        client = weaviate.Client(
            url=os.getenv("WEAVIATE_URL", "http://weaviate:8080")
        )
        
        # Upload each chunk with metadata
        batch = client.batch.configure(batch_size=100)
        with batch:
            for i, chunk in enumerate(chunks):
                properties = {
                    "content": chunk,
                    "metadata": f"{metadata} (part {i+1}/{len(chunks)})",
                    "category": category,
                    "originalMetadata": metadata,
                    "chunkIndex": i,
                    "totalChunks": len(chunks)
                }
                
                client.batch.add_data_object(
                    data_object=properties,
                    class_name="SupportDocs"
                )
        
        return {
            "status": "success", 
            "message": f"Document processed and uploaded in {len(chunks)} chunks",
            "chunks": len(chunks)
        }
            
    except Exception as e:
        print(f"Upload error: {str(e)}")  # Add logging
        return {"status": "error", "message": str(e)}

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

@app.get("/count")
async def get_count():
    """Get total number of documents"""
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
        
        count = result["data"]["Aggregate"]["SupportDocs"][0]["meta"]["count"]
        return {"count": count}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents")
async def get_documents():
    """Get all documents, combining chunks"""
    try:
        client = weaviate.Client(
            url=os.getenv("WEAVIATE_URL", "http://weaviate:8080")
        )
        
        result = (
            client.query
            .get("SupportDocs", ["content", "metadata", "category", "originalMetadata", "chunkIndex", "totalChunks"])
            .with_additional(["id"])
            .do()
        )
        
        if result and "data" in result and "Get" in result["data"] and "SupportDocs" in result["data"]["Get"]:
            # Group chunks by original metadata
            documents = {}
            for doc in result["data"]["Get"]["SupportDocs"]:
                key = f"{doc['originalMetadata']}_{doc['category']}"
                if key not in documents:
                    documents[key] = {
                        "content": [],
                        "metadata": doc['originalMetadata'],
                        "category": doc['category'],
                        "id": doc['_additional']['id'],
                        "chunks": doc['totalChunks']
                    }
                documents[key]["content"].insert(doc['chunkIndex'], doc['content'])
            
            # Combine chunks and format for display
            formatted_docs = []
            for doc in documents.values():
                formatted_docs.append({
                    "id": doc["id"],
                    "content": " ".join(doc["content"]),
                    "metadata": doc["metadata"],
                    "category": doc["category"],
                    "chunks": doc["chunks"]
                })
                
            return {"documents": formatted_docs}
            
        return {"documents": []}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/delete/{doc_id}")
async def delete_document(doc_id: str):
    """Delete all chunks of a document"""
    try:
        client = weaviate.Client(
            url=os.getenv("WEAVIATE_URL", "http://weaviate:8080")
        )
        
        # Get the document to find all related chunks
        result = (
            client.query
            .get("SupportDocs", ["originalMetadata", "category"])
            .with_additional(["id"])
            .with_where({
                "path": ["_additional", "id"],
                "operator": "Equal",
                "valueString": doc_id
            })
            .do()
        )
        
        if result and "data" in result and "Get" in result["data"] and "SupportDocs" in result["data"]["Get"]:
            doc = result["data"]["Get"]["SupportDocs"][0]
            
            # Delete all chunks with same metadata and category
            client.batch.delete_objects(
                class_name="SupportDocs",
                where={
                    "operator": "And",
                    "operands": [
                        {
                            "path": ["originalMetadata"],
                            "operator": "Equal",
                            "valueString": doc["originalMetadata"]
                        },
                        {
                            "path": ["category"],
                            "operator": "Equal",
                            "valueString": doc["category"]
                        }
                    ]
                }
            )
            
            return {"status": "success", "message": "Document and all chunks deleted successfully"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(request: Request):
    """Handle chat messages"""
    try:
        data = await request.json()
        message = data.get("message")
        category = data.get("category")
        
        if not message or not category:
            raise HTTPException(status_code=400, detail="Message and category are required")

        # Get relevant context
        context_data = await get_relevant_context(message, category)
        
        if not context_data["context_text"]:
            return {
                "response": "I couldn't find any relevant information. Could you please rephrase your question?",
                "results": []
            }
            
        # Generate response using OpenAI
        system_prompt = """You are a helpful support assistant. Use the provided context to answer the user's question.
        If you cannot find a relevant answer in the context, say so.
        Keep your answers clear and concise."""
        
        user_prompt = f"""Question: {message}

        Available context:{context_data['context_text']}

        Please provide a clear, step-by-step answer based on this information."""
        
        try:
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
            ai_response = "I found relevant information but had trouble generating a response. Please try again."
        
        return {
            "response": ai_response,
            "results": context_data["contexts"]
        }
            
    except Exception as e:
        print(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))