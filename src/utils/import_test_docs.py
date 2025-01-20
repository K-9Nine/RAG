import weaviate
import time

def import_test_docs():
    print("Connecting to Weaviate...")
    client = weaviate.Client(
        url="http://weaviate:8080"
    )
    
    # Test documents about phone system features
    test_docs = [
        {
            "content": "CallSwitch Voicemail Setup: To change your voicemail greeting, dial your extension, press * during the greeting, enter your PIN, then select option 4 to record a new greeting.",
            "category": "phone",
            "metadata": "voicemail configuration"
        },
        {
            "content": "Password Management: To change your CallSwitch password, log into the web portal, go to User Settings > Security, and select 'Change Password'. Enter your current password and your new password twice to confirm.",
            "category": "phone",
            "metadata": "security settings"
        },
        {
            "content": "Call Forwarding: Enable call forwarding by dialing *72 followed by the destination number. To disable, dial *73. You can also configure this in the CallSwitch web portal under User Settings > Forward.",
            "category": "phone",
            "metadata": "call management"
        },
        {
            "content": "Voicemail to Email: Set up voicemail to email notifications in the CallSwitch portal. Go to User Settings > Voicemail > Email Notifications and enter your email address.",
            "category": "phone",
            "metadata": "voicemail settings"
        },
        {
            "content": "Ring Groups: Administrators can configure ring groups in the CallSwitch portal under Admin > Groups. Add extensions and set ring patterns (simultaneous or sequential).",
            "category": "phone",
            "metadata": "call routing"
        }
    ]
    
    print(f"Importing {len(test_docs)} test documents...")
    
    # Import documents with batch processing
    with client.batch as batch:
        batch.batch_size = 5
        for doc in test_docs:
            print(f"Adding document: {doc['metadata']}")
            try:
                batch.add_data_object(
                    data_object=doc,
                    class_name="SupportDocs"
                )
            except Exception as e:
                print(f"Error adding document: {e}")
    
    print("Import complete. Waiting for indexing...")
    time.sleep(2)  # Give Weaviate time to index
    
    # Verify import
    try:
        result = (
            client.query
            .aggregate("SupportDocs")
            .with_meta_count()
            .do()
        )
        
        count = result["data"]["Aggregate"]["SupportDocs"][0]["meta"]["count"]
        print(f"Successfully imported {count} documents")
        
        # Show sample document
        sample = (
            client.query
            .get("SupportDocs", ["content", "category", "metadata"])
            .with_limit(1)
            .do()
        )
        
        if sample and 'data' in sample and 'Get' in sample['data'] and 'SupportDocs' in sample['data']['Get']:
            print("\nSample document:")
            print(sample['data']['Get']['SupportDocs'][0])
        
    except Exception as e:
        print(f"Error verifying import: {e}")

if __name__ == "__main__":
    import_test_docs() 