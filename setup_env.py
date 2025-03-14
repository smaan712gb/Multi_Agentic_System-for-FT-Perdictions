import os
import sys
import dotenv

def setup_env():
    """
    Set up environment variables from .env files
    """
    # Load environment variables from root .env file (if exists)
    root_env_file = ".env"
    if os.path.exists(root_env_file):
        dotenv.load_dotenv(root_env_file)
    
    # Load environment variables from agents/.env file
    agents_env_file = os.path.join("agents", ".env")
    if not os.path.exists(agents_env_file):
        print(f"Error: {agents_env_file} not found.")
        print("Please create this file with your API keys.")
        print("Example content:")
        print("DEEPSEEK_API_KEY=your_deepseek_api_key")
        print("GEMINI_API_KEY=your_gemini_api_key")
        print("GROQ_API_KEY=your_groq_api_key")
        sys.exit(1)
    
    # Load environment variables from agents/.env file
    dotenv.load_dotenv(agents_env_file, override=True)
    
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
