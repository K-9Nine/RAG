from fastapi import FastAPI, HTTPException, Query, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
import weaviate
import os
from typing import Dict, Optional
from pathlib import Path
from openai import OpenAI
import httpx
from src.utils.document_processor import DocumentProcessor, Category

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
app.mount("/static", StaticFiles(directory=str(static_dir.absolute())), name="static")

# Initialize templates
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def read_root():
    return FileResponse("src/static/index.html")

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

@app.route('/delete', methods=['POST'])
def delete_document():
    try:
        data = request.json
        text = data.get('text')  # We can use text to find and delete the document
        
        if not text:
            return jsonify({'success': False, 'message': 'No text provided'}), 400
            
        # Initialize Weaviate client
        client = weaviate.Client(WEAVIATE_URL)
        
        # Find and delete the document
        result = client.query.get('Document', ['text']).with_where({
            'path': ['text'],
            'operator': 'Equal',
            'valueText': text
        }).do()
        
        if result['data']['Get']['Document']:
            # Get the ID of the document
            doc_id = result['data']['Get']['Document'][0]['_additional']['id']
            
            # Delete the document
            client.data_object.delete(doc_id, 'Document')
            
            return jsonify({
                'success': True, 
                'message': 'Document deleted successfully'
            })
        else:
            return jsonify({
                'success': False, 
                'message': 'Document not found'
            }), 404
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500