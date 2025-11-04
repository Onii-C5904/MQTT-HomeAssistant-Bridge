import board
import busio
import adafruit_bme680
import json

i2c = None
sensor = None

def c_to_f(c):
    return c * 9 / 5 + 32


def initSensors() -> None:
    i2c = busio.I2C(board.SCL, board.SDA)

    sensor = adafruit_bme680.Adafruit_BME680_I2C(i2c)

    sensor.sea_level_pressure = 1013.25


def parseSensors() -> str:

    if sensor is None or i2c is None:
        print("Sensors and I2C not initialized!")
        return "exit"

    temp_f = c_to_f(sensor.temperature)

    print("=" * 40)
    print(f"Temperature: {temp_f:.1f} °F")
    print(f"Humidity:    {sensor.humidity:.1f} %")
    print(f"Pressure:    {sensor.pressure:.1f} hPa")
    print(f"Gas:         {sensor.gas} Ω")
    print(f"Altitude:    {sensor.altitude:.2f} m")
    print("=" * 40)

    return json.dumps(sensor.__dict__)
