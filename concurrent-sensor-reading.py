import datetime
from zoneinfo import ZoneInfo

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
logger_1 = logging.getLogger('SHT30')
logger_2 = logging.getLogger('STEMMA')
logger_3 = logging.getLogger('Anemometer')
# Set the logging level for each of our concurrent functions to INFO.
logger_1.setLevel(logging.INFO)
logger_2.setLevel(logging.INFO)
logger_3.setLevel(logging.INFO)


async def read_temphum(sht30):
    while True:
        # Async sleep for 5 sec
        await asyncio.sleep(TEMP_INTERVAL)

        # Calculate temperature and humidity (SHT30)
        temp = ("Temperature: %0.3f C" % sht30.temperature)
        hum = ("Humidity: %0.3f%%" % sht30.relative_humidity)
        logger_1.info(f"{temp}\n{hum}\n")


async def read_soil(stemma):
    while True:
        # Async sleep for 6 sec
        await asyncio.sleep(SOIL_INTERVAL)

        # Calculate soil moisture and temperature (STEMMA)
        soil_m = ("Soil Moisture: %0.3f" % stemma.moisture_read())
        soil_t = ("Soil Temperature: %0.3f C" % stemma.get_temp())
        logger_2.info(f"{soil_m}\n{soil_t}\n")


async def read_wind(anem):
    while True:
        # Async sleep for 3 sec
        await asyncio.sleep(WIND_INTERVAL)

        # Calculate wind speed (Anemometer)
        wind_s = ("Wind Speed: %0.3f m/s" % ads_to_wind_speed(anem.voltage))
        logger_3.info(f"{wind_s}\n")


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