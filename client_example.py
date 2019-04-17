import rov_comm
import datetime
import ast

CLIENT_PORT = 1234
DRIVER_PORT = 1235

driver = rov_comm.Client(DRIVER_PORT)
client = rov_comm.Client(CLIENT_PORT)

if not (driver.connection_on is True and client.connection_on is True):
    print("server down")
else:
    while True:
        driver.send_data({'A':1,'B':2})
        data = client.get_data()
        data = data.decode("utf-8")
        data = ast.literal_eval(data)
        #print(type(data))

print("Goodbye")
