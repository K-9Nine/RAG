import weaviate
import os
import time

def update_categories():
    print("Starting category update process...")
    
    # Wait for Weaviate to be ready
    client = weaviate.Client(url="http://weaviate:8080")
    max_retries = 5
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            print("Checking Weaviate connection...")
            client.schema.get()
            print("Successfully connected to Weaviate!")
            break
        except Exception as e:
            retry_count += 1
            print(f"Connection attempt {retry_count} failed: {e}")
            if retry_count < max_retries:
                print("Retrying in 5 seconds...")
                time.sleep(5)
            else:
                print("Failed to connect to Weaviate after multiple attempts")
                return
    
    try:
        print("\nUpdating schema to ensure category property exists...")
        try:
            schema = {
                "dataType": ["text"],
                "name": "category",
                "description": "The category of the document"
            }
            client.schema.property.create("SupportDocs", schema)
            print("✓ Added category property to schema")
        except Exception as schema_error:
            print(f"Note: Category property might already exist: {schema_error}")

        print("\nFetching all documents...")
        result = (
            client.query
            .get("SupportDocs", ["_additional {id}"])
            .with_limit(10000)
            .do()
        )

        if 'data' in result and 'Get' in result['data'] and 'SupportDocs' in result['data']['Get']:
            docs = result['data']['Get']['SupportDocs']
            total = len(docs)
            print(f"Found {total} documents to update")
            
            print("\nUpdating documents one by one...")
            updated = 0
            for doc in docs:
                try:
                    doc_id = doc['_additional']['id']
                    client.data_object.update(
                        data_object={"category": "phone"},
                        class_name="SupportDocs",
                        uuid=doc_id
                    )
                    updated += 1
                    if updated % 10 == 0:
                        print(f"Progress: {updated}/{total} documents")
                except Exception as update_error:
                    print(f"Error updating document: {update_error}")
            
            print(f"\n✓ Updated {updated} out of {total} documents")
            
            print("\nVerifying updates...")
            verify = (
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
            
            count = verify["data"]["Aggregate"]["SupportDocs"][0]["meta"]["count"]
            print(f"✓ Verified {count} documents now have 'phone' category")
            
        else:
            print("No documents found to update")
            
    except Exception as e:
        print(f"Error during update process: {e}")

if __name__ == "__main__":
    update_categories() 