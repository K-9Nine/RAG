import weaviate
from typing import List, Dict
from src.config import settings
import json
import uuid

class DocumentProcessor:
    def __init__(self, collection_name: str = "SupportDocs"):
        print(f"Initializing Weaviate client with URL: {settings.WEAVIATE_URL}")
        
        self.client = weaviate.WeaviateClient(
            connection_params=weaviate.connect.ConnectionParams.from_url(
                url=settings.WEAVIATE_URL,
                headers={
                    "X-OpenAI-Api-Key": settings.OPENAI_API_KEY
                }
            )
        )
        self.collection_name = collection_name
        
        # Create schema if it doesn't exist
        self._create_schema()

    def _create_schema(self):
        """Create the class schema in Weaviate"""
        schema = {
            "class": self.collection_name,
            "description": "IT Support documents and knowledge base",
            "properties": [
                {
                    "name": "content",
                    "dataType": ["text"],
                    "description": "The content of the support document"
                },
                {
                    "name": "docType",
                    "dataType": ["string"],
                    "description": "Type of document (e.g., voip, email)"
                },
                {
                    "name": "category",
                    "dataType": ["string"],
                    "description": "Category of the document"
                }
            ],
            "vectorizer": "text2vec-openai"
        }
        
        try:
            self.client.schema.create(schema)
            print(f"Created schema for collection: {self.collection_name}")
        except Exception as e:
            print(f"Schema creation error (might already exist): {str(e)}")

    def add_documents(self, documents: List[Dict[str, str]]):
        """Add documents to Weaviate"""
        with self.client.batch as batch:
            batch_size = 100
            for doc in documents:
                try:
                    metadata = json.loads(doc['metadata'])
                except:
                    metadata = {}
                
                properties = {
                    "content": doc['content'],
                    "docType": metadata.get('type', ''),
                    "category": metadata.get('category', '')
                }
                
                # Generate a UUID based on content
                doc_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, doc['content']))
                
                batch.add_object(
                    collection=self.collection_name,
                    properties=properties,
                    uuid=doc_id
                )

    def query_documents(self, query: str, n_results: int = 3) -> List[Dict]:
        """Query Weaviate for relevant documents"""
        print(f"Querying Weaviate with: {query}")
        try:
            response = (
                self.client.query
                .get(self.collection_name, ["content", "docType", "category"])
                .with_near_text({"concepts": [query]})
                .with_limit(n_results)
                .do()
            )
            
            print(f"Weaviate response: {json.dumps(response, indent=2)}")
            
            documents = []
            if response and "data" in response and "Get" in response["data"]:
                results = response["data"]["Get"][self.collection_name]
                for r in results:
                    documents.append({
                        'content': r['content'],
                        'metadata': {
                            'type': r.get('docType', ''),
                            'category': r.get('category', '')
                        }
                    })
            
            print(f"Found {len(documents)} relevant documents")
            return documents
            
        except Exception as e:
            print(f"Error querying Weaviate: {str(e)}")
            return [] 