from src.mysql import MySQL

mysql = MySQL()
res = mysql.get_status("door", "livingroom", "status")
print(res)