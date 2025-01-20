import weaviate
import os
import json
from pathlib import Path

def setup_weaviate():
    print("Connecting to Weaviate...")
    client = weaviate.Client(
        url="http://weaviate:8080"
    )
    
    # First, check if schema exists
    print("Checking existing schema...")
    try:
        client.schema.delete_all()
        print("Deleted existing schema")
    except Exception as e:
        print(f"Note: {e}")

    # Create new schema
    print("Creating new schema...")
    schema = {
        "class": "SupportDocs",
        "vectorizer": "text2vec-openai",
        "moduleConfig": {
            "text2vec-openai": {
                "model": "ada",
                "modelVersion": "002",
                "type": "text"
            }
        },
        "properties": [
            {
                "name": "content",
                "dataType": ["text"],
                "moduleConfig": {
                    "text2vec-openai": {
                        "skip": False,
                        "vectorizePropertyName": False
                    }
                }
            },
            {
                "name": "category",
                "dataType": ["text"],
                "moduleConfig": {
                    "text2vec-openai": {
                        "skip": True,
                        "vectorizePropertyName": False
                    }
                }
            },
            {
                "name": "metadata",
                "dataType": ["text"],
                "moduleConfig": {
                    "text2vec-openai": {
                        "skip": True,
                        "vectorizePropertyName": False
                    }
                }
            }
        ]
    }
    
    client.schema.create_class(schema)
    print("Schema created successfully")

    # Import documents
    print("Importing documents...")
    docs_path = Path(__file__).parent.parent.parent / "data" / "phone_docs.json"
    
    if not docs_path.exists():
        print(f"Error: Documents file not found at {docs_path}")
        return
    
    with open(docs_path, 'r', encoding='utf-8') as f:
        documents = json.load(f)
    
    print(f"Found {len(documents)} documents to import")
    
    # Batch import documents
    with client.batch as batch:
        batch.batch_size = 100
        for i, doc in enumerate(documents):
            print(f"Importing document {i+1}/{len(documents)}")
            
            properties = {
                "content": doc["content"],
                "category": "phone",
                "metadata": doc.get("metadata", "")
            }
            
            batch.add_data_object(
                data_object=properties,
                class_name="SupportDocs"
            )
    
    print("Import complete!")
    
    # Verify import
    result = (
        client.query
        .aggregate("SupportDocs")
        .with_meta_count()
        .do()
    )
    
    count = result["data"]["Aggregate"]["SupportDocs"][0]["meta"]["count"]
    print(f"Verified {count} documents in database")

if __name__ == "__main__":
    setup_weaviate() 