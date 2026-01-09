from src.tools import tools
from src.prompt import get_prompt

user_location = "livingroom"
prompt = get_prompt(user_location, tools)
print(prompt)
