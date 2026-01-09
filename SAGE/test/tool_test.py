from src.tools import get_room_info

res = get_room_info.invoke({"rooms": ["livingroom", "kitchen"]})
print(res)