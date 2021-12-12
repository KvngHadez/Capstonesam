from typing import Optional
import asyncio
import platform
from datetime import datetime
from typing import Callable, Any

from aioconsole import ainput
from bleak import BleakClient, discover

from fastapi import FastAPI
from pydantic import BaseModel

read_characteristic = "00001143-0000-1000-8000-00805f9b34fb"
write_characteristic = "0000FFF3-0000-1000-8000-00805f9b34fb"


app = FastAPI()

class Item(BaseModel):
    distance: str
    time: str
    direction: str

@app.post("/items/")
async def create_item(item: Item):
    global in_dis
    global in_time
    global in_dir
    global loop
    loop = asyncio.get_event_loop()
    in_dis = item.distance
    in_time = item.time
    in_dir = item.direction
    connection = Connection(
        loop, read_characteristic, write_characteristic)
    asyncio.ensure_future(connection.manager())
    asyncio.ensure_future(user_console_manager(connection))
    asyncio.ensure_future(connection.cleanup())
    return in_dis + in_time + in_dir

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
        print("Bluetooth LE hardware warming up...")
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
            if 13 in manudata :
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


#############
# Loops
#############
async def user_console_manager(connection: Connection):
    i = 0
    while i == 0:
        if connection.client and connection.connected:
            input_str = in_dis + in_time + "0" + in_dir
            print(input_str)

            await connection.client.write_gatt_char(write_characteristic, bytes.fromhex(input_str))
            print(f"Sent: {input_str}")
            i = i + 1
        else:
            await asyncio.sleep(2.0, loop=loop)


#async def main():
#    while True:
#        # YOUR APP CODE WOULD GO HERE.
#        await asyncio.sleep(5)

