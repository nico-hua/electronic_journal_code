from langchain_core.tools import tool
from typing import List
from .config import DEFAULT_ROOMS
from .mysql import MySQL

@tool
def get_room_info(rooms: List[str]) -> dict:
    """
    Function:
        Query the environmental and device information of given rooms.
    Input:
        rooms (List[str]): list of valid room names, each value must be one of ["balcony", "livingroom", "kitchen", "bathroom", "cloakroom", "masterbedroom", "guestbedroom"].
    Output (JSON):
        {
            "room_info": [
                {
                    "room": "livingroom",
                    "environment": [...],   # Sensor data (temperature, humidity, etc.)
                    "devices": [...]        # Smart devices (lights, air_conditioner, etc.)
                },
                ...
            ],
            "message": "success or error info"
        }
    """
    res = {}
    # 检查房间名是否正确
    for room in rooms:
        if room not in DEFAULT_ROOMS:
            res["room_info"] = []
            res["message"] = f"Invalid room name: {room}. Valid options are: {DEFAULT_ROOMS}"
            return res
    # 数据库配置
    mysql = MySQL()
    # 获取各房间的设备信息
    room_infos = []
    for room in rooms:
        room_info = mysql.get_room_info(room)
        room_infos.append(room_info)
    # 关闭数据库连接
    mysql.close_client()
    res["room_info"] = room_infos
    res["message"] = "success"
    return res

tools = [
    get_room_info
]