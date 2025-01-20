import weaviate
import time
import os

def setup_database():
    print("Connecting to Weaviate...")
    client = weaviate.Client(
        url="http://weaviate:8080"
    )

    # Delete existing schema if it exists
    print("Cleaning up existing schema...")
    try:
        client.schema.delete_all()
        print("Deleted existing schema")
    except Exception as e:
        print(f"Note: {e}")

    time.sleep(2)  # Wait for deletion to complete

    # Create new schema
    print("Creating new schema...")
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

    try:
        client.schema.create_class(schema)
        print("Schema created successfully")
    except Exception as e:
        print(f"Error creating schema: {e}")
        return

    # Add test documents
    print("\nAdding test documents...")
    test_docs = [
        # Phone System
        {
            "content": "To change your CallSwitch password, log into the web portal, go to User Settings > Security, and select 'Change Password'. Enter your current password and your new password twice to confirm.",
            "category": "phone",
            "metadata": "password management"
        },
        {
            "content": "CallSwitch Voicemail Setup: To change your voicemail greeting, dial your extension, press * during the greeting, enter your PIN, then select option 4 to record a new greeting.",
            "category": "phone",
            "metadata": "voicemail configuration"
        },
        {
            "content": "Call Forwarding: Enable call forwarding by dialing *72 followed by the destination number. To disable, dial *73. You can also configure this in the CallSwitch web portal under User Settings > Forward.",
            "category": "phone",
            "metadata": "call management"
        },
        {
            "content": "Conference Calling: To start a conference call, dial the first participant and press *2 after they answer. This puts them on hold. Dial the second participant and press *2 after they answer. Press *2 again to connect all parties. You can add up to 5 participants.",
            "category": "phone",
            "metadata": "conference calls"
        },
        # Fibre Leased Line
        {
            "content": "Our Fibre Leased Line service provides dedicated, symmetric bandwidth from 100Mbps to 10Gbps. It includes a 99.9% uptime SLA, 24/7 support, and a 5-hour fix time guarantee. Installation typically takes 45-65 working days.",
            "category": "fibre",
            "metadata": "service overview"
        },
        {
            "content": "Fibre Leased Line fault reporting: Contact our 24/7 support team immediately at the dedicated number. Have your circuit reference ready. We'll begin diagnostics within 15 minutes and dispatch engineers if needed, with updates every hour.",
            "category": "fibre",
            "metadata": "fault reporting"
        },
        # Broadband
        {
            "content": "FTTC Broadband offers speeds up to 80Mbps download and 20Mbps upload. Installation requires an engineer visit to install a new master socket. Typical installation time is 10-15 working days.",
            "category": "broadband",
            "metadata": "FTTC service"
        },
        {
            "content": "For broadband faults, first check your router's power and connections. Try restarting the router. If issues persist, run a speed test and contact our support team with your results and account number.",
            "category": "broadband",
            "metadata": "troubleshooting"
        },
        # Microsoft Email
        {
            "content": "To set up Microsoft 365 email on your phone: Open the Outlook app, tap Add Account, enter your email and password. For manual setup, use outlook.office365.com as the server, port 993 for IMAP, and 587 for SMTP.",
            "category": "email",
            "metadata": "mobile setup"
        },
        {
            "content": "Reset your Microsoft 365 password through the web portal at portal.office.com. Click on your profile picture, select 'View account', then 'Security & privacy' and 'Password'. Follow the prompts to create a new password.",
            "category": "email",
            "metadata": "password reset"
        },
        {
            "content": "Microsoft Teams is included with your Microsoft 365 subscription. Download Teams from teams.microsoft.com, sign in with your email, and you can start collaborating with video calls, chat, and file sharing.",
            "category": "email",
            "metadata": "teams setup"
        }
    ]

    with client.batch as batch:
        batch.batch_size = len(test_docs)
        for doc in test_docs:
            print(f"Adding document: {doc['metadata']} ({doc['category']})")
            try:
                batch.add_data_object(
                    data_object=doc,
                    class_name="SupportDocs"
                )
            except Exception as e:
                print(f"Error adding document: {e}")

    time.sleep(2)  # Wait for indexing

    # Verify setup
    print("\nVerifying setup...")
    try:
        result = (
            client.query
            .aggregate("SupportDocs")
            .with_meta_count()
            .do()
        )
        
        count = result["data"]["Aggregate"]["SupportDocs"][0]["meta"]["count"]
        print(f"Successfully verified {count} documents in database")
        
        # Test search by category
        for category in ["phone", "fibre", "broadband", "email"]:
            print(f"\nTesting {category} category...")
            test = (
                client.query
                .get("SupportDocs")
                .with_where({
                    "path": ["category"],
                    "operator": "Equal",
                    "valueString": category
                })
                .with_limit(1)
                .do()
            )
            
            if test and 'data' in test and 'Get' in test['data'] and 'SupportDocs' in test['data']['Get']:
                print(f"✓ {category} category verified")
            else:
                print(f"✗ Warning: {category} category test failed")
            
    except Exception as e:
        print(f"Error verifying setup: {e}")

if __name__ == "__main__":
    setup_database() 