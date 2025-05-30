# Raspberry Pi Environmental Sensor Data Collection 🌲💧💨

This project details the setup and implementation of a Raspberry Pi 4-based system for collecting environmental data from various sensors. It explores different data acquisition methods, including serial polling and cooperative multitasking using Python's `asyncio` library. 

---
### Sensor Suite & Setup

The project utilized a Raspberry Pi 4 connected to the following sensors via a breadboard seen below:
* **[SHT30 Temperature and Humidity Sensor](https://www.adafruit.com/product/5064)**: Connected via I²C for ambient temperature and humidity readings.
* **[STEMMA Capacitive Soil Moisture Sensor](https://www.adafruit.com/product/4026)**: Measures soil moisture and temperature; connected via I²C.
* **[Anemometer (Wind Speed Sensor)](https://www.adafruit.com/product/1733)**: Requires a 7-24 VDC power supply. Its analog output is read using the ADS1015 ADC.
* **[ADS1015 12-Bit ADC Microcontroller](https://www.adafruit.com/product/1083)**: Converts analog signals to digital, interfacing with the Pi via I²C.

<div align="center">
  <img src="https://github.com/user-attachments/assets/a89565e9-e1f7-417e-9339-68aacbbe4cd7" width="400"/>
</div>

**Circuit Assembly**:
The Pi's GPIO pins were used for 3.3V power (Pin 1), shared ground (Pin 9), and I²C communication (SDA - Pin 3, SCL - Pin 5). I²C was chosen for its suitability for short-distance communication with multiple devices using only two pins. The `sudo i2cdetect -y 1` command was used to verify I²C connections, showing devices at addresses 0x44 (SHT30), 0x36 (STEMMA), and 0x48 (ADC).

---
### Data Collection Methods

Python was used for development, with CircuitPython libraries for sensor interaction.

#### 1. Serial Polling
This approach involved sequentially reading data from each sensor in a loop every 5 seconds. Sensor objects were initialized once, and then their respective methods were called to get readings.
* SHT30: `sht30.temperature`, `sht30.relative_humidity`.
* STEMMA: `stemma.moisture_read()`, `stemma.get_temp()`.
* Anemometer: Voltage read via `anem.voltage` (from ADS1015) and converted to m/s.

#### 2. Cooperative Multitasking with `asyncio`
This method uses asynchronous functions (`async def`) and `asyncio.sleep()` to manage sensor readings, giving the illusion of parallelism on a single core. It's beneficial for managing timers and waiting tasks without blocking.
* Three coroutines were defined, one for each sensor group (temp/humidity, soil, wind), each with its own polling interval.
* `asyncio.gather()` was used to run these coroutines concurrently.

**3: Cooperative Multitasking with Global Timer**
To ensure more synchronized readings and allow sensors to read at different frequencies based on a common timeline, a global timer coroutine was implemented.
* The timer increments every second.
* It uses a global list (`reg_vals`) to flag when each sensor should take a reading based on its specified interval (e.g., wind every 3s, temp/humidity every 5s, soil every 6s).
* Sensor coroutines loop, check their respective flag in `reg_vals`, read data if true, and then reset the flag. A small `asyncio.sleep(0.1)` was added in these loops to prevent blocking and allow other coroutines to run.
