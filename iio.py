import os

## Constant
# Specifies the IIO Base folder in Linux
IIO_BASE = "/sys/bus/iio/devices/"
IIO_META = {'in_intensity_sampling_frequency': (float, 1, None), 'in_voltageY_raw': ('mV', 1, 'voltage'), 'in_voltageY_supply_raw': ('mV', 1, 'voltage'), 'in_voltageY-voltageZ_raw': ('mV', 1, 'voltage'), 'in_altvoltageY_rms_raw': ('mV', 1, 'voltage'), 'in_powerY_raw': ('W', 0.001, 'power'), 'in_powerY_active_raw': ('W', 0.001, 'power'), 'in_powerY_reactive_raw': ('W', 0.001, 'reactive_power'), 'in_powerY_apparent_raw': ('W', 0.001, 'apparent_power'), 'in_powerY_powerfactor': ('W', 0.001, 'power_factor'), 'in_temp_raw': ('°C', 0.001, 'temperature'), 'in_tempY_raw': ('°C', 0.001, 'temperature'), 'in_temp_x_raw': ('°C', 0.001, 'temperature'), 'in_temp_y_raw': ('°C', 0.001, 'temperature'), 'in_temp_ambient_raw': ('°C', 0.001, 'temperature'), 'in_temp_object_raw': ('°C', 0.001, 'temperature'), 'in_tempY_input': ('°C', 0.001, 'temperature'), 'in_temp_input': ('°C', 0.001, 'temperature'), 'in_accel_x_raw': ('m/s', 1, None), 'in_accel_y_raw': ('m/s', 1, None), 'in_accel_z_raw': ('m/s', 1, None), 'in_accel_linear_x_raw': ('m/s', 1, None), 'in_accel_linear_y_raw': ('m/s', 1, None), 'in_accel_linear_z_raw': ('m/s', 1, None), 'in_gravity_x_raw': ('m/s', 1, None), 'in_gravity_y_raw': ('m/s', 1, None), 'in_gravity_z_raw': ('m/s', 1, None), 'in_deltaangl_x_raw': (float, 57.29577951308232, None), 'in_deltaangl_y_raw': (float, 57.29577951308232, None), 'in_deltaangl_z_raw': (float, 57.29577951308232, None), 'in_deltavelocity_x_raw': ('m/s', 1, None), 'in_deltavelocity_y_raw': ('m/s', 1, None), 'in_deltavelocity_z_raw': ('m/s', 1, None), 'in_angl_raw': (float, 57.29577951308232, None), 'in_anglY_raw': (float, 57.29577951308232, None), 'in_anglvel_x_raw': ('m/s', 57.29577951308232, None), 'in_anglvel_y_raw': ('m/s', 57.29577951308232, None), 'in_anglvel_z_raw': ('m/s', 57.29577951308232, None), 'in_incli_x_raw': (float, 1, None), 'in_incli_y_raw': (float, 1, None), 'in_incli_z_raw': (float, 1, None), 'in_magn_x_raw': (float, 1, None), 'in_magn_y_raw': (float, 1, None), 'in_magn_z_raw': (float, 1, None), 'in_accel_x_peak_raw': ('m/s', 1, None), 'in_accel_y_peak_raw': ('m/s', 1, None), 'in_accel_z_peak_raw': ('m/s', 1, None), 'in_humidityrelative_peak_raw': ('%', 1, 'humidity'), 'in_temp_peak_raw': ('°C', 0.001, 'temperature'), 'in_humidityrelative_trough_raw': ('%', 1, 'humidity'), 'in_temp_trough_raw': ('°C', 0.001, 'temperature'), 'in_accel_xyz_squared_peak_raw': ('m/s', 1, None), 'in_humidityrelative_raw': ('%', 1, 'humidity'), 'in_humidityrelative_input': ('%', 1, 'humidity'), 'in_Y_mean_raw': ('float', 1, None), 'in_activity_still_input': ('%', 1, None), 'in_activity_walking_input': ('%', 1, None), 'in_activity_jogging_input': ('%', 1, None), 'in_activity_running_input': ('%', 1, None), 'in_distance_input': ('m', 1, 'distance'), 'in_distance_raw': ('m', 1, 'distance'), 'in_proximity_raw': ('m', 1, 'distance'), 'in_proximity_input': ('m', 1, 'distance'), 'in_proximityY_raw': ('m', 1, 'distance'), 'in_illuminance_input': ('lx', 1, 'illuminance'), 'in_illuminance_raw': ('lx', 1, 'illuminance'), 'in_illuminanceY_input': ('lx', 1, 'illuminance'), 'in_illuminanceY_raw': ('lx', 1, 'illuminance'), 'in_illuminanceY_mean_raw': ('lx', 1, 'illuminance'), 'in_illuminance_ir_raw': ('lx', 1, 'illuminance'), 'in_illuminance_clear_raw': ('lx', 1, 'illuminance'), 'in_intensityY_raw': (float, 1, None), 'in_intensityY_ir_raw': (float, 1, None), 'in_intensityY_both_raw': (float, 1, None), 'in_intensityY_uv_raw': (float, 1, None), 'in_intensityY_uva_raw': (float, 1, None), 'in_intensityY_uvb_raw': (float, 1, None), 'in_intensityY_duv_raw': (float, 1, None), 'in_intensity_red_raw': (float, 1, None), 'in_intensity_green_raw': (float, 1, None), 'in_intensity_blue_raw': (float, 1, None), 'in_intensity_clear_raw': (float, 1, None), 'in_uvindex_input': ('UV index', 1, None), 'in_rot_quaternion_raw': (float, 1, None), 'in_rot_from_north_magnetic_tilt_comp_raw': (float, 1, None), 'in_rot_from_north_true_tilt_comp_raw': (float, 1, None), 'in_rot_from_north_magnetic_raw': (float, 1, None), 'in_rot_from_north_true_raw': (float, 1, None), 'in_currentY_raw': ('mA', 1, 'current'), 'in_currentY_supply_raw': ('mA', 1, 'current'), 'in_altcurrentY_rms_raw': ('mA', 1, 'current'), 'in_steps_en': (int, 1, None), 'in_velocity_sqrt(x^2+y^2+z^2)_input': ('m/s', 1, 'speed'), 'in_velocity_sqrt(x^2+y^2+z^2)_raw': ('m/s', 1, 'speed'), 'in_magn_x_oversampling_ratio': (float, 1, None), 'in_magn_y_oversampling_ratio': (float, 1, None), 'in_magn_z_oversampling_ratio': (float, 1, None), 'in_concentration_raw': ('%', 1, None), 'in_concentrationY_raw': ('%', 1, None), 'in_concentration_co2_raw': ('%', 1, 'co2'), 'in_concentrationY_co2_raw': ('%', 1, None), 'in_concentration_ethanol_raw': ('%', 1, None), 'in_concentrationY_ethanol_raw': ('%', 1, None), 'in_concentration_h2_raw': ('%', 1, None), 'in_concentrationY_h2_raw': ('%', 1, None), 'in_concentration_o2_raw': ('%', 1, None), 'in_concentrationY_o2_raw': ('%', 1, None), 'in_concentration_voc_raw': ('%', 1, 'volatile_organic_compounds'), 'in_concentrationY_voc_raw': ('%', 1, None), 'in_resistance_raw': ('ohms', 1, None), 'in_resistanceY_raw': ('ohms', 1, None), 'heater_enable': (bool, 1, None), 'in_ph_raw': (float, 1, None), 'in_massconcentration_pm1_input': ('µg/m³', 1, 'pm1'), 'in_massconcentrationY_pm1_input': ('µg/m³', 1, None), 'in_massconcentration_pm2p5_input': ('µg/m³', 1, 'pm25'), 'in_massconcentrationY_pm2p5_input': ('µg/m³', 1, None), 'in_massconcentration_pm4_input': ('µg/m³', 1, None), 'in_massconcentrationY_pm4_input': ('µg/m³', 1, None), 'in_massconcentration_pm10_input': ('µg/m³', 1, 'pm1'), 'in_massconcentrationY_pm10_input': ('µg/m³', 1, None), 'in_temp_thermocouple_type': (str, 1, None), 'in_intensity_x_raw': ('W/m²', 1e-09, 'irradiance'), 'in_intensity_y_raw': ('W/m²', 1e-09, 'irradiance'), 'in_intensity_z_raw': ('W/m²', 1e-09, 'irradiance'), 'in_anglY_label': (float, 57.29577951308232, None), 'in_illuminance_hysteresis_relative': ('%', 1, None), 'in_intensity_hysteresis_relative': ('%', 1, None), 'in_powerY_sampling_frequency': ('W', 0.001, None), 'in_currentY_sampling_frequency': ('mA', 1, 'current'), 'in_rot_yaw_raw': (float, 1, None), 'in_rot_pitch_raw': (float, 1, None), 'in_rot_roll_raw': (float, 1, None), 'in_colortemp_raw': ('K', 1, 'temperature')}
IIO_ATTRIBUTES = ['in_intensity_sampling_frequency', 'in_voltageY_raw', 'in_voltageY_supply_raw', 'in_voltageY-voltageZ_raw', 'in_altvoltageY_rms_raw', 'in_powerY_raw', 'in_powerY_active_raw', 'in_powerY_reactive_raw', 'in_powerY_apparent_raw', 'in_powerY_powerfactor', 'in_temp_raw', 'in_tempY_raw', 'in_temp_x_raw', 'in_temp_y_raw', 'in_temp_ambient_raw', 'in_temp_object_raw', 'in_tempY_input', 'in_temp_input', 'in_accel_x_raw', 'in_accel_y_raw', 'in_accel_z_raw', 'in_accel_linear_x_raw', 'in_accel_linear_y_raw', 'in_accel_linear_z_raw', 'in_gravity_x_raw', 'in_gravity_y_raw', 'in_gravity_z_raw', 'in_deltaangl_x_raw', 'in_deltaangl_y_raw', 'in_deltaangl_z_raw', 'in_deltavelocity_x_raw', 'in_deltavelocity_y_raw', 'in_deltavelocity_z_raw', 'in_angl_raw', 'in_anglY_raw', 'in_anglvel_x_raw', 'in_anglvel_y_raw', 'in_anglvel_z_raw', 'in_incli_x_raw', 'in_incli_y_raw', 'in_incli_z_raw', 'in_magn_x_raw', 'in_magn_y_raw', 'in_magn_z_raw', 'in_accel_x_peak_raw', 'in_accel_y_peak_raw', 'in_accel_z_peak_raw', 'in_humidityrelative_peak_raw', 'in_temp_peak_raw', 'in_humidityrelative_trough_raw', 'in_temp_trough_raw', 'in_accel_xyz_squared_peak_raw', 'in_humidityrelative_raw', 'in_humidityrelative_input', 'in_Y_mean_raw', 'in_activity_still_input', 'in_activity_walking_input', 'in_activity_jogging_input', 'in_activity_running_input', 'in_distance_input', 'in_distance_raw', 'in_proximity_raw', 'in_proximity_input', 'in_proximityY_raw', 'in_illuminance_input', 'in_illuminance_raw', 'in_illuminanceY_input', 'in_illuminanceY_raw', 'in_illuminanceY_mean_raw', 'in_illuminance_ir_raw', 'in_illuminance_clear_raw', 'in_intensityY_raw', 'in_intensityY_ir_raw', 'in_intensityY_both_raw', 'in_intensityY_uv_raw', 'in_intensityY_uva_raw', 'in_intensityY_uvb_raw', 'in_intensityY_duv_raw', 'in_intensity_red_raw', 'in_intensity_green_raw', 'in_intensity_blue_raw', 'in_intensity_clear_raw', 'in_uvindex_input', 'in_rot_quaternion_raw', 'in_rot_from_north_magnetic_tilt_comp_raw', 'in_rot_from_north_true_tilt_comp_raw', 'in_rot_from_north_magnetic_raw', 'in_rot_from_north_true_raw', 'in_currentY_raw', 'in_currentY_supply_raw', 'in_altcurrentY_rms_raw', 'in_steps_en', 'in_velocity_sqrt(x^2+y^2+z^2)_input', 'in_velocity_sqrt(x^2+y^2+z^2)_raw', 'in_magn_x_oversampling_ratio', 'in_magn_y_oversampling_ratio', 'in_magn_z_oversampling_ratio', 'in_concentration_raw', 'in_concentrationY_raw', 'in_concentration_co2_raw', 'in_concentrationY_co2_raw', 'in_concentration_ethanol_raw', 'in_concentrationY_ethanol_raw', 'in_concentration_h2_raw', 'in_concentrationY_h2_raw', 'in_concentration_o2_raw', 'in_concentrationY_o2_raw', 'in_concentration_voc_raw', 'in_concentrationY_voc_raw', 'in_resistance_raw', 'in_resistanceY_raw', 'heater_enable', 'in_ph_raw', 'in_massconcentration_pm1_input', 'in_massconcentrationY_pm1_input', 'in_massconcentration_pm2p5_input', 'in_massconcentrationY_pm2p5_input', 'in_massconcentration_pm4_input', 'in_massconcentrationY_pm4_input', 'in_massconcentration_pm10_input', 'in_massconcentrationY_pm10_input', 'in_temp_thermocouple_type', 'in_intensity_x_raw', 'in_intensity_y_raw', 'in_intensity_z_raw', 'in_anglY_label', 'in_illuminance_hysteresis_relative', 'in_intensity_hysteresis_relative', 'in_powerY_sampling_frequency', 'in_currentY_sampling_frequency', 'in_rot_yaw_raw', 'in_rot_pitch_raw', 'in_rot_roll_raw', 'in_colortemp_raw']

