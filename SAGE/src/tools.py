from langchain_core.tools import tool
from typing import List
from .config import DEFAULT_ROOMS, TURN_ON_DEVICE_TYPE, OPEN_DEVICE_TYPE, TEMPERATURE_DEVICE_TYPE, SPEED_DEVICE_TYPE
from .mysql import MySQL

@tool
def get_room_info(rooms: List[str]) -> dict:
    """
    Function:
        Query the device information of given rooms.
    Input:
        rooms (List[str]): list of valid room names, each value must be one of ["balcony", "livingroom", "kitchen", "bathroom", "cloakroom", "masterbedroom", "guestbedroom"].
    Output (JSON):
        {
            "room_info": [
                {
                    "room": "livingroom",
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

@tool
def turn_on(device_type: str, room: str) -> dict:
    """
    Function:
        Turn on a specified device in a given room.
    Input:
        device_type (str): must be one of ["air_conditioner", "air_purifier", "bath_heater", "cooker_hood", "fan", "gas_stove", "heater", "humidifier", "light", "microwave_oven", "television", "towel_dryer", "washing_machine", "water_heater"]
        room (str): room name, e.g. "livingroom", "kitchen"
    Output (JSON):
        {
            "message": "execution result"
        }
    """
    if device_type not in TURN_ON_DEVICE_TYPE:
        return {"message": f"{device_type} is not a valid device_type, must be one of {TURN_ON_DEVICE_TYPE}"}
    if room not in DEFAULT_ROOMS:
        return {"message": f"{room} is not a valid room, must be one of {DEFAULT_ROOMS}"}
    mysql = MySQL()
    message = mysql.turn_on(device_type, room)
    mysql.close_client()
    return {"message": message} 

@tool
def turn_off(device_type: str, room: str) -> dict:
    """
    Function:
        Turn off a specified device in a given room.
    Input:
        device_type (str): must be one of ["air_conditioner", "air_purifier", "bath_heater", "cooker_hood", "fan", "gas_stove", "heater", "humidifier", "light", "microwave_oven", "television", "towel_dryer", "washing_machine", "water_heater"]
        room (str): room name, e.g. "livingroom", "kitchen"
    Output (JSON):
        {
            "message": "execution result"
        }
    """
    if device_type not in TURN_ON_DEVICE_TYPE:
        return {"message": f"{device_type} is not a valid device_type, must be one of {TURN_ON_DEVICE_TYPE}"}
    if room not in DEFAULT_ROOMS:
        return {"message": f"{room} is not a valid room, must be one of {DEFAULT_ROOMS}"}
    mysql = MySQL()
    message = mysql.turn_off(device_type, room)
    mysql.close_client()
    return {"message": message} 

@tool
def open(device_type: str, room: str) -> dict:
    """
    Function:
        Open a specified device in a given room.
    Input:
        device_type (str): must be one of ["window", "door", "curtain"]
        room (str): room name, e.g. "livingroom", "kitchen"
    Output (JSON):
        {
            "message": "execution result"
        }
    """
    if device_type not in OPEN_DEVICE_TYPE:
        return {"message": f"{device_type} is not a valid device_type, must be one of {OPEN_DEVICE_TYPE}"}
    if room not in DEFAULT_ROOMS:
        return {"message": f"{room} is not a valid room, must be one of {DEFAULT_ROOMS}"}
    mysql = MySQL()
    message = mysql.open(device_type, room)
    mysql.close_client()
    return {"message": message} 

@tool
def close(device_type: str, room: str) -> dict:
    """
    Function:
        Close a specified device in a given room.
    Input:
        device_type (str): must be one of ["window", "door", "curtain"]
        room (str): room name, e.g. "livingroom", "kitchen"
    Output (JSON):
        {
            "message": "execution result"
        }
    """
    if device_type not in OPEN_DEVICE_TYPE:
        return {"message": f"{device_type} is not a valid device_type, must be one of {OPEN_DEVICE_TYPE}"}
    if room not in DEFAULT_ROOMS:
        return {"message": f"{room} is not a valid room, must be one of {DEFAULT_ROOMS}"}
    mysql = MySQL()
    message = mysql.close(device_type, room)
    mysql.close_client()
    return {"message": message} 

@tool
def set_temperature(device_type: str, room: str, temperature: int) -> dict:
    """
    Function:
        Set the temperature of a specified device in a given room.
    Input:
        device_type (str): must be one of ["air_conditioner", "bath_heater"]
        room (str): room name, e.g. "livingroom", "bedroom"
        temperature (int): target temperature value
    Output (JSON):
        {
            "message": "execution result"
        }
    """
    if device_type not in TEMPERATURE_DEVICE_TYPE:
        return {"message": f"{device_type} is not a valid device_type, must be one of {TEMPERATURE_DEVICE_TYPE}"}
    if room not in DEFAULT_ROOMS:
        return {"message": f"{room} is not a valid room, must be one of {DEFAULT_ROOMS}"}
    mysql = MySQL()
    message = mysql.set_temperature(device_type, room, temperature)
    mysql.close_client()
    return {"message": message} 

@tool
def set_speed(device_type: str, room: str, speed: int) -> dict:
    """
    Function:
        Set the speed of a specified device in a given room.
    Input:
        device_type (str): must be one of ["air_conditioner", "cooker_hood", "fan"]
        room (str): room name, e.g. "livingroom", "bedroom"
        speed (int): must be in [1, 2, 3]
    Output (JSON):
        {
            "message": "execution result"
        }
    """
    if device_type not in SPEED_DEVICE_TYPE:
        return {"message": f"{device_type} is not a valid device_type, must be one of {SPEED_DEVICE_TYPE}"}
    if room not in DEFAULT_ROOMS:
        return {"message": f"{room} is not a valid room, must be one of {DEFAULT_ROOMS}"}
    if speed < 1 or speed > 3:
        return {"message": f"{speed} is not a valid speed, must be in [1, 2, 3]"}
    mysql = MySQL()
    message = mysql.set_speed(device_type, room, speed)
    mysql.close_client()
    return {"message": message} 

tools = [get_room_info, turn_on, turn_off, open, close, set_temperature, set_speed]