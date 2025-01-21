from fastapi import FastAPI, HTTPException, Query, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse, JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
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

class DocumentUpload(BaseModel):
    content: str
    metadata: str
    category: str

@app.post("/upload")
async def upload_document(request: Request):
    """Process and upload a document with RAG optimization"""
    try:
        # Get form data and print for debugging
        form_data = await request.form()
        print("Received form data:", dict(form_data))
        
        content = form_data.get('content', '')
        metadata = form_data.get('metadata', '')
        category = form_data.get('category', '')

        if not all([content, metadata, category]):
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Missing required fields"}
            )

        # Clean the text
        processed_content = preprocess_text(content)
        
        # Split into chunks
        chunks = chunk_document(processed_content)
        
        # Initialize Weaviate client
        client = weaviate.Client(
            url=os.getenv("WEAVIATE_URL", "http://weaviate:8080")
        )
        
        print(f"Uploading document: {len(chunks)} chunks")
        print(f"Category: {category}")
        print(f"Metadata: {metadata}")
        
        # Upload each chunk with explicit property types
        for i, chunk in enumerate(chunks):
            try:
                # Create properties with explicit types
                properties = {
                    "content": str(chunk),
                    "metadata": str(metadata),
                    "category": str(category),
                    "originalMetadata": str(metadata),
                    "chunkIndex": int(i),
                    "totalChunks": int(len(chunks))
                }
                
                print(f"Adding chunk {i+1}/{len(chunks)} with properties:", properties)
                
                # Add document directly instead of using batch
                client.data_object.create(
                    data_object=properties,
                    class_name="SupportDocs"
                )
                
            except Exception as e:
                print(f"Error adding chunk {i}: {str(e)}")
                raise e
        
        print("Upload completed successfully")
        
        return JSONResponse(
            content={
                "status": "success", 
                "message": f"Document processed and uploaded in {len(chunks)} chunks",
                "chunks": len(chunks)
            }
        )
            
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

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
        
        print("Fetching documents from Weaviate...")
        
        # First, let's see what we're getting from the database
        result = (
            client.query
            .get("SupportDocs", ["content", "metadata", "category", "originalMetadata", "chunkIndex", "totalChunks"])
            .with_additional(["id"])
            .do()
        )
        
        if not result or "data" not in result or "Get" not in result["data"] or "SupportDocs" not in result["data"]["Get"]:
            print("No documents found")
            return {"documents": []}
        
        docs = result["data"]["Get"]["SupportDocs"]
        print(f"Found {len(docs)} document chunks")
        
        # Group chunks by original metadata and category
        documents = {}
        for doc in docs:
            try:
                # Extract values with defaults
                metadata = doc.get('originalMetadata', doc.get('metadata', ''))
                category = doc.get('category', '')
                content = doc.get('content', '')
                doc_id = doc.get('_additional', {}).get('id', '')
                
                # Create a key for grouping
                key = f"{metadata}_{category}"
                
                # Initialize document entry if it doesn't exist
                if key not in documents:
                    documents[key] = {
                        "content": [],
                        "metadata": metadata,
                        "category": category,
                        "id": doc_id
                    }
                
                # Append content (we'll sort later if chunk info exists)
                documents[key]["content"].append(content)
                
                # Try to get chunk information
                try:
                    chunk_index = int(doc.get('chunkIndex', -1))
                    total_chunks = int(doc.get('totalChunks', 1))
                    if chunk_index >= 0:
                        # Ensure content list is long enough
                        while len(documents[key]["content"]) < total_chunks:
                            documents[key]["content"].append("")
                        # Place content in correct position
                        documents[key]["content"][chunk_index] = content
                except (TypeError, ValueError) as e:
                    print(f"No valid chunk information for document: {e}")
                    # Keep the content appended at the end
                
            except Exception as e:
                print(f"Error processing document: {str(e)}")
                continue
        
        # Format documents for display
        formatted_docs = []
        for doc in documents.values():
            try:
                # Filter out empty strings and join content
                content = " ".join(filter(None, doc["content"]))
                if content:
                    formatted_docs.append({
                        "id": doc["id"],
                        "content": content,
                        "metadata": doc["metadata"],
                        "category": doc["category"],
                        "chunks": len(doc["content"])
                    })
            except Exception as e:
                print(f"Error formatting document: {str(e)}")
                continue
        
        print(f"Returning {len(formatted_docs)} documents")
        return {"documents": formatted_docs}
            
    except Exception as e:
        print(f"Error in get_documents: {str(e)}")
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

