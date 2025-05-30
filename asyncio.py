import datetime
from zoneinfo import ZoneInfo

import sys
import asyncio
import logging
import board
import adafruit_sht31d
import adafruit_ads1x15.ads1015 as ADS

from adafruit_seesaw.seesaw import Seesaw
from adafruit_ads1x15.analog_in import AnalogIn
from simpleio import map_range

TEMP_INTERVAL = 5
SOIL_INTERVAL = 6
WIND_INTERVAL = 3

'''
ASYNCIO LOGGING FROM EXAMPLE
'''
# Setting up our default logging format.
logging.basicConfig(format='[%(asctime)s] (%(name)s) %(levelname)s:\n%(message)s',)
# Set up loggers for each of our concurrent functions.
logger_1 = logging.getLogger('Temp/Hum')
logger_2 = logging.getLogger('Soil')
logger_3 = logging.getLogger('Wind')
# Set the logging level for each of our concurrent functions to INFO.
logger_1.setLevel(logging.INFO)
logger_2.setLevel(logging.INFO)
logger_3.setLevel(logging.INFO)


# Register values init to False
# 0 -> SHT30, 1 -> STEMMA, 2 -> Anemometer
reg_vals = [False] * 3


# Timer function, async sleeps 1 second at a time and checks total elapsed time
async def timer():
    time = 0        # Start timer at 0
    while True:
        # Don't immediately log at t = 0
        if time != 0:
            if time % WIND_INTERVAL == 0:
                reg_vals[2] = True          # Anemometer (3s)
            if time % TEMP_INTERVAL == 0:
                reg_vals[0] = True          # SHT30 (5s)
            if time % SOIL_INTERVAL == 0: 
                reg_vals[1] = True          # STEMMA (6s)
        # Async sleep 1 second and increment time
        await asyncio.sleep(1)
        time += 1
        # Handle integer getting too large -> reset back to interval LCM
        if time == 300:
            time = 30
            

async def read_temphum(sht30):
    while True:
        # Check register values
        if reg_vals[0] == True:
            # Calculate temperature and humidity (SHT30)
            temp = ("Temperature: %0.3f C" % sht30.temperature)
            hum = ("Humidity: %0.3f%%" % sht30.relative_humidity)
            logger_1.info(f"{temp}\n{hum}\n")
            reg_vals[0] = False
        # Added small wait to yield and prevent permanent loop
        await asyncio.sleep(0.1)


async def read_soil(stemma):
    while True:
        # Check register values
        if reg_vals[1] == True:
            # Calculate soil moisture and temperature (STEMMA)
            soil_m = ("Soil Moisture: %0.3f" % stemma.moisture_read())
            soil_t = ("Soil Temperature: %0.3f C" % stemma.get_temp())
            logger_2.info(f"{soil_m}\n{soil_t}\n")
            reg_vals[1] = False
        # Added small wait to yield and prevent permanent loop
        await asyncio.sleep(0.1)


async def read_wind(anem):
    while True:
        # Check register values
        if reg_vals[2] == True:
            # Calculate wind speed (Anemometer)
            wind_s = ("Wind Speed: %0.3f m/s" % ads_to_wind_speed(anem.voltage))
            logger_3.info(f"{wind_s}\n")
            reg_vals[2] = False
        # Added small wait to yield and prevent permanent loop
        await asyncio.sleep(0.1)


def ads_to_wind_speed(voltage_val):
    # Convert ADS voltage to wind speed m/s
    return map_range(voltage_val, 0.4, 2, 0, 32.4)


async def main():
    # Create sensor object, communicating over the board's default I2C bus
    i2c = board.I2C()  # uses board.SCL and board.SDA

    sht30 = adafruit_sht31d.SHT31D(i2c)     # SHT30
    stemma = Seesaw(i2c, addr=0x36)         # STEMMA
    ads = ADS.ADS1015(i2c)                  # ADS
    # ads.gain = 2                            # +- 2.048 V
    anem = AnalogIn(ads, ADS.P0)            # Anemometer

    await asyncio.gather(
        timer(),
        read_temphum(sht30),
        read_soil(stemma),
        read_wind(anem)
    )
        

if __name__ == "__main__":
    # Run async main and catch Keyboard Interrupt
    try: 
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting program...")
        exit(0)