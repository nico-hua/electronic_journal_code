from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="qwen-plus",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key="sk-cc6863cc94ff4a8ca9055513bb381adb",
    temperature=0
)

# llm = ChatOpenAI(model="gpt-4o", 
#                 base_url="https://api.bianxie.ai/v1", 
#                 api_key="sk-SMltQxHCeYY8iATPrnJ5IbvQyF2JM2wslJerfvQJ4CObQ0jO",
#                 temperature=0
#)