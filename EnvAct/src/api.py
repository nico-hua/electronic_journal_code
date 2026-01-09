from .mysql import MySQL
from .config import DEFAULT_ROOMS, TURN_ON_DEVICE_TYPE, OPEN_DEVICE_TYPE, TEMPERATURE_DEVICE_TYPE, SPEED_DEVICE_TYPE
def turn_on(device_type: str, room: str) -> str:
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
        return f"{device_type} is not a valid device_type, must be one of {TURN_ON_DEVICE_TYPE}"
    if room not in DEFAULT_ROOMS:
        return f"{room} is not a valid room, must be one of {DEFAULT_ROOMS}"
    mysql = MySQL()
    message = mysql.turn_on(device_type, room)
    mysql.close_client()
    return message

def turn_off(device_type: str, room: str) -> str:
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
        return f"{device_type} is not a valid device_type, must be one of {TURN_ON_DEVICE_TYPE}"
    if room not in DEFAULT_ROOMS:
        return f"{room} is not a valid room, must be one of {DEFAULT_ROOMS}"
    mysql = MySQL()
    message = mysql.turn_off(device_type, room)
    mysql.close_client()
    return message

def open(device_type: str, room: str) -> str:
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
        return f"{device_type} is not a valid device_type, must be one of {OPEN_DEVICE_TYPE}"
    if room not in DEFAULT_ROOMS:
        return f"{room} is not a valid room, must be one of {DEFAULT_ROOMS}"
    mysql = MySQL()
    message = mysql.open(device_type, room)
    mysql.close_client()
    return message

def close(device_type: str, room: str) -> str:
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
        return f"{device_type} is not a valid device_type, must be one of {OPEN_DEVICE_TYPE}"
    if room not in DEFAULT_ROOMS:
        return f"{room} is not a valid room, must be one of {DEFAULT_ROOMS}"
    mysql = MySQL()
    message = mysql.close(device_type, room)
    mysql.close_client()
    return message

def set_temperature(device_type: str, room: str, temperature: int) -> str:
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
        return f"{device_type} is not a valid device_type, must be one of {TEMPERATURE_DEVICE_TYPE}"
    if room not in DEFAULT_ROOMS:
        return f"{room} is not a valid room, must be one of {DEFAULT_ROOMS}"
    mysql = MySQL()
    message = mysql.set_temperature(device_type, room, temperature)
    mysql.close_client()
    return message

def set_speed(device_type: str, room: str, speed: int) -> str:
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
        return f"{device_type} is not a valid device_type, must be one of {SPEED_DEVICE_TYPE}"
    if room not in DEFAULT_ROOMS:
        return f"{room} is not a valid room, must be one of {DEFAULT_ROOMS}"
    if speed < 1 or speed > 3:
        return f"{speed} is not a valid speed, must be in [1, 2, 3]"
    mysql = MySQL()
    message = mysql.set_speed(device_type, room, speed)
    mysql.close_client()
    return message