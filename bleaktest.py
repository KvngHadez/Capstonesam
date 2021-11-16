import asyncio
from bleak import BleakScanner

async def main():
    devices = await BleakScanner.discover()
    for d in devices:
        print(d)

asyncio.run(main())


# import asyncio
# from bleak import BleakClient

# address = "00:5B:94:43:D7:62"
# MODEL_NBR_UUID = "104FC763-72F7-4C4E-A728-62743AE36E71"

# async def main(address):
#     async with BleakClient(address) as client:
#         model_number = await client.read_gatt_char(MODEL_NBR_UUID)
#         print("Model Number: {0}".format("".join(map(chr, model_number))))

# asyncio.run(main(address))
