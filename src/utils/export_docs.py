import weaviate
import json
import os
from pathlib import Path

def export_documents():
    print("Connecting to Weaviate...")
    client = weaviate.Client(
        url="http://weaviate:8080"
    )
    
    print("Fetching all documents...")
    try:
        result = (
            client.query
            .get("SupportDocs", ["content", "category", "metadata"])
            .with_limit(10000)  # Adjust if you have more documents
            .do()
        )
        
        if 'data' in result and 'Get' in result['data'] and 'SupportDocs' in result['data']['Get']:
            docs = result['data']['Get']['SupportDocs']
            print(f"Found {len(docs)} documents")
            
            # Create data directory if it doesn't exist
            data_dir = Path(__file__).parent.parent.parent / "data"
            data_dir.mkdir(exist_ok=True)
            
            # Save documents to JSON file
            output_file = data_dir / "phone_docs.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(docs, f, indent=2, ensure_ascii=False)
            
            print(f"Successfully exported {len(docs)} documents to {output_file}")
            
        else:
            print("No documents found to export")
            
    except Exception as e:
        print(f"Error exporting documents: {e}")

if __name__ == "__main__":
    export_documents() 