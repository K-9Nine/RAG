import weaviate
import os
import time

# Print the URL being used
weaviate_url = os.getenv("WEAVIATE_URL", "http://weaviate:8080")
print(f"Connecting to Weaviate at: {weaviate_url}")

# Try to connect with retries
max_retries = 5
retry_delay = 2

for attempt in range(max_retries):
    try:
        client = weaviate.Client(
            url=weaviate_url,
            additional_headers={
                "X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")
            },
            timeout_config=(5, 15)  # (connect timeout, read timeout)
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
