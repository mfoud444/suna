# import requests

# url = "https://mfoud444-oi.hf.space//api/generate"  # Placeholder, must confirm real path

# headers = {
#     "Content-Type": "application/json"
# }

# payload = {
#     "model": "qwen2.5-coder:0.5b",
#     "messages": [
#         {"role": "user", "content": "Write a Python function to reverse a string."}
#     ],
#     "stream": False  # Set True if the API supports streaming
# }

# response = requests.post(url, headers=headers, json=payload)

# if response.ok:
#     print(response.json())
# else:
#     print("Error:", response.status_code, response.text)


from openai import OpenAI

# Initialize the OpenAI client
client = OpenAI(
    api_key="secret",  # Set an API key (use "secret" if your provider doesn't require one)
    base_url="https://mfoud444-docsp.hf.space/v1"  # Point to your local or custom API endpoint
)

# Create a chat completion request
response = client.chat.completions.create(
    model="llama-3.2-90b",  # Specify the model to use
    messages=[{"role": "user", "content": "Write a poem about a tree"}],  # Define the input message
    stream=True,  # Enable streaming for real-time responses
)

# Handle the response
if isinstance(response, dict):
    # Non-streaming response
    print(response.choices[0].message.content)
else:
    # Streaming response
    for token in response:
        content = token.choices[0].delta.content
        if content is not None:
            print(content, end="", flush=True)