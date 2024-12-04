import requests
import json
import time
from requests.exceptions import ConnectionError

def wait_for_server(timeout=30):
    """Wait for server to be ready"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get("http://localhost:8000/api/test")
            if response.status_code == 200:
                return True
        except ConnectionError:
            print("Waiting for server to start...")
            time.sleep(2)
    return False

# Example documents with pre-serialized metadata
documents = [
    {
        "content": "VoIP System: Our company uses Cisco IP phones. Common issues include network connectivity problems and power cycling. First steps: 1) Check if phone has power 2) Verify network cable is connected 3) Test network connectivity",
        "metadata": '{"type": "voip", "category": "hardware"}'
    },
    {
        "content": "Email System: We use Microsoft Exchange/Office 365. Common issues include Outlook configuration and password resets. For connection issues, first check Outlook's connection status and verify internet connectivity.",
        "metadata": '{"type": "email", "category": "software"}'
    }
]

def load_test_documents():
    if not wait_for_server():
        print("Error: Server not available. Please start the server first.")
        return

    try:
        response = requests.post(
            "http://localhost:8000/api/load-documents",
            json=documents
        )
        print(response.json())
    except Exception as e:
        print(f"Error loading documents: {str(e)}")

if __name__ == "__main__":
    load_test_documents() 