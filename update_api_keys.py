import os
import sys

def update_api_keys():
    """
    Update API keys in the .env file
    """
    env_file = os.path.join("agents", ".env")
    
    # Create the agents directory if it doesn't exist
    os.makedirs("agents", exist_ok=True)
    
    # Check if .env file exists
    if os.path.exists(env_file):
        # Read existing keys
        with open(env_file, "r") as f:
            lines = f.readlines()
        
        # Parse existing keys
        keys = {}
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#"):
                key, value = line.split("=", 1)
                keys[key.strip()] = value.strip()
    else:
        keys = {}
    
    # Ask for API keys
    print("Please enter your API keys:")
    
    # DeepSeek API key
    deepseek_key = keys.get("DEEPSEEK_API_KEY", "")
    print(f"DeepSeek API key [{deepseek_key[:5] + '...' if deepseek_key else ''}]: ", end="")
    new_deepseek_key = input()
    if new_deepseek_key:
        keys["DEEPSEEK_API_KEY"] = new_deepseek_key
    elif "DEEPSEEK_API_KEY" not in keys:
        keys["DEEPSEEK_API_KEY"] = ""
    
    # Gemini API key
    gemini_key = keys.get("GEMINI_API_KEY", "")
    print(f"Gemini API key [{gemini_key[:5] + '...' if gemini_key else ''}]: ", end="")
    new_gemini_key = input()
    if new_gemini_key:
        keys["GEMINI_API_KEY"] = new_gemini_key
    elif "GEMINI_API_KEY" not in keys:
        keys["GEMINI_API_KEY"] = ""
    
    # Groq API key
    groq_key = keys.get("GROQ_API_KEY", "")
    print(f"Groq API key [{groq_key[:5] + '...' if groq_key else ''}]: ", end="")
    new_groq_key = input()
    if new_groq_key:
        keys["GROQ_API_KEY"] = new_groq_key
    elif "GROQ_API_KEY" not in keys:
        keys["GROQ_API_KEY"] = ""
    
    # Write the updated keys to the .env file
    with open(env_file, "w") as f:
        for key, value in keys.items():
            f.write(f"{key}={value}\n")
    
    print(f"\nAPI keys updated in {env_file}")

if __name__ == "__main__":
    update_api_keys()