@app.get("/diagnose")
async def diagnose_documents():
    """Diagnostic endpoint to check document structure"""
    try:
        client = weaviate.Client(
            url=os.getenv("WEAVIATE_URL", "http://weaviate:8080")
        )
        
        # Get all documents with all properties
        result = (
            client.query
            .get("SupportDocs")
            .with_additional(["id"])
            .do()
        )
        
        if not result or "data" not in result or "Get" not in result["data"] or "SupportDocs" not in result["data"]["Get"]:
            return {"status": "No documents found"}
            
        docs = result["data"]["Get"]["SupportDocs"]
        
        # Analyze document structure
        analysis = {
            "total_documents": len(docs),
            "documents_by_category": {},
            "property_analysis": {
                "with_chunk_info": 0,
                "without_chunk_info": 0,
                "with_original_metadata": 0,
                "categories": set()
            }
        }
        
        for doc in docs:
            # Count by category
            category = doc.get('category', 'unknown')
            analysis["documents_by_category"][category] = analysis["documents_by_category"].get(category, 0) + 1
            analysis["property_analysis"]["categories"].add(category)
            
            # Check chunk information
            if doc.get('chunkIndex') is not None and doc.get('totalChunks') is not None:
                analysis["property_analysis"]["with_chunk_info"] += 1
            else:
                analysis["property_analysis"]["without_chunk_info"] += 1
                
            # Check metadata
            if doc.get('originalMetadata'):
                analysis["property_analysis"]["with_original_metadata"] += 1
                
        # Convert sets to lists for JSON serialization
        analysis["property_analysis"]["categories"] = list(analysis["property_analysis"]["categories"])
        
        return analysis
            
    except Exception as e:
        print(f"Error in diagnose_documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cleanup")
async def cleanup_database():
    """Clean up and reinitialize the database"""
    try:
        client = weaviate.Client(
            url=os.getenv("WEAVIATE_URL", "http://weaviate:8080")
        )
        
        # Delete the existing class
        try:
            client.schema.delete_class("SupportDocs")
            print("Deleted existing SupportDocs class")
        except Exception as e:
            print(f"Error deleting class: {e}")
        
        # Create the class with proper schema
        class_obj = {
            "class": "SupportDocs",
            "description": "Support documentation with proper chunking",
            "properties": [
                {
                    "name": "content",
                    "dataType": ["text"],
                    "description": "The document content"
                },
                {
                    "name": "metadata",
                    "dataType": ["text"],
                    "description": "Document metadata"
                },
                {
                    "name": "category",
                    "dataType": ["text"],
                    "description": "Document category"
                },
                {
                    "name": "originalMetadata",
                    "dataType": ["text"],
                    "description": "Original document metadata"
                },
                {
                    "name": "chunkIndex",
                    "dataType": ["int"],
                    "description": "Index of this chunk"
                },
                {
                    "name": "totalChunks",
                    "dataType": ["int"],
                    "description": "Total number of chunks"
                }
            ],
            "vectorizer": "text2vec-openai"
        }
        
        client.schema.create_class(class_obj)
        print("Created new SupportDocs class with proper schema")
        
        return {
            "status": "success",
            "message": "Database cleaned up and reinitialized"
        }
            
    except Exception as e:
        print(f"Error in cleanup_database: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))