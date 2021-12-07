import json
import os, sys
import asyncio
import platform
from datetime import datetime
from typing import Callable, Any

from aioconsole import ainput
from bleak import BleakClient, discover

read_characteristic = "00002A38-0000-1000-8000-00805f9b34fb"
write_characteristic = "00002A37-0000-1000-8000-00805f9b34fb"

root_path = os.environ["HOME"]
output_file = f"{root_path}/Desktop/dump.csv"

HEADERS = {'Access-Control-Allow-Headers': 'Content-Type',
           'Access-Control-Allow-Origin': '*',
           'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'}

loop = asyncio.get_event_loop()

# import requests

def handle_exception(status, error_data):
    """
    Exception handler for endpoints. 
    Use this in except block or return statement to return relvent error 
    message to the client
    :param int status: HTTP status code to send back. Default 500
    :param str error_data: Error data to send back
    """
    return {
        "statusCode": status,
        'headers': HEADERS,
        "body": json.dumps(error_data, indent=2),
    }


def lambda_handler(event, context):

    if(event['body'] == None):
       return handle_exception(405, {"message" : "You have given us any information"})
    else: 
        if (event['httpMethod'] == 'POST'):
                event_body = json.loads(event['body'])
                return post(event_body)
        else:
                return handle_exception(405, {"message": "Method not allowed."})

def post(event_body):
    class Connection:
    
        client: BleakClient = None
        
        def __init__(
            self,
            loop: asyncio.AbstractEventLoop,
            read_characteristic: str,
            write_characteristic: str,
            #data_dump_handler: Callable[[str, Any], None],
            #data_dump_size: int = 256,
        ):
            self.loop = loop
            self.read_characteristic = read_characteristic
            self.write_characteristic = write_characteristic
            #self.data_dump_handler = data_dump_handler

            self.last_packet_time = datetime.now()
            #self.dump_size = data_dump_size
            self.connected = False
            self.connected_device = None

            self.rx_data = []
            self.rx_timestamps = []
            self.rx_delays = []

        def on_disconnect(self, client: BleakClient, future: asyncio.Future):
            self.connected = False
            # Put code here to handle what happens on disconnet.
            print(f"Disconnected from {self.connected_device.name}!")

        async def cleanup(self):
            if self.client:
                await self.client.stop_notify(read_characteristic)
                await self.client.disconnect()

        async def manager(self):
            print("Starting connection manager.")
            while True:
                if self.client:
                    await self.connect()
                else:
                    await self.select_device()
                    await asyncio.sleep(15.0, loop=loop)       

        async def connect(self):
            if self.connected:
                return
            try:
                await self.client.connect()
                self.connected = await self.client.is_connected()
                if self.connected:
                    print(F"Connected to {self.connected_device.name}")
                    self.client.set_disconnected_callback(self.on_disconnect)
                    print(f"set_disconnected")
                    #await self.client.start_notify(
                    #    self.read_characteristic, self.notification_handler,
                    #)
                    #print(f"start_notify")
                    while True:
                        if not self.connected:
                            break
                        await asyncio.sleep(3.0, loop=loop)
                else:
                    print(f"Failed to connect to {self.connected_device.name}")
            except Exception as e:
                print(e)

        async def select_device(self):
            print("Bluetooh LE hardware warming up...")
            await asyncio.sleep(2.0, loop=loop) # Wait for BLE to initialize.
            devices = await discover()

            # print("Please select device: ")
            diction = []
            num = 0
            for i, device in enumerate(devices):
                print(f"{i}: {device.name}")
                manudata = device.metadata["manufacturer_data"].keys()
                uuids = device.metadata["uuids"]
                print(uuids)
                print(manudata)
                if "Polar HR Sensor" == device.name :
                    break
            
            self.connected_device = device
            self.client = BleakClient(device.address, loop=self.loop)
            

            # response = -1
            # while True:
            #     response = await ainput("Select device: ")
            #     try:
            #         response = int(response.strip())
            #     except:
            #         print("Please make valid selection.")
                
            #     if response > -1 and response < len(devices):
            #         break
            #     else:
            #         print("Please make valid selection.")

        


        def record_time_info(self):
            present_time = datetime.now()
            self.rx_timestamps.append(present_time)
            self.rx_delays.append((present_time - self.last_packet_time).microseconds)
            self.last_packet_time = present_time

        def clear_lists(self):
            self.rx_data.clear()
            self.rx_delays.clear()
            self.rx_timestamps.clear()

        def notification_handler(self, sender: str, data: Any):
            self.rx_data.append(int.from_bytes(data, byteorder="big"))
            self.record_time_info()
            if len(self.rx_data) >= self.dump_size:
                self.data_dump_handler(self.rx_data, self.rx_timestamps, self.rx_delays)
                self.clear_lists()
    
    async def user_console_manager(connection: Connection):
        while True:
            if connection.client and connection.connected:
                #input_str = await ainput("Enter string: ")
                #bytes_to_send = hex(int(event_body['distance'], 16))
                #print(bytes_to_send)
                #finalbytes = bytearray(map(ord, bytes_to_send))
                input = event_body['distance'] + event_body['direction'] + "0" +event_body['time']
                await connection.client.write_gatt_char(write_characteristic, bytes.fromhex(input))
                print(f"Sent: {event_body['distance']}")
            else:
                await asyncio.sleep(2.0, loop=loop)

    connection = Connection(
        loop, read_characteristic, write_characteristic
    )

    #print(connection.write_characteristic)
    try:
        asyncio.ensure_future(connection.manager())
        asyncio.ensure_future(user_console_manager(connection))
        asyncio.sleep(5)
        return {
                    "statusCode": 200,
                    'headers': HEADERS,
                    "body": json.dumps({"distance": event_body['distance'], "time":event_body['time'], "direction":event_body['direction']}, indent=2),
            }
    except KeyboardInterrupt:
        print()
        print("User stopped program.")
        return handle_exception(405, {"message": "Your missing an input"})
    finally:
        print("Disconnecting...")
        loop.run_until_complete(connection.cleanup())
        return handle_exception(405, {"message": "Disconnecting"})
