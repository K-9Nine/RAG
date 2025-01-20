import requests
from requests.auth import HTTPBasicAuth

def test_chat():
    url = "http://localhost:8088/api/chat"
    auth = HTTPBasicAuth("testuser", "testpass123")
    
    test_messages = [
        "what is callswitch one",
        "how do I configure call recording",
        "explain the mobile app features"
    ]
    
    for message in test_messages:
        print(f"\nTesting message: {message}")
        print("=" * 50)
        
        payload = {
            "message": message,
            "user_id": "test_user",
            "chat_history": []
        }
        
        response = requests.post(url, json=payload, auth=auth)
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(response.json())

if __name__ == "__main__":
    test_chat() 