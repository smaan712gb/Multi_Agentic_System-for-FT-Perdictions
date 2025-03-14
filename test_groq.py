import os
from groq import Groq

# Get the API key from the .env file
with open(os.path.join("agents", ".env"), "r") as f:
    for line in f:
        if line.startswith("GROQ_API_KEY="):
            groq_api_key = line.strip().split("=")[1]
            break

print(f"Using Groq API key: {groq_api_key}")

try:
    client = Groq(
        api_key=groq_api_key,
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "you are a helpful assistant."
            },
            {
                "role": "user",
                "content": "Say hello in one sentence.",
            }
        ],
        model="llama-3.3-70b-versatile",
    )

    print("Success! Response:")
    print(chat_completion.choices[0].message.content)
except Exception as e:
    print(f"Error: {e}")
