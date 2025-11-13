import os

## Constant
# Specifies the IIO Base folder in Linux
IIO_BASE = "/sys/bus/iio/devices/"
DEVICE_INDEX = 1

## Helper Function
# Converts from Celsius to Fahrenheit.
def c_to_f(c:int):
    return c * 9 / 5 + 32

## Function to find a specific IIO Device
# Function currently only tests for a specific device and returns it
# Function will be replaced with proper parsing code in later versions
def find_iio_device():
    if not os.path.exists(IIO_BASE):
        raise FileNotFoundError(f"No IIO devices found at {IIO_BASE}")
    devices = [d for d in os.listdir(IIO_BASE) if d.startswith("iio:device")]
    if not devices:
        raise FileNotFoundError("No IIO devices detected")
    return os.path.join(IIO_BASE, devices[DEVICE_INDEX])

## Function to read various channels from an IIO Device
# Function will be replaced with proper parsing code in later versions
def read_channel(device_path, channel_name):
    channel_file = os.path.join(device_path, f"{channel_name}_input")
    if os.path.exists(channel_file):
        with open(channel_file) as f:
            value = f.read().strip()
        return value
    return None

## Function to parse data from the BME680 sensor
# Function will be replaced with proper parsing code in later versions
def parse_Data():
    device_path = ""

    try:
        device_path = find_iio_device()

    except FileNotFoundError:
        print("No IIO devices detected. Falling back to dummy data.")

        return {"Temperature": 120,
                "Humidity": 41.3,
                "Pressure": 1012.8,
                "Gas": 12000}

    channels = {
        "temperature": "in_temp",
        "humidity": "in_humidityrelative",
        "pressure": "in_pressure",
        "gas": "in_resistance",
    }

    data = {}
    print("=" * 40)
    for label, ch in channels.items():
        val = read_channel(device_path, ch)
        if val is not None:
            if ch == "in_temp":
                temp_c = float(val) / 1000.0  # m°C → °C
                data["Temperature"] = round(c_to_f(temp_c), 1)
                print(f"Temperature: {data['Temperature']} °F / {temp_c:.2f} °C")
            elif ch == "in_humidityrelative":
                data["Humidity"] = round(float(val) / 1000.0, 1)
                print(f"Humidity: {data['Humidity']} %")
            elif ch == "in_pressure":
                data["Pressure"] = round(float(val) / 100.0, 1)
                print(f"Pressure: {data['Pressure']} hPa")
            else:
                data["Gas"] = float(val)
                print(f"Gas: {data['Gas']} Ω")
        else:
            print(f"{label.capitalize()}: N/A")
    print("=" * 40)

    return data