from src.agent import Agent
from src.tools import tools
from src.model import llm

agent = Agent(
    llm=llm,
    tools=tools,
    user_location="bathroom"
)

agent.run()