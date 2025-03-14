from agno.agent import Agent
from agno.models.groq import Groq
import os

# Get the API key from the .env file
with open(os.path.join("agents", ".env"), "r") as f:
    for line in f:
        if line.startswith("GROQ_API_KEY="):
            groq_api_key = line.strip().split("=")[1]
            os.environ["GROQ_API_KEY"] = groq_api_key
            break

# Initialize the agent
agent = Agent(
    model=Groq(id="llama-3.3-70b-versatile"),
    markdown=True
)

# Print the response in the terminal
agent.print_response("Share a 2 sentence horror story.")
