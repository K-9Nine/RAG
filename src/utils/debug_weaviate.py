import weaviate
import json

def debug_weaviate():
    print("\n=== Weaviate Debug Info ===\n")
    
    client = weaviate.Client(
        url="http://weaviate:8080"
    )
    
    # 1. Check total count
    print("Checking document count...")
    try:
        result = (
            client.query
            .aggregate("SupportDocs")
            .with_meta_count()
            .do()
        )
        count = result["data"]["Aggregate"]["SupportDocs"][0]["meta"]["count"]
        print(f"Total documents: {count}")
    except Exception as e:
        print(f"Error getting count: {e}")
    
    # 2. Get all documents
    print("\nFetching all documents...")
    try:
        result = (
            client.query
            .get("SupportDocs", ["content", "category", "metadata"])
            .with_limit(100)  # Adjust if needed
            .do()
        )
        
        if 'data' in result and 'Get' in result['data'] and 'SupportDocs' in result['data']['Get']:
            docs = result['data']['Get']['SupportDocs']
            print(f"\nFound {len(docs)} documents:")
            for i, doc in enumerate(docs, 1):
                print(f"\n--- Document {i} ---")
                print(f"Category: {doc.get('category', 'N/A')}")
                print(f"Metadata: {doc.get('metadata', 'N/A')}")
                print(f"Content: {doc.get('content', 'N/A')[:100]}...")  # First 100 chars
    except Exception as e:
        print(f"Error fetching documents: {e}")
    
    # 3. Try a test search
    print("\nTesting search functionality...")
    try:
        test_query = "password"
        result = (
            client.query
            .get("SupportDocs", ["content", "category", "metadata"])
            .with_near_text({"concepts": [test_query]})
            .with_limit(3)
            .with_additional(["distance"])
            .do()
        )
        
        print(f"\nSearch results for '{test_query}':")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error testing search: {e}")

if __name__ == "__main__":
    debug_weaviate() 