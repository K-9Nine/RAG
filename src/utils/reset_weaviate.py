import weaviate
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize client
client = weaviate.Client(
    url="http://localhost:8080",
    additional_headers={
        "X-OpenAI-Api-Key": os.getenv('OPENAI_API_KEY')
    }
)

# Delete the existing schema
try:
    client.schema.delete_class("SupportDocs")
    print("Deleted existing schema")
except Exception as e:
    print(f"Error deleting schema: {str(e)}") 