MYSQL_CONFIG = {
    "host": "10.176.65.202",
    "port": 3306,
    "user": "root",
    "password": "123456a",
    "device_database": "smart_home_device",
    "state_database": "smart_home_state"
}

DEFAULT_ROOMS = [
    "balcony",
    "livingroom",
    "kitchen",
    "bathroom",
    "cloakroom",
    "masterbedroom",  
    "guestbedroom"
]

ROOM_MAP_DEVICE = {
    "balcony": [
        "light",
        "window",
        "door",
        "curtain",
        "washing_machine"
    ],
    "livingroom": [
        "air_conditioner",
        "air_purifier",
        "curtain",
        "door",
        "heater",
        "humidifier",
        "light",
        "window",
        "television",
        "fan"
    ],
    "kitchen": [
        "cooker_hood",
        "gas_stove",
        "microwave_oven",
        "window",
        "door",
        "light",
        "curtain"
    ],
    "bathroom": [
        "light",
        "door",
        "towel_dryer",
        "water_heater",
        "bath_heater"
    ],
    "cloakroom": [
        "door",
        "light"
    ],
    "masterbedroom": [   
        "air_conditioner",
        "window",
        "door",
        "humidifier",
        "air_purifier",
        "heater",
        "curtain",
        "light",
        "fan"
    ],
    "guestbedroom": [   
        "light",
        "television",
        "air_conditioner",
        "window",
        "door",
        "humidifier",
        "air_purifier",
        "heater",
        "curtain",
        "fan"
    ]
}

DEVICE_MAP_ROOM = {
    "light": [
        "balcony",
        "livingroom",
        "kitchen",
        "bathroom",
        "cloakroom",
        "masterbedroom",
        "guestbedroom"
    ],
    "window": [
        "balcony",
        "livingroom",
        "kitchen",
        "masterbedroom",
        "guestbedroom"
    ],
    "door": [
        "balcony",
        "livingroom",
        "kitchen",
        "bathroom",
        "cloakroom",
        "masterbedroom",
        "guestbedroom"
    ],
    "curtain": [
        "balcony",
        "livingroom",
        "kitchen",
        "masterbedroom",
        "guestbedroom"
    ],
    "washing_machine": [
        "balcony"
    ],
    "air_conditioner": [
        "livingroom",
        "masterbedroom",
        "guestbedroom"
    ],
    "air_purifier": [
        "livingroom",
        "masterbedroom",
        "guestbedroom"
    ],
    "heater": [
        "livingroom",
        "masterbedroom",
        "guestbedroom"
    ],
    "humidifier": [
        "livingroom",
        "masterbedroom",
        "guestbedroom"
    ],
    "television": [
        "livingroom",
        "guestbedroom"
    ],
    "cooker_hood": [
        "kitchen"
    ],
    "gas_stove": [
        "kitchen"
    ],
    "microwave_oven": [
        "kitchen"
    ],
    "towel_dryer": [
        "bathroom"
    ],
    "water_heater": [
        "bathroom"
    ],
    "bath_heater": [
        "bathroom"
    ],
    "fan": [
        "livingroom",
        "masterbedroom",
        "guestbedroom"
    ]
}

TURN_ON_DEVICE_TYPE = [
    "air_conditioner",
    "air_purifier",
    "bath_heater",
    "cooker_hood",
    "fan",
    "gas_stove",
    "heater",
    "humidifier",
    "light",
    "microwave_oven",
    "television",
    "towel_dryer",
    "washing_machine",
    "water_heater"
]

OPEN_DEVICE_TYPE = [
    "window",
    "door",
    "curtain"
]

TEMPERATURE_DEVICE_TYPE = [
    "air_conditioner",
    "bath_heater"
]

SPEED_DEVICE_TYPE = [
    "air_conditioner",
    "cooker_hood",
    "fan"
]

ROOM_MAP_STATE = {
    "balcony": [
        "noise",
        "temperature",
        "brightness",
        "humidity",
        "air_quality"
    ],
    "livingroom": [
        "noise",
        "ultraviolet_level",
        "temperature",
        "brightness",
        "humidity",
        "air_quality",
    ],
    "kitchen": [
        "co_level",
        "temperature",
        "brightness",
        "humidity",
        "air_quality",
    ],
    "bathroom": [
        "temperature",
        "brightness",
        "humidity",
        "air_quality",
    ],
    "cloakroom": [
        "temperature",
        "brightness",
        "humidity",
        "air_quality"
    ],
    "masterbedroom": [  
        "noise",
        "ultraviolet_level",
        "temperature",
        "brightness",
        "humidity",
        "air_quality"
    ],
    "guestbedroom": [   
        "ultraviolet_level",
        "temperature",
        "brightness",
        "humidity",
        "air_quality",
        "noise"
    ],
    "context": [
        "temperature",
        "brightness",
        "humidity",
        "air_quality",
        "weather",
        "ultraviolet_level"
    ]
}

STATE_MAP_ROOM = {
    "noise": [
        "balcony",
        "livingroom",
        "masterbedroom",
        "guestbedroom"
    ],
    "temperature": [
        "balcony",
        "livingroom",
        "kitchen",
        "bathroom",
        "cloakroom",
        "masterbedroom",
        "guestbedroom",
        "context"
    ],
    "brightness": [
        "balcony",
        "livingroom",
        "kitchen",
        "bathroom",
        "cloakroom",
        "masterbedroom",
        "guestbedroom",
        "context"
    ],
    "humidity": [
        "balcony",
        "livingroom",
        "kitchen",
        "bathroom",
        "cloakroom",
        "masterbedroom",
        "guestbedroom",
        "context"
    ],
    "air_quality": [
        "balcony",
        "livingroom",
        "kitchen",
        "bathroom",
        "cloakroom",
        "masterbedroom",
        "guestbedroom",
        "context"
    ],
    "ultraviolet_level": [
        "livingroom",
        "masterbedroom",
        "guestbedroom",
        "context"
    ],
    "co_level": [
        "kitchen"
    ],
    "weather": [
        "context"
    ]
}