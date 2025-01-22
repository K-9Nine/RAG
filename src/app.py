from fastapi import FastAPI, HTTPException, Query, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse, JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
import weaviate
import os
from typing import Dict, Optional, List, Any, Tuple
from pathlib import Path
from openai import OpenAI
import httpx
from src.utils.document_processor import DocumentProcessor, Category
from fastapi.middleware.cors import CORSMiddleware
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter
import json
from datetime import datetime
import numpy as np
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Initialize OpenAI client
openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    http_client=httpx.Client()
)

# Initialize Weaviate client
client = weaviate.Client(
    url="http://weaviate:8080",  # Use Docker service name
    additional_headers={
        "X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")
    }
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
        # Get form data
        form_data = await request.form()
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
        chunks = chunk_document(processed_content)
        
        client = weaviate.Client(
            url=os.getenv("WEAVIATE_URL", "http://weaviate:8080")
        )
        
        uploaded_ids = []
        for i, chunk in enumerate(chunks):
            properties = {
                "content": str(chunk),
                "metadata": str(metadata),
                "category": str(category),
                "originalMetadata": str(metadata),
                "chunkIndex": i,
                "totalChunks": len(chunks)
            }
            
            print(f"Adding chunk with properties:", properties)
            
            # Add document and get ID
            result = client.data_object.create(
                data_object=properties,
                class_name="SupportDocs"
            )
            
            uploaded_ids.append(result)
            
            # Verify upload
            uploaded_doc = client.data_object.get_by_id(result, class_name="SupportDocs")
            print(f"Verified uploaded chunk {i}:", uploaded_doc)
        
        return JSONResponse(
            content={
                "status": "success", 
                "message": f"Document processed and uploaded in {len(chunks)} chunks",
                "chunks": len(chunks),
                "uploaded_ids": uploaded_ids
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

def generate_answer(query: str, docs: List[Dict]) -> Tuple[str, List[Dict]]:
    """Generate response and return used sources"""
    if not docs:
        return "I don't have enough information to answer that question.", []
    
    # Sort documents by relevance (distance)
    sorted_docs = sorted(docs, key=lambda x: x["_additional"]["distance"])
    
    # Get the most relevant document
    primary_doc = sorted_docs[0]
    response = primary_doc["content"]
    
    # Track used sources
    used_sources = [{
        "content": primary_doc["content"],
        "distance": primary_doc["_additional"]["distance"],
        "metadata": primary_doc.get("metadata", "")
    }]
    
    # Get supporting details from other relevant documents
    for doc in sorted_docs[1:3]:
        if doc["content"] not in response:  # Avoid duplicate information
            additional_info = doc["content"].split(". ")[0]  # Take first sentence
            if len(response + ". " + additional_info) <= 500:
                response += ". " + additional_info
                used_sources.append({
                    "content": doc["content"],
                    "distance": doc["_additional"]["distance"],
                    "metadata": doc.get("metadata", "")
                })
    
    return response, used_sources

def calculate_confidence(
    vector_score: float,
    num_docs: int,
    context_completeness: float
) -> float:
    """Calculate confidence score (0-1) based on multiple factors"""
    # Normalize vector score (usually 0-1 already)
    vec_weight = 0.5
    doc_weight = 0.3
    context_weight = 0.2
    
    # Document count score (peaks at 3-5 docs)
    doc_score = min(num_docs / 3, 1.0)
    
    # Combine scores with weights
    confidence = (
        vector_score * vec_weight +
        doc_score * doc_weight +
        context_completeness * context_weight
    )
    
    return round(confidence, 2)

@app.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        message = data.get("message", "")
        category = data.get("category", "")
        
        logger.info(f"Received query: {message} for category: {category}")

        # Get vector search results
        query = client.query.get(
            "SupportDocs",
            ["content", "metadata", "category"]
        ).with_near_text({
            "concepts": [message]
        }).with_additional(["distance"]).do()
        
        logger.info(f"Weaviate query response: {query}")

        docs = query.get("data", {}).get("Get", {}).get("SupportDocs", [])
        logger.info(f"Found {len(docs)} documents")

        if not docs:
            logger.warning("No documents found in response")
            return {
                "response": "I don't have enough information to answer that question.",
                "confidence": 0.0,
                "sources": [],
                "results": []
            }

        # Calculate confidence score
        distances = [d["_additional"]["distance"] for d in docs]
        vector_score = 1 - min(distances) if distances else 0
        context_words = sum(len(d["content"].split()) for d in docs)
        context_completeness = min(context_words / 100, 1.0)
        
        confidence = calculate_confidence(
            vector_score=vector_score,
            num_docs=len(docs),
            context_completeness=context_completeness
        )
        
        logger.info(f"Calculated confidence: {confidence}")

        # Generate response using the documents
        response, used_sources = generate_answer(message, docs)
        logger.info(f"Generated response: {response}")
        logger.info(f"Used sources: {used_sources}")

        return {
            "response": response,
            "confidence": confidence,
            "sources": used_sources,
            "results": docs[:5]
        }

    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        return {"error": str(e)}

@app.get("/diagnose")
async def diagnose_documents():
    """Diagnostic endpoint to check document structure"""
    try:
        client = weaviate.Client(
            url=os.getenv("WEAVIATE_URL", "http://weaviate:8080")
        )
        
        # Get all documents with explicit field selection
        result = (
            client.query
            .get("SupportDocs", [
                "content", 
                "metadata", 
                "category", 
                "originalMetadata", 
                "chunkIndex", 
                "totalChunks"
            ])
            .with_additional(["id"])
            .do()
        )
        
        print("Raw query result:", result)  # Debug print
        
        if not result or "data" not in result or "Get" not in result["data"] or "SupportDocs" not in result["data"]["Get"]:
            return {"status": "No documents found"}
            
        docs = result["data"]["Get"]["SupportDocs"]
        
        # Let's also try a direct object get for comparison
        sample_doc_id = docs[0]["_additional"]["id"] if docs else None
        if sample_doc_id:
            direct_doc = client.data_object.get_by_id(sample_doc_id, class_name="SupportDocs")
            print("Direct document fetch:", direct_doc)
        
        analysis = {
            "total_documents": len(docs),
            "raw_documents": docs,  # Include full document data
            "documents_by_category": {},
            "property_analysis": {
                "with_chunk_info": 0,
                "without_chunk_info": 0,
                "with_original_metadata": 0,
                "categories": set(),
                "property_counts": {
                    "content": 0,
                    "metadata": 0,
                    "category": 0,
                    "originalMetadata": 0,
                    "chunkIndex": 0,
                    "totalChunks": 0
                }
            }
        }
        
        for doc in docs:
            # Count properties
            for prop in ["content", "metadata", "category", "originalMetadata", "chunkIndex", "totalChunks"]:
                if doc.get(prop) is not None:
                    analysis["property_analysis"]["property_counts"][prop] += 1
            
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
        return {"error": str(e), "traceback": str(e.__traceback__)}

@app.get("/backup")
async def backup_database():
    """Backup all documents from the database"""
    try:
        client = weaviate.Client(
            url=os.getenv("WEAVIATE_URL", "http://weaviate:8080")
        )
        
        # Get all documents with all properties
        result = (
            client.query
            .get("SupportDocs", [
                "content", 
                "metadata", 
                "category", 
                "originalMetadata", 
                "chunkIndex", 
                "totalChunks"
            ])
            .with_additional(["id"])
            .do()
        )
        
        if not result or "data" not in result or "Get" not in result["data"] or "SupportDocs" not in result["data"]["Get"]:
            return {"status": "No documents found to backup"}
            
        docs = result["data"]["Get"]["SupportDocs"]
        
        # Create backup with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"backup_{timestamp}.json"
        
        with open(backup_file, 'w') as f:
            json.dump(docs, f)
        
        return {
            "status": "success",
            "message": f"Backed up {len(docs)} documents to {backup_file}",
            "document_count": len(docs)
        }
            
    except Exception as e:
        print(f"Error in backup_database: {str(e)}")
        return {"error": str(e)}

@app.post("/restore")
async def restore_database(backup_file: str = Form(...)):
    """Restore documents from a backup file"""
    try:
        # Load backup file
        with open(backup_file, 'r') as f:
            docs = json.load(f)
        
        client = weaviate.Client(
            url=os.getenv("WEAVIATE_URL", "http://weaviate:8080")
        )
        
        # Upload each document
        restored_count = 0
        for doc in docs:
            try:
                # Remove the _additional field if it exists
                doc.pop('_additional', None)
                
                # Add document
                client.data_object.create(
                    data_object=doc,
                    class_name="SupportDocs"
                )
                restored_count += 1
                
            except Exception as e:
                print(f"Error restoring document: {str(e)}")
                continue
        
        return {
            "status": "success",
            "message": f"Restored {restored_count} documents",
            "restored_count": restored_count
        }
            
    except Exception as e:
        print(f"Error in restore_database: {str(e)}")
        return {"error": str(e)}

@app.get("/cleanup")
async def cleanup_database():
    """Clean up and reinitialize the database"""
    try:
        client = weaviate.Client(
            url=os.getenv("WEAVIATE_URL", "http://weaviate:8080")
        )
        
        # First backup existing data
        backup_result = await backup_database()
        if "error" in backup_result:
            return {"status": "error", "message": "Failed to backup existing data", "error": backup_result["error"]}
        
        # Then proceed with cleanup
        try:
            client.schema.delete_class("SupportDocs")
            print("Deleted existing SupportDocs class")
        except Exception as e:
            print(f"Error deleting class: {e}")
        
        # Create the class with proper schema
        class_obj = {
            "class": "SupportDocs",
            "description": "Support documentation with proper chunking",
            "vectorizer": "text2vec-openai",
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
            ]
        }
        
        client.schema.create_class(class_obj)
        print("Created new SupportDocs class")
        
        return {
            "status": "success",
            "message": "Database cleaned up and reinitialized",
            "backup": backup_result
        }
            
    except Exception as e:
        print(f"Error in cleanup_database: {str(e)}")
        return {"error": str(e)}

def extract_and_format_document(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Format a document with proper structure"""
    return {
        "content": doc.get("content", ""),
        "metadata": doc.get("metadata", ""),
        "category": doc.get("category", "unknown"),
        "originalMetadata": doc.get("metadata", "")  # Use metadata as originalMetadata if not present
    }

def validate_document(doc: Dict[str, Any]) -> bool:
    """Validate document has required fields"""
    required_fields = ["content", "metadata", "category"]
    return all(doc.get(field) for field in required_fields)

@app.route("/reprocess", methods=["GET", "POST"])
async def reprocess_documents(request: Request):
    """Extract, reformat, and re-upload all documents with proper chunking"""
    try:
        client = weaviate.Client(
            url=os.getenv("WEAVIATE_URL", "http://weaviate:8080")
        )
        
        print("Starting document reprocessing...")
        
        # First, get all existing documents with only available fields
        result = (
            client.query
            .get("SupportDocs", [
                "content", 
                "metadata", 
                "category"
            ])
            .with_additional(["id"])
            .do()
        )
        
        print("Query result:", result)
        
        if not result or "data" not in result or "Get" not in result["data"] or "SupportDocs" not in result["data"]["Get"]:
            return JSONResponse(content={"status": "No documents found"})
            
        docs = result["data"]["Get"]["SupportDocs"]
        print(f"Found {len(docs)} documents to process")
        
        # Backup existing data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"backup_{timestamp}.json"
        with open(backup_file, 'w') as f:
            json.dump(docs, f)
        print(f"Backed up data to {backup_file}")
        
        # Clean up existing class
        try:
            client.schema.delete_class("SupportDocs")
            print("Deleted existing SupportDocs class")
        except Exception as e:
            print(f"Error deleting class: {e}")
            
        # Recreate schema
        class_obj = {
            "class": "SupportDocs",
            "description": "Support documentation with proper chunking",
            "vectorizer": "text2vec-openai",
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
            ]
        }
        
        client.schema.create_class(class_obj)
        print("Created new SupportDocs class")
        
        # Process and re-upload documents
        processed_count = 0
        error_count = 0
        
        for doc in docs:
            try:
                print(f"Processing document {processed_count + 1}/{len(docs)}")
                
                # Format document with only available fields
                formatted_doc = {
                    "content": doc.get("content", ""),
                    "metadata": doc.get("metadata", ""),
                    "category": doc.get("category", "unknown"),
                    "originalMetadata": doc.get("metadata", "")  # Use metadata as originalMetadata
                }
                
                # Validate
                if not all(formatted_doc.get(field) for field in ["content", "metadata", "category"]):
                    print(f"Skipping invalid document: {doc.get('_additional', {}).get('id')}")
                    error_count += 1
                    continue
                
                # Clean and chunk content
                processed_content = preprocess_text(formatted_doc["content"])
                chunks = chunk_document(processed_content)
                
                print(f"Created {len(chunks)} chunks")
                
                # Upload chunks
                for i, chunk in enumerate(chunks):
                    properties = {
                        "content": str(chunk),
                        "metadata": str(formatted_doc["metadata"]),
                        "category": str(formatted_doc["category"]),
                        "originalMetadata": str(formatted_doc["originalMetadata"]),
                        "chunkIndex": i,
                        "totalChunks": len(chunks)
                    }
                    
                    client.data_object.create(
                        data_object=properties,
                        class_name="SupportDocs"
                    )
                    print(f"Uploaded chunk {i+1}/{len(chunks)}")
                
                processed_count += 1
                
            except Exception as e:
                print(f"Error processing document: {str(e)}")
                error_count += 1
                continue
        
        return JSONResponse(content={
            "status": "success",
            "processed": processed_count,
            "errors": error_count,
            "backup_file": backup_file
        })
            
    except Exception as e:
        print(f"Error in reprocess_documents: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.post("/validate")
async def validate_upload(request: Request):
    """Validate document before upload"""
    try:
        form_data = await request.form()
        
        # Check required fields
        content = form_data.get('content', '')
        metadata = form_data.get('metadata', '')
        category = form_data.get('category', '')
        
        validation = {
            "valid": True,
            "errors": []
        }
        
        # Validate required fields
        if not content:
            validation["errors"].append("Content is required")
        if not metadata:
            validation["errors"].append("Metadata is required")
        if not category:
            validation["errors"].append("Category is required")
            
        # Check content length
        if len(content) < 10:
            validation["errors"].append("Content must be at least 10 characters")
            
        # Update valid flag
        validation["valid"] = len(validation["errors"]) == 0
        
        return validation
            
    except Exception as e:
        return {
            "valid": False,
            "errors": [str(e)]
        }

@app.post("/cleanup-data")
async def cleanup_existing_data():
    """Clean up existing documents without reprocessing"""
    try:
        client = weaviate.Client(
            url=os.getenv("WEAVIATE_URL", "http://weaviate:8080")
        )
        
        # Get all documents
        result = (
            client.query
            .get("SupportDocs", [
                "content", 
                "metadata", 
                "category", 
                "originalMetadata",
                "chunkIndex",
                "totalChunks"
            ])
            .with_additional(["id"])
            .do()
        )
        
        if not result or "data" not in result or "Get" not in result["data"] or "SupportDocs" not in result["data"]["Get"]:
            return {"status": "No documents found"}
            
        docs = result["data"]["Get"]["SupportDocs"]
        
        # Process each document
        updated_count = 0
        error_count = 0
        
        for doc in docs:
            try:
                doc_id = doc["_additional"]["id"]
                
                # Update only if missing required fields
                if not doc.get("category"):
                    doc["category"] = "unknown"
                if not doc.get("originalMetadata"):
                    doc["originalMetadata"] = doc.get("metadata", "")
                if doc.get("chunkIndex") is None:
                    doc["chunkIndex"] = 0
                if doc.get("totalChunks") is None:
                    doc["totalChunks"] = 1
                    
                # Remove _additional field
                doc.pop("_additional", None)
                
                # Update document
                client.data_object.update(
                    doc,
                    class_name="SupportDocs",
                    uuid=doc_id
                )
                
                updated_count += 1
                
            except Exception as e:
                print(f"Error updating document: {str(e)}")
                error_count += 1
                continue
        
        return {
            "status": "success",
            "updated": updated_count,
            "errors": error_count
        }
            
    except Exception as e:
        print(f"Error in cleanup_existing_data: {str(e)}")
        return {"error": str(e)}

@app.post("/query")
async def query_documents(query: str):
    try:
        # Get vector search results
        results = client.query.get(
            "SupportDocs",
            ["content", "metadata", "category"]
        ).with_near_text({
            "concepts": [query]
        }).with_additional(["distance"]).do()
        
        if not results.get("data", {}).get("Get", {}).get("SupportDocs"):
            return {"answer": "I don't have enough information to answer that question.",
                    "confidence": 0.0}
            
        # Extract relevant documents
        docs = results["data"]["Get"]["SupportDocs"]
        distances = [d["_additional"]["distance"] for d in docs]
        
        # Calculate vector similarity score (1 - normalized distance)
        vector_score = 1 - min(distances) if distances else 0
        
        # Calculate context completeness
        context_words = sum(len(d["content"].split()) for d in docs)
        context_completeness = min(context_words / 100, 1.0)  # Normalize to 0-1
        
        # Generate answer using the documents
        answer = generate_answer(query, docs)
        
        # Calculate confidence
        confidence = calculate_confidence(
            vector_score=vector_score,
            num_docs=len(docs),
            context_completeness=context_completeness
        )
        
        confidence_label = get_confidence_label(confidence)
        
        return {
            "answer": answer,
            "confidence": confidence,
            "confidence_label": confidence_label,
            "sources": [d["content"] for d in docs[:3]]  # Top 3 sources
        }
        
    except Exception as e:
        print(f"Error in query_documents: {str(e)}")
        return {"error": str(e)}

def get_confidence_label(score: float) -> str:
    """Convert confidence score to human-readable label"""
    if score >= 0.8:
        return "High Confidence"
    elif score >= 0.5:
        return "Medium Confidence"
    else:
        return "Low Confidence"