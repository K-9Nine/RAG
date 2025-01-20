import weaviate
import os
import time

# Print the URL being used
weaviate_url = os.getenv("WEAVIATE_URL", "http://localhost:8087")
print(f"Connecting to Weaviate at: {weaviate_url}")

# Try to connect with retries
max_retries = 5
retry_delay = 5

for attempt in range(max_retries):
    try:
        print(f"\nAttempt {attempt + 1}/{max_retries} to connect to Weaviate...")
        
        client = weaviate.Client(
            url=weaviate_url,
            additional_headers={
                "X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")
            }
        )
        
        # Test connection
        client.schema.get()
        print("Successfully connected to Weaviate")
        break
        
    except Exception as e:
        print(f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}")
        if attempt < max_retries - 1:
            print(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
        else:
            raise Exception("Failed to connect to Weaviate after multiple attempts")

# Delete existing schema if it exists
try:
    client.schema.delete_all()
    print("Deleted existing schema")
except Exception as e:
    print(f"Error deleting schema: {str(e)}")

# Define the schema
class_obj = {
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
            "name": "metadata",
            "dataType": ["text"],
            "moduleConfig": {
                "text2vec-openai": {
                    "skip": True
                }
            }
        }
    ]
}

# Create the schema
try:
    client.schema.create_class(class_obj)
    print("Schema created successfully")
except Exception as e:
    print(f"Error creating schema: {str(e)}")

# Verify the documents were added
try:
    result = client.query.get("SupportDocs").do()
    print(f"\nVerification - Found {len(result['data']['Get']['SupportDocs'])} documents in Weaviate")
    
    # Print first few documents as a sample
    print("\nSample documents:")
    for doc in result['data']['Get']['SupportDocs'][:3]:  # Show first 3 docs
        print(f"\nContent: {doc['content'][:100]}...")  # Show first 100 chars of content
        print(f"Metadata: {doc['metadata']}")
except Exception as e:
    print(f"Error verifying documents: {str(e)}")