from typing import List
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool
from langchain_community.chat_message_histories import ChatMessageHistory
from .prompt import get_prompt, FINISH_SIGNAL
from .output_parser import AgentOutputParser
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from pydantic import ValidationError
import time

class Agent:
    def __init__(
        self,
        llm: BaseChatModel,
        tools: List[BaseTool],
        user_location: str
    ):
        self.llm = llm
        self.prompt = get_prompt(user_location, tools)
        self.tools = {tool.name: tool for tool in tools}
        self.output_parser = AgentOutputParser()
        self.chat_history_memory = ChatMessageHistory()

    def run(self):
        instruction = input("Please enter the command and enter 'exit' to exit: ")
        start_time = time.time()
        if instruction != "exit" and instruction != "":
            self.chat_history_memory.add_message(SystemMessage(content=self.prompt))
            self.chat_history_memory.add_user_message(HumanMessage(content=instruction))

            loop_count = 0
            while True:
                loop_count += 1
                if loop_count > 10:
                    print("Max loop reached. Exiting...")
                    return
                
                # Send message to AI, get response
                messages = self.chat_history_memory.messages
                assistant_reply = self.llm.invoke(messages).content

                # Print Assistant thoughts
                print(assistant_reply)  
                self.chat_history_memory.add_message(AIMessage(content=assistant_reply))

                # Get command name and arguments
                action = self.output_parser.parse(assistant_reply)
                if action.name == FINISH_SIGNAL:
                    print(action.args['response'])
                    end_time = time.time()
                    print(f"Total time: {end_time - start_time}")
                    instruction = input("Please enter the command and enter 'exit' to exit: ")
                    if instruction == "exit" or instruction == "":
                        return
                    # deal with feedback
                    result = instruction
                    loop_count = 0
                elif action.name in self.tools:
                    tool = self.tools[action.name]
                    try:
                        observation = tool.run(action.args)
                    except ValidationError as e:
                        observation = (
                            f"Validation Error in args: {str(e)}, args: {action.args}"
                        )
                    except Exception as e:
                        observation = (
                            f"Error: {str(e)}, {type(e).__name__}, args: {action.args}"
                        )
                    result = f"Command {tool.name} returned: {observation}"
                elif action.name == "ERROR":
                    result = f"Error: {action.args}. "
                else:
                    result = (
                        f"Unknown command '{action.name}'. "
                        f"Please refer to the 'COMMANDS' list for available "
                        f"commands and only respond in the specified JSON format."
                    )
                
                # add the result to messages
                self.chat_history_memory.add_message(HumanMessage(content=result))
                
    
