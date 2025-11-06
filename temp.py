#!/usr/bin/env python3

'''
11/4/2025
Dan Howard

Modified by Kristijan Stojanovski

Parses data from an iio device
'''
import os

IIO_BASE = "/sys/bus/iio/devices/"

device_path = ""

channels = {
        "Temperature": "in_temp",
        "Humidity": "in_humidityrelative",
        "Pressure": "in_pressure",
        "Gas": "in_resistance",
    }


def c_to_f(c):
    return c * 9 / 5 + 32


def find_iio_device():
    if not os.path.exists(IIO_BASE):
        raise FileNotFoundError(f"No IIO devices found at {IIO_BASE}")
    devices = [d for d in os.listdir(IIO_BASE) if d.startswith("iio:device")]
    if not devices:
        raise FileNotFoundError("No IIO devices detected")
    return os.path.join(IIO_BASE, devices[0])

def read_channel(device_path, channel_name):
    channel_file = os.path.join(device_path, f"{channel_name}_input")
    if os.path.exists(channel_file):
        with open(channel_file) as f:
            value = int(f.read())
        return value
    return None


def init():
    try:
        device_path = find_iio_device()
    except FileNotFoundError:
        print("No IIO devices detected. Exiting.")
        return

def parse_Data() -> dict:
    payload = {}
    print("=" * 40)
    for label, ch in channels.items():
        val = read_channel(device_path, ch)
        if val is not None:
            if ch == "in_temp":
                temp_c = val / 1000.0  # m°C → °C
                print(f"{label}: {c_to_f(temp_c):.1f} °F / {temp_c:.2f} °C")
                payload[label] = c_to_f(temp_c)
            elif ch == "in_humidityrelative":
                print(f"{label}: {val / 1000.0:.1f} %")
                payload[label] = {f"{val / 1000.0:.1f} %"}
            elif ch == "in_pressure":
                print(f"{label}: {val / 100.0:.1f} hPa")
                payload[label] = {f"{val / 100.0:.1f} hPa"}
            else:
                print(f"{label}: {val}")
                payload[label] = val
        else:
            print(f"{label}: N/A")
            payload[label] = "N/A"

    print("=" * 40)

    # I hate my life

    return payload