## Class to define a IIO Device object
# Class contains the device's path, name, and attributes
# Class has one method to parse and return the attribute data
class Device:
    ## Class Constructor
    def __init__(self, devicePath):
        self.devicePath = devicePath
        self.deviceID: int = 0
        self.name: str = ""
        self.stateTopic: str = ""
        self.availabilityTopic: str = ""
        self.abiAttributes: list = []
        self.genericAttributes: list = []
        self.__initDevice()

    ## Function to handle top level device parsing
    def __initDevice(self) -> None:
        # Device Name
        with open(os.path.join(self.devicePath, "name"), "r") as f:
            self.name = f.read().strip()

        # Attributes
        for attr in os.listdir(self.devicePath):
            if attr in IIO_META.keys():
                self.abiAttributes.append(attr)
            else:
                if attr.startswith("in_"):
                    self.genericAttributes.append(attr)

    ## Function to parse attribute data
    # Checks for a scale if available and applies it
    def parse(self) -> dict:
        data = {}
        for i, attr in enumerate(self.abiAttributes):
            path = os.path.join(self.devicePath, attr)
            print(f"[{i}] attr={repr(attr)} path={repr(path)}")

            with open(path, "r") as f:
                print(f"  opening {path}")
                attributeData = f.read().strip()
                print(f"  value={repr(attributeData)}")

            try:
                attributeData = float(attributeData)
                topLevelAttributeType = attr.split("_")[:2]
                scalePathPart = f"{topLevelAttributeType[0]}_{topLevelAttributeType[1]}_scale"
                scalePath = os.path.join(self.devicePath, scalePathPart)

                if os.path.exists(scalePath):
                    with open(scalePath) as scaleFile:
                        scaleData = float(scaleFile.read().strip())
                        data[attr] = round(attributeData * scaleData, 2)

            except ValueError:
                data[attr] = attributeData

        return data

    ## Function to generate MQTT auto discovery configs
    def generateConfigs(self, clientID: str) -> dict:
        config = {}

        for attr in self.abiAttributes:
            _configTopic = f"homeassistant/sensor/{self.name}_{attr}/config"
            _name = f"{self.name.upper()} {attr.title()}"
            _uniqueID = f"{self.name.lower()}_{attr.lower()}_{self.deviceID}"
            _stateTopic = f"homeassistant/sensor/{self.name}/state"
            _device = {"identifiers": [f"{self.name}_{clientID}"], "name": f"{self.name.upper()}_{clientID.title()}"}
            _availability = f"homeassistant/sensor/{self.name}/availability"
            _valueTemplate = "{{ value_json." + attr + " }}"
            _device_class = IIO_META.get(attr)[2] if IIO_META.get(attr) is not None else None
            _unitOfMeasurement = IIO_META.get(attr)[0] if IIO_META.get(attr) is not int and IIO_META.get(attr) is not float and IIO_META.get(attr) != str else None

            config[_configTopic] = {"name": _name, "unique_id": _uniqueID, "state_topic": _stateTopic}

            if _device_class is not None:
                config[_configTopic]["device_class"] = _device_class

            if _unitOfMeasurement is not None:
                config[_configTopic]["unit_of_measurement"] = _unitOfMeasurement

            config[_configTopic]["value_template"] = _valueTemplate
            config[_configTopic]["device"] = _device
            config[_configTopic]["availability_topic"] = _availability

            self.stateTopic = _stateTopic
            self.availabilityTopic = _availability

        return config

## Function to parse devices on the system
# This function finds all iio:deviceX's on the system
# and wraps them in a Device object
def find_iio_devices() -> list[Device]:
    if not os.path.exists(IIO_BASE):
        raise FileNotFoundError(f"No IIO devices found at {IIO_BASE}")
    _devices = sorted([d for d in os.listdir(IIO_BASE) if d.startswith("iio:device")])

    _physicalDevices = [Device(os.path.join(IIO_BASE + _device)) for _device in _devices]
    for index, _ in enumerate(_physicalDevices):
        _physicalDevices[index].deviceID = index

    return [d for d in _physicalDevices if len(d.abiAttributes)]

if __name__ == "__main__":
    devices = find_iio_devices()
    for d in devices:
        d.parse()