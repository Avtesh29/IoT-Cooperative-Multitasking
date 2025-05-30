from datetime import datetime
from zoneinfo import ZoneInfo
import time

import board
import adafruit_sht31d
import adafruit_ads1x15.ads1015 as ADS

from adafruit_seesaw.seesaw import Seesaw
from adafruit_ads1x15.analog_in import AnalogIn
from simpleio import map_range


def ads_to_wind_speed(voltage_val):
    # Convert ADS voltage to wind speed m/s
    return map_range(voltage_val, 0.4, 2, 0, 32.4)


def main():
    with open('polling-log.txt', 'w') as outfile:
        outfile.write("Avtesh Singh\n")

    # Create sensor object, communicating over the board's default I2C bus
    i2c = board.I2C()  # uses board.SCL and board.SDA

    sht30 = adafruit_sht31d.SHT31D(i2c)     # SHT30
    stemma = Seesaw(i2c, addr=0x36)         # STEMMA
    ads = ADS.ADS1015(i2c)                  # ADS
    # ads.gain = 2                            # +- 2.048 V
    anem = AnalogIn(ads, ADS.P0)            # Anemometer

    while True:
        # Get and format current date information
        current_datetime = datetime.now(ZoneInfo("America/Los_Angeles"))
        formatted_datetime = current_datetime.strftime("%m-%d-%Y %H:%M:%S")

        # Calculate temperature and humidity (SHT30)
        temp = ("Temperature: %0.3f C" % sht30.temperature)
        hum = ("Humidity: %0.3f%%" % sht30.relative_humidity)

        # Calculate soil moisture and temperature (STEMMA)
        soil_m = ("Soil Moisture: %0.3f" % stemma.moisture_read())
        soil_t = ("Soil Temperature: %0.3f C" % stemma.get_temp())
        
        # Calculate wind speed (Anemometer)
        wind_s = ("Wind Speed: %0.3f m/s" % ads_to_wind_speed(anem.voltage))
        # print(anem.voltage, anem.value)

        with open('polling-log.txt', 'a') as outfile:
            outfile.write(f"{formatted_datetime}\n{temp}\n{hum}\n{soil_m}\n{soil_t}\n{wind_s}\n\n")

        time.sleep(5)


if __name__ == "__main__":
    # Run async main and catch Keyboard Interrupt
    try: 
        main()
    except KeyboardInterrupt:
        print("\nExiting program...")
        exit(0)