import weaviate
import json
from pprint import pprint

def check_weaviate():
    print("Connecting to Weaviate...")
    client = weaviate.Client(
        url="http://weaviate:8080"
    )
    
    print("\nChecking schema...")
    try:
        schema = client.schema.get()
        print("Current schema:")
        pprint(schema)
    except Exception as e:
        print(f"Error getting schema: {e}")
    
    print("\nChecking classes...")
    try:
        classes = client.schema.get()['classes']
        print(f"Found {len(classes) if classes else 0} classes:")
        for cls in (classes or []):
            print(f"- {cls['class']}")
    except Exception as e:
        print(f"Error getting classes: {e}")
    
    if not classes:
        print("\nNo classes found. Creating SupportDocs class...")
        try:
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
            print("Successfully created SupportDocs class")
        except Exception as e:
            print(f"Error creating schema: {e}")

    print("\nChecking for documents...")
    try:
        result = (
            client.query
            .get("SupportDocs", ["content", "category", "metadata"])
            .with_limit(5)  # Just get a few docs to check
            .do()
        )
        
        if result and 'data' in result and 'Get' in result['data'] and 'SupportDocs' in result['data']['Get']:
            docs = result['data']['Get']['SupportDocs']
            print(f"Found {len(docs)} sample documents")
            if docs:
                print("\nSample document:")
                pprint(docs[0])
        else:
            print("No documents found")
            
    except Exception as e:
        print(f"Error checking documents: {e}")

if __name__ == "__main__":
    check_weaviate() 