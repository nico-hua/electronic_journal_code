MYSQL_CONFIG = {
    "host": "10.192.48.114",
    "port": 3306,
    "user": "root",
    "password": "123456",
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

DEFAULT_ROOMS = [
    "balcony",
    "livingroom",
    "kitchen",
    "bathroom",
    "cloakroom",
    "masterbedroom",  
    "guestbedroom"
]

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