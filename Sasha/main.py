from src.agent import Agent
from src.model import llm

agent = Agent(
    llm = llm,
    user_location = "bathroom"
)

agent.run()