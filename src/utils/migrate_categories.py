import weaviate
import os
from typing import List, Dict

def migrate_to_phone_category():
    # Use localhost when running locally
    client = weaviate.Client(
        url="http://localhost:8080",  # Changed from weaviate:8080 to localhost:8080
        additional_headers={
            "X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")
        }
    )
    
    # First, update schema to include category if it doesn't exist
    try:
        schema = {
            "dataType": ["text"],
            "name": "category"
        }
        client.schema.property.create("SupportDocs", schema)
        print("Added category property to schema")
    except Exception as e:
        print(f"Category property might already exist: {e}")

    # Batch update all documents to phone category
    try:
        result = (
            client.query
            .get("SupportDocs", ["_additional {id}"])
            .with_limit(10000)
            .do()
        )

        if 'data' in result and 'Get' in result['data'] and 'SupportDocs' in result['data']['Get']:
            docs = result['data']['Get']['SupportDocs']
            
            # Update each document with phone category
            batch_size = 100
            for i in range(0, len(docs), batch_size):
                batch = docs[i:i + batch_size]
                
                with client.batch as batch_client:
                    for doc in batch:
                        doc_id = doc['_additional']['id']
                        batch_client.data_object.update(
                            {"category": "phone"},
                            class_name="SupportDocs",
                            uuid=doc_id
                        )
                
                print(f"Updated documents {i} to {i + len(batch)}")
            
            print(f"Successfully updated {len(docs)} documents to phone category")
        else:
            print("No documents found to update")
            
    except Exception as e:
        print(f"Error updating documents: {e}")

if __name__ == "__main__":
    migrate_to_phone_category() 