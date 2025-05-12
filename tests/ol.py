import requests
import json

# Ollama API endpoint
url = "http://130.61.213.45:11434/api/chat"

# Request payload
payload = {
    "model": "deepseek-r1:latest",
    "messages": [
        {
            "role": "user",
            "content": "Why is the sky blue?"
        }
    ],
    "stream": True
}

try:
    # Send POST request with streaming
    response = requests.post(url, json=payload, stream=True)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Iterate over the streaming response
        for line in response.iter_lines():
            if line:
                # Decode the line and parse the JSON
                decoded_line = line.decode('utf-8')
                try:
                    data = json.loads(decoded_line)
                    # Print the message content if it exists
                    if "message" in data and "content" in data["message"]:
                        print(data["message"]["content"], end="", flush=True)
                except json.JSONDecodeError:
                    print(f"Failed to decode JSON: {decoded_line}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")