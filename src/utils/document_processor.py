import weaviate
import os
from enum import Enum
from typing import Optional, Dict, Any, List
from src.config import settings
import json
import uuid

class Category(Enum):
    EMAIL = "email"
    PHONE = "phone"
    BROADBAND = "broadband"
    FIBRE = "fibre"

class DocumentProcessor:
    def __init__(self, collection_name: str = "SupportDocs"):
        print(f"Initializing Weaviate client with URL: {settings.WEAVIATE_URL}")
        
        self.client = weaviate.Client(
            url=os.getenv("WEAVIATE_URL", "http://weaviate:8080"),
            additional_headers={
                "X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")
            }
        )
        self.collection_name = collection_name
        
        # Create schema if it doesn't exist
        self._create_schema()

    def _create_schema(self):
        """Create the class schema in Weaviate"""
        schema = {
            "class": self.collection_name,
            "vectorizer": "text2vec-openai",
            "properties": [
                {
                    "name": "content",
                    "dataType": ["text"],
                },
                {
                    "name": "metadata",
                    "dataType": ["text"],
                },
                {
                    "name": "category",
                    "dataType": ["text"],
                    "description": "The category of the support document (email, phone, broadband, fibre)"
                }
            ]
        }
        
        try:
            self.client.schema.create_class(schema)
            print(f"Created schema for {self.collection_name}")
        except Exception as e:
            print(f"Schema might already exist: {e}")

    def add_documents(self, documents: List[Dict[str, str]]) -> None:
        """Add documents to Weaviate."""
        try:
            with self.client.batch as batch:
                batch.batch_size = 100
                for doc in documents:
                    self.client.batch.add_data_object(
                        data_object=doc,
                        class_name=self.collection_name
                    )
        except Exception as e:
            print(f"Error adding documents: {e}")

    def query_documents(self, query: str, n_results: int = 3) -> List[Dict]:
        """Query Weaviate for relevant documents"""
        print(f"Querying Weaviate with: {query}")
        try:
            response = (
                self.client.query
                .get(self.collection_name, ["content", "metadata", "category"])
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
                        'metadata': json.loads(r['metadata']),
                        'category': r['category']
                    })
            
            print(f"Found {len(documents)} relevant documents")
            return documents
            
        except Exception as e:
            print(f"Error querying Weaviate: {str(e)}")
            return []

    def process_document(self, content: str, metadata: str, category: Category) -> Optional[str]:
        """
        Process and store a document with its category
        """
        try:
            # Create the document
            result = self.client.data_object.create(
                data_object={
                    "content": content,
                    "metadata": metadata,
                    "category": category.value
                },
                class_name=self.collection_name
            )
            return result
        except Exception as e:
            print(f"Error processing document: {e}")
            return None

    def batch_process_documents(self, documents: List[Dict[str, Any]]) -> None:
        """Process multiple documents in batch."""
        try:
            with self.client.batch as batch:
                batch.batch_size = 100
                for doc in documents:
                    batch.add_data_object(
                        data_object=doc,
                        class_name=self.collection_name
                    )
        except Exception as e:
            print(f"Error in batch processing: {e}")

    def get_document_count(self, category: Optional[Category] = None) -> int:
        """
        Get count of documents, optionally filtered by category
        """
        query = self.client.query.aggregate(self.collection_name)
        
        if category:
            query = query.with_where({
                "path": ["category"],
                "operator": "Equal",
                "valueString": category.value
            })
        
        result = query.with_meta_count().do()
        
        return result["data"]["Aggregate"][self.collection_name][0]["meta"]["count"] 