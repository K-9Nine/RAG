import weaviate
from typing import List, Dict
from ..config import settings
import json
import uuid

class DocumentProcessor:
    def __init__(self, collection_name: str = "SupportDocs"):
        print(f"Initializing Weaviate client with URL: {settings.WEAVIATE_URL}")
        
        self.client = weaviate.Client(
            url=settings.WEAVIATE_URL,
            additional_headers={
                "X-OpenAI-Api-Key": settings.OPENAI_API_KEY
            }
        )
        self.collection_name = collection_name
        
        # Create schema if it doesn't exist
        self._create_schema()

    def _create_schema(self):
        """Create the class schema in Weaviate"""
        try:
            # Check if collection exists
            collections = self.client.collections.list_all()
            if self.collection_name not in [c.name for c in collections]:
                # Create collection with properties
                self.client.collections.create(
                    name=self.collection_name,
                    description="IT Support documents and knowledge base",
                    vectorizer_config=weaviate.config.Configure.Vectorizer.text2vec_openai(),
                    properties=[
                        weaviate.Property(name="content", data_type=weaviate.DataType.TEXT),
                        weaviate.Property(name="docType", data_type=weaviate.DataType.TEXT),
                        weaviate.Property(name="category", data_type=weaviate.DataType.TEXT),
                    ]
                )
                print(f"Created collection: {self.collection_name}")
        except Exception as e:
            print(f"Schema creation error: {str(e)}")

    def add_documents(self, documents: List[Dict[str, str]]):
        """Add documents to Weaviate"""
        collection = self.client.collections.get(self.collection_name)
        
        with collection.batch.dynamic() as batch:
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
                
                batch.add_object(
                    properties=properties,
                    uuid=uuid.uuid5(uuid.NAMESPACE_DNS, doc['content'])
                )

    def query_documents(self, query: str, n_results: int = 3) -> List[Dict]:
        """Query Weaviate for relevant documents"""
        print(f"Querying Weaviate with: {query}")
        try:
            collection = self.client.collections.get(self.collection_name)
            response = collection.query.near_text(
                query=query,
                limit=n_results,
                return_properties=["content", "docType", "category"]
            )
            
            print(f"Weaviate response: {response}")
            
            documents = []
            for obj in response.objects:
                documents.append({
                    'content': obj.properties['content'],
                    'metadata': {
                        'type': obj.properties.get('docType', ''),
                        'category': obj.properties.get('category', '')
                    }
                })
            
            print(f"Found {len(documents)} relevant documents")
            return documents
            
        except Exception as e:
            print(f"Error querying Weaviate: {str(e)}")
            return [] 