import os
import sys
import dotenv

def setup_env():
    """
    Set up environment variables from .env file
    """
    # Load environment variables from .env file
    env_file = os.path.join("agents", ".env")
    if not os.path.exists(env_file):
        print(f"Error: {env_file} not found.")
        print("Please create this file with your API keys.")
        print("Example content:")
        print("DEEPSEEK_API_KEY=your_deepseek_api_key")
        print("GEMINI_API_KEY=your_gemini_api_key")
        print("GROQ_API_KEY=your_groq_api_key")
        sys.exit(1)
    
    # Load environment variables
    dotenv.load_dotenv(env_file)
    
    # Check if API keys are set
    api_keys = {
        "DEEPSEEK_API_KEY": os.environ.get("DEEPSEEK_API_KEY"),
        "GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY"),
        "GROQ_API_KEY": os.environ.get("GROQ_API_KEY"),
        "ALPHA_VANTAGE_API_KEY": os.environ.get("ALPHA_VANTAGE_API_KEY", "4M6VASN5R8SRDP29")
    }
    
    missing_keys = [key for key, value in api_keys.items() if not value]
    if missing_keys:
        print(f"Error: The following API keys are missing: {', '.join(missing_keys)}")
        print("Please add them to the .env file.")
        sys.exit(1)
    
    print("Environment variables loaded successfully.")
    print(f"API keys found: {', '.join(api_keys.keys())}")

if __name__ == "__main__":
    setup_env()
