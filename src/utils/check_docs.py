import weaviate
import os
import time
import json
from src.utils.document_processor import DocumentProcessor
from src.utils.context_manager import ContextManager

# Print the URL being used
weaviate_url = os.getenv("WEAVIATE_URL", "http://weaviate:8080")
print(f"Connecting to Weaviate at: {weaviate_url}")

# Try to connect with retries
max_retries = 5
retry_delay = 2

for attempt in range(max_retries):
    try:
        client = weaviate.WeaviateClient(
            connection_params=weaviate.connect.ConnectionParams.from_url(
                url=weaviate_url,
                headers={
                    "X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")
                }
            )
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

# Get document count
try:
    result = client.query.aggregate("SupportDocs").with_meta_count().do()
    count = result['data']['Aggregate']['SupportDocs'][0]['meta']['count']
    print(f"Number of documents in database: {count}")
except Exception as e:
    print(f"Error checking documents: {str(e)}")

def check_docs():
    processor = DocumentProcessor()
    context_manager = ContextManager(processor)
    
    query = "what is callswitch one"
    
    # Check raw documents
    print("\nChecking direct document retrieval:")
    docs = processor.query_documents(query, n_results=3)
    print(json.dumps(docs, indent=2))
    
    # Check context generation
    print("\nChecking context generation:")
    context = context_manager.get_context(query)
    print(context)
    
    # Check full prompt
    print("\nChecking enhanced prompt:")
    enhanced = context_manager.enhance_prompt(query, "You are an assistant.")
    print(enhanced)

if __name__ == "__main__":
    check_docs()
