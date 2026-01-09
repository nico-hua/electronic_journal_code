from .config import MYSQL_CONFIG, ROOM_MAP_DEVICE, ROOM_MAP_STATE
import pymysql

class MySQL:
    def __init__(self):
        self.device_client = pymysql.connect(
            host=MYSQL_CONFIG['host'],
            port=MYSQL_CONFIG['port'],
            user=MYSQL_CONFIG['user'],
            password=MYSQL_CONFIG['password'],
            database=MYSQL_CONFIG['device_database'],
            cursorclass=pymysql.cursors.DictCursor
        )
        self.state_client = pymysql.connect(
            host=MYSQL_CONFIG['host'],
            port=MYSQL_CONFIG['port'],
            user=MYSQL_CONFIG['user'],
            password=MYSQL_CONFIG['password'],
            database=MYSQL_CONFIG['state_database'],
            cursorclass=pymysql.cursors.DictCursor
        )

    def get_room_info(self, room: str) -> dict:
        """
        查询指定房间的信息，包括环境信息和设备信息。
        返回格式:
        {
            "room": "livingroom",      # 房间名称
            "environment": [ ... ],    # 环境信息列表，如温度、湿度
            "devices": [ ... ]         # 设备信息列表，如灯、空调等
        }
        """
        result = {
            "room": room,
            "environment": self.get_environment_info(room),
            "devices": self.get_device_info(room)
        }
        return result
    
    def get_environment_info(self, room: str) -> list:
        """
        查询指定房间的环境信息。
        返回格式:
        [
            {
                "temperature": 25.0,    # 温度
            },
            {
                "humidity": 60.0        # 湿度
            }
        ]
        """
        states = ROOM_MAP_STATE[room]
        results = []
        with self.state_client.cursor() as cursor:
            for state in states:
                sql = f"SELECT * FROM `{state}` WHERE location=%s"
                cursor.execute(sql, (room,))
                result = cursor.fetchone()
                if result:
                    results.append(result)
        return results
            
    
    def get_device_info(self, room: str) -> list:
        """
        查询指定房间的设备信息。
        返回格式:
        [
            {
                "name": "light",       # 设备名称
                "status": "ON"         # 设备状态
            },
            {
                "name": "ac",
                "status": "OFF"
            }
        ]
        """
        devices = ROOM_MAP_DEVICE[room]
        results = []
        with self.device_client.cursor() as cursor:
            for device in devices:
                if device == 'window':
                    sql = "SELECT * FROM windows WHERE location=%s"
                else:
                    sql = f"SELECT * FROM `{device}` WHERE location=%s"
                cursor.execute(sql, (room,))
                result = cursor.fetchone()
                if result:
                    results.append(result)
        return results
    
    def get_context(self) -> list:
        """
        查询外部的环境信息。
        返回格式:
        [
            {
                "temperature": 25.0,    # 温度
            },
            {
                "humidity": 60.0        # 湿度
            }
        ]
        """
        states = ROOM_MAP_STATE['context']
        results = []
        with self.state_client.cursor() as cursor:
            for state in states:
                sql = f"SELECT * FROM `{state}` WHERE location=%s"
                cursor.execute(sql, ("context",))
                result = cursor.fetchone()
                if result:
                    results.append(result)
        return results
    
    def turn_on(self, device_type: str, room: str) -> str:
        """
        开启设备
        """
        with self.device_client.cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) FROM {device_type} WHERE location=%s", (room,))
            count = cursor.fetchone()['COUNT(*)']
            if count == 0:
                return f"{room} does not exist {device_type}"
            cursor.execute(f"UPDATE {device_type} SET status='ON' WHERE location=%s", (room,))
        self.device_client.commit()
        print(f"{device_type} in {room} turned on successfully")
        return "success"
    
    def turn_off(self, device_type: str, room: str) -> str:
        """
        关闭设备
        """
        with self.device_client.cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) FROM {device_type} WHERE location=%s", (room,))
            count = cursor.fetchone()['COUNT(*)']
            if count == 0:
                return f"{room} does not exist {device_type}"
            cursor.execute(f"UPDATE {device_type} SET status='OFF' WHERE location=%s", (room,))
        self.device_client.commit()
        print(f"{device_type} in {room} turned off successfully")
        return "success"
    
    def open(self, device_type: str, room: str) -> str:
        """
        打开设备
        """
        with self.device_client.cursor() as cursor:
            if device_type == 'window':
                cursor.execute(f"SELECT COUNT(*) FROM windows WHERE location=%s", (room,))
            else:
                cursor.execute(f"SELECT COUNT(*) FROM {device_type} WHERE location=%s", (room,))
            count = cursor.fetchone()['COUNT(*)']
            if count == 0:
                return f"{room} does not exist {device_type}"
            if device_type == 'window':
                cursor.execute(f"UPDATE windows SET status='OPEN' WHERE location=%s", (room,))
            else:
                cursor.execute(f"UPDATE {device_type} SET status='OPEN' WHERE location=%s", (room,))
        self.device_client.commit()
        print(f"{device_type} in {room} opened successfully")
        return "success"
    
    def close(self, device_type: str, room: str) -> str:
        """
        关上设备
        """
        with self.device_client.cursor() as cursor:
            if device_type == 'window':
                cursor.execute(f"SELECT COUNT(*) FROM windows WHERE location=%s", (room,))
            else:
                cursor.execute(f"SELECT COUNT(*) FROM {device_type} WHERE location=%s", (room,))
            count = cursor.fetchone()['COUNT(*)']
            if count == 0:
                return f"{room} does not exist {device_type}"
            if device_type == 'window':
                cursor.execute(f"UPDATE windows SET status='CLOSED' WHERE location=%s", (room,))
            else:
                cursor.execute(f"UPDATE {device_type} SET status='CLOSED' WHERE location=%s", (room,))
        self.device_client.commit()
        print(f"{device_type} in {room} closed successfully")
        return "success"
    
    def set_temperature(self, device_type: str, room: str, temperature: int) -> str:
        """
        设置温度
        """
        with self.device_client.cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) FROM {device_type} WHERE location=%s", (room,))
            count = cursor.fetchone()['COUNT(*)']
            if count == 0:
                return f"{room} does not exist {device_type}"
            cursor.execute(f"UPDATE {device_type} SET temperature=%s WHERE location=%s", (temperature, room))
        self.device_client.commit()
        print(f"temperature of {device_type} in {room} seted to {temperature}°C successfully")
        return "success"
    
    def set_speed(self, device_type: str, room: str, speed: int) -> str:
        """
        设置速率
        """
        with self.device_client.cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) FROM {device_type} WHERE location=%s", (room,))
            count = cursor.fetchone()['COUNT(*)']
            if count == 0:
                return f"{room} does not exist {device_type}"
            cursor.execute(f"UPDATE {device_type} SET speed=%s WHERE location=%s", (speed, room))
        self.device_client.commit()
        print(f"speed of {device_type} in {room} seted to {speed} successfully")
        return "success"
    
    def get_status(self, device_type: str, room: str, field: str):
        """
        查询状态信息
        """
        try:
            with self.device_client.cursor() as cursor:
                if device_type == "window":
                    cursor.execute(f"SELECT {field} FROM windows WHERE location=%s", (room,))
                else:
                    cursor.execute(f"SELECT {field} FROM {device_type} WHERE location=%s", (room,))
                result = cursor.fetchone()
                if result is None:
                    return None
                return result[field] 
        except Exception as e:
            print(f"Error getting status for {device_type} in {room}: {e}")
            return None
        
    def get_env_state(self, state_type: str, room: str, field: str):
        try:
            with self.state_client.cursor() as cursor:
                cursor.execute(f"SELECT {field} FROM {state_type} WHERE location=%s", (room,))
                result = cursor.fetchone()
                if result is None:
                    return None
                return result[field]
        except Exception as e:
            print(f"Error getting status for {state_type} in {room}: {e}")
            return None
            
    def close_client(self):
        """ 关闭数据库连接 """
        self.device_client.close()
        self.state_client.close()