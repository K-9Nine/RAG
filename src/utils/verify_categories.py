import weaviate
import os

def verify_categories():
    client = weaviate.Client(
        url="http://localhost:8080",
        additional_headers={
            "X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")
        }
    )
    
    # Get count of documents with phone category
    result = (
        client.query
        .aggregate("SupportDocs")
        .with_where({
            "path": ["category"],
            "operator": "Equal",
            "valueString": "phone"
        })
        .with_meta_count()
        .do()
    )
    
    print("Category verification results:")
    print(result)

if __name__ == "__main__":
    verify_categories() 