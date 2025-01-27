import asyncio
from bleak import BleakScanner, BleakClient
import  struct
import pandas as pd
from datetime import datetime
import logging
logging.basicConfig(level=logging.INfO)
logger =  logging.getlogger(__name__)

class BeaconXProW6Scanner:
    def __init__(self):
        self.known_devices = {}
        self.data_records = []
        
    async def scan_and_connect(self):
        try:
            logger.info("starting Beacon scannner ...")
            scanner =  BleakScanner()
            scanner.register_detection_callback(self.detection_callback)
            await scanner.start()
            await asyncio.sleep(5.0)
            await scanner.stop()
            
            for address,device_info in self.known_devices.items():
                logger.info(f"Found device: {device_info.device}")
                
                try:
                    async with BleakClient(address) as client:
                        logger.info(f"connected to {address}")
                        
                        manufacturer_data = await self.read_manufacturer_data(client)
                        logger.info(f"Manufacturer data: {manufacturer_data.manufacturer}")
                        sensor_data = await self.read_sensor_data(client)
                        logger.info(f"Sensor data: {sensor_data}")
                        self.store_data(address,manufacturer_data,sensor_data)
                except Exception as e:
                    logger.error(f"Failed to connect to {address}: {str(e)}")
        except 