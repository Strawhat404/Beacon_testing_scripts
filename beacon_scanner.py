import asyncio
from bleak import BleakScanner, BleakClient
import struct
import pandas as pd
from datetime import datetime
import logging
import aiohttp
import json


class BeaconBackendConnector:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.token = None
        
    async def authenticate(self):
        async with aiohttp.ClientSession() as session:
            auth_data = {
                "username": "your_username",
                "password": "your_password"
            }
            async with session.post(f"{self.base_url}/api/auth/login/", json=auth_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.token = data['tokens']['access']
                    return True
                return False

    async def send_beacon_data(self, data):
        if not self.token:
            await self.authenticate()
            
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/beacon/data/",
                headers=headers,
                json=data
            ) as response:
                return await response.json()
            
# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BeaconXProW6Scanner:
    def __init__(self):
        self.known_devices = {}
        self.data_records = []
        
    async def scan_and_connect(self):
        try:
            logger.info("Starting beacon scanner...")
            
            # Start scanning for devices
            scanner = BleakScanner()
            scanner.register_detection_callback(self.detection_callback)
            
            await scanner.start()
            await asyncio.sleep(5.0)  # Scan for 5 seconds
            await scanner.stop()
            
            # Print found devices
            for address, device_info in self.known_devices.items():
                logger.info(f"Found device: {device_info}")
                
                # Try to connect to each found device
                try:
                    async with BleakClient(address) as client:
                        logger.info(f"Connected to {address}")
                        
                        # Read device info
                        manufacturer_data = await self.read_manufacturer_data(client)
                        logger.info(f"Manufacturer data: {manufacturer_data}")
                        
                        # Read sensor data
                        sensor_data = await self.read_sensor_data(client)
                        logger.info(f"Sensor data: {sensor_data}")
                        
                        # Store data
                        self.store_data(address, manufacturer_data, sensor_data)
                        
                except Exception as e:
                    logger.error(f"Failed to connect to {address}: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Scanning error: {str(e)}")

    async def detection_callback(self, device, advertisement_data):
        if device.address not in self.known_devices:
            # Checking if it's a MokoSmart device
            if self.is_mokosmart_device(advertisement_data):
                logger.info(f"Found MokoSmart device: {device.address}")
                self.known_devices[device.address] = {
                    'name': device.name or 'Unknown',
                    'rssi': device.rssi,
                    'address': device.address
                }

    def is_mokosmart_device(self, advertisement_data):
        # Check manufacturer data for MokoSmart identifier
        
        manufacturer_id = 0x0059  # actual MokoSmart ID
        if advertisement_data.manufacturer_data:
            return manufacturer_id in advertisement_data.manufacturer_data
        return False

    async def read_manufacturer_data(self, client):
        # Read manufacturer-specific data
       
        manufacturer_char_uuid = "0000180A-0000-1000-8000-00805F9B34FB"
        try:
            manufacturer_data = await client.read_gatt_char(manufacturer_char_uuid)
            return self.parse_manufacturer_data(manufacturer_data)
        except Exception as e:
            logger.error(f"Error reading manufacturer data: {str(e)}")
            return None

    async def read_sensor_data(self, client):
        # Read sensor data
       
        sensor_char_uuid = "0000180F-0000-1000-8000-00805F9B34FB"
        try:
            sensor_data = await client.read_gatt_char(sensor_char_uuid)
            return self.parse_sensor_data(sensor_data)
        except Exception as e:
            logger.error(f"Error reading sensor data: {str(e)}")
            return None

    def parse_manufacturer_data(self, data):
        # Parse manufacturer data according to W6 specification
        
        try:
            return {
                'raw_data': data.hex(),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error parsing manufacturer data: {str(e)}")
            return None

    def parse_sensor_data(self, data):
        # Parse sensor data according to W6 specification
       
        try:
            return {
                'raw_data': data.hex(),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error parsing sensor data: {str(e)}")
            return None

    def store_data(self, address, manufacturer_data, sensor_data):
        record = {
            'timestamp': datetime.now().isoformat(),
            'device_address': address,
            'manufacturer_data': manufacturer_data,
            'sensor_data': sensor_data
        }
        self.data_records.append(record)
        
        # this saves to csv format
        try:
            df = pd.DataFrame(self.data_records)
            df.to_csv('beacon_data.csv', index=False)
            logger.info(f"Data saved to beacon_data.csv")
        except Exception as e:
            logger.error(f"Error saving data: {str(e)}")

async def main():
    scanner = BeaconXProW6Scanner()
    while True:
        await scanner.scan_and_connect()
        await asyncio.sleep(1)  # Wait 1 second between scans

if __name__ == "__main__":
    asyncio.run(main())