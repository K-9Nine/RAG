import weaviate
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()

# Initialize client
client = weaviate.Client(
    url="http://localhost:8080",
    additional_headers={
        "X-OpenAI-Api-Key": os.getenv('OPENAI_API_KEY')
    }
)

# Get all documents
result = client.query.get("SupportDocs", ["content", "docType", "category"]).do()
print(json.dumps(result, indent=2)) 