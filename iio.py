import os

## Constant
# Specifies the IIO Base folder in Linux
IIO_BASE = "/sys/bus/iio/devices/"
IIO_ATTRIBUTES_WITH_UNITS = {'current_timestamp_clock': ('mA', 1), 'in_intensity_sampling_frequency': (float, 1), 'in_voltageY_raw': ('mV', 1), 'in_voltageY_supply_raw': ('mV', 1), 'in_voltageY-voltageZ_raw': ('mV', 1), 'in_altvoltageY_rms_raw': ('mV', 1), 'in_powerY_raw': ('W', 0.001), 'in_powerY_active_raw': ('W', 0.001), 'in_powerY_reactive_raw': ('W', 0.001), 'in_powerY_apparent_raw': ('W', 0.001), 'in_powerY_powerfactor': ('W', 0.001), 'in_temp_raw': ('°C', 0.001), 'in_tempY_raw': ('°C', 0.001), 'in_temp_x_raw': ('°C', 0.001), 'in_temp_y_raw': ('°C', 0.001), 'in_temp_ambient_raw': ('°C', 0.001), 'in_temp_object_raw': ('°C', 0.001), 'in_tempY_input': ('°C', 0.001), 'in_temp_input': ('°C', 0.001), 'in_accel_x_raw': ('m/s', 1), 'in_accel_y_raw': ('m/s', 1), 'in_accel_z_raw': ('m/s', 1), 'in_accel_linear_x_raw': ('m/s', 1), 'in_accel_linear_y_raw': ('m/s', 1), 'in_accel_linear_z_raw': ('m/s', 1), 'in_gravity_x_raw': ('m/s', 1), 'in_gravity_y_raw': ('m/s', 1), 'in_gravity_z_raw': ('m/s', 1), 'in_deltaangl_x_raw': (float, 57.29577951308232), 'in_deltaangl_y_raw': (float, 57.29577951308232), 'in_deltaangl_z_raw': (float, 57.29577951308232), 'in_deltavelocity_x_raw': ('m/s', 1), 'in_deltavelocity_y_raw': ('m/s', 1), 'in_deltavelocity_z_raw': ('m/s', 1), 'in_angl_raw': (float, 57.29577951308232), 'in_anglY_raw': (float, 57.29577951308232), 'in_anglvel_x_raw': ('m/s', 57.29577951308232), 'in_anglvel_y_raw': ('m/s', 57.29577951308232), 'in_anglvel_z_raw': ('m/s', 57.29577951308232), 'in_incli_x_raw': (float, 1), 'in_incli_y_raw': (float, 1), 'in_incli_z_raw': (float, 1), 'in_magn_x_raw': (float, 1), 'in_magn_y_raw': (float, 1), 'in_magn_z_raw': (float, 1), 'in_accel_x_peak_raw': ('m/s', 1), 'in_accel_y_peak_raw': ('m/s', 1), 'in_accel_z_peak_raw': ('m/s', 1), 'in_humidityrelative_peak_raw': ('%', 1), 'in_temp_peak_raw': ('°C', 0.001), 'in_humidityrelative_trough_raw': ('%', 1), 'in_temp_trough_raw': ('°C', 0.001), 'in_accel_xyz_squared_peak_raw': ('m/s', 1), 'in_humidityrelative_raw': ('%', 1), 'in_humidityrelative_input': ('%', 1), 'in_Y_mean_raw': ('float', 1), 'in_activity_still_input': ('%', 1), 'in_activity_walking_input': ('%', 1), 'in_activity_jogging_input': ('%', 1), 'in_activity_running_input': ('%', 1), 'in_distance_input': ('m', 1), 'in_distance_raw': ('m', 1), 'in_proximity_raw': ('m', 1), 'in_proximity_input': ('m', 1), 'in_proximityY_raw': ('m', 1), 'in_illuminance_input': ('lx', 1), 'in_illuminance_raw': ('lx', 1), 'in_illuminanceY_input': ('lx', 1), 'in_illuminanceY_raw': ('lx', 1), 'in_illuminanceY_mean_raw': ('lx', 1), 'in_illuminance_ir_raw': ('lx', 1), 'in_illuminance_clear_raw': ('lx', 1), 'in_intensityY_raw': (float, 1), 'in_intensityY_ir_raw': (float, 1), 'in_intensityY_both_raw': (float, 1), 'in_intensityY_uv_raw': (float, 1), 'in_intensityY_uva_raw': (float, 1), 'in_intensityY_uvb_raw': (float, 1), 'in_intensityY_duv_raw': (float, 1), 'in_intensity_red_raw': (float, 1), 'in_intensity_green_raw': (float, 1), 'in_intensity_blue_raw': (float, 1), 'in_intensity_clear_raw': (float, 1), 'in_uvindex_input': ('UV index', 1), 'in_rot_quaternion_raw': (float, 1), 'in_rot_from_north_magnetic_tilt_comp_raw': (float, 1), 'in_rot_from_north_true_tilt_comp_raw': (float, 1), 'in_rot_from_north_magnetic_raw': (float, 1), 'in_rot_from_north_true_raw': (float, 1), 'in_currentY_raw': ('mA', 1), 'in_currentY_supply_raw': ('mA', 1), 'in_altcurrentY_rms_raw': ('mA', 1), 'in_steps_en': (int, 1), 'in_velocity_sqrt(x^2+y^2+z^2)_input': ('m/s', 1), 'in_velocity_sqrt(x^2+y^2+z^2)_raw': ('m/s', 1), 'in_magn_x_oversampling_ratio': (float, 1), 'in_magn_y_oversampling_ratio': (float, 1), 'in_magn_z_oversampling_ratio': (float, 1), 'in_concentration_raw': ('%', 1), 'in_concentrationY_raw': ('%', 1), 'in_concentration_co2_raw': ('%', 1), 'in_concentrationY_co2_raw': ('%', 1), 'in_concentration_ethanol_raw': ('%', 1), 'in_concentrationY_ethanol_raw': ('%', 1), 'in_concentration_h2_raw': ('%', 1), 'in_concentrationY_h2_raw': ('%', 1), 'in_concentration_o2_raw': ('%', 1), 'in_concentrationY_o2_raw': ('%', 1), 'in_concentration_voc_raw': ('%', 1), 'in_concentrationY_voc_raw': ('%', 1), 'in_resistance_raw': ('ohms', 1), 'in_resistanceY_raw': ('ohms', 1), 'heater_enable': (bool, 1), 'in_ph_raw': (float, 1), 'in_massconcentration_pm1_input': ('µg/m³', 1), 'in_massconcentrationY_pm1_input': ('µg/m³', 1), 'in_massconcentration_pm2p5_input': ('µg/m³', 1), 'in_massconcentrationY_pm2p5_input': ('µg/m³', 1), 'in_massconcentration_pm4_input': ('µg/m³', 1), 'in_massconcentrationY_pm4_input': ('µg/m³', 1), 'in_massconcentration_pm10_input': ('µg/m³', 1), 'in_massconcentrationY_pm10_input': ('µg/m³', 1), 'in_temp_thermocouple_type': (str, 1), 'in_intensity_x_raw': ('W/m²', 1e-09), 'in_intensity_y_raw': ('W/m²', 1e-09), 'in_intensity_z_raw': ('W/m²', 1e-09), 'in_anglY_label': (float, 57.29577951308232), 'in_illuminance_hysteresis_relative': ('%', 1), 'in_intensity_hysteresis_relative': ('%', 1), 'in_powerY_sampling_frequency': ('W', 0.001), 'in_currentY_sampling_frequency': ('mA', 1), 'in_rot_yaw_raw': (float, 1), 'in_rot_pitch_raw': (float, 1), 'in_rot_roll_raw': (float, 1), 'in_colortemp_raw': ('K', 1)}
IIO_ATTRIBUTES = ['current_timestamp_clock', 'in_intensity_sampling_frequency', 'in_voltageY_raw', 'in_voltageY_supply_raw', 'in_voltageY-voltageZ_raw', 'in_altvoltageY_rms_raw', 'in_powerY_raw', 'in_powerY_active_raw', 'in_powerY_reactive_raw', 'in_powerY_apparent_raw', 'in_powerY_powerfactor', 'in_temp_raw', 'in_tempY_raw', 'in_temp_x_raw', 'in_temp_y_raw', 'in_temp_ambient_raw', 'in_temp_object_raw', 'in_tempY_input', 'in_temp_input', 'in_accel_x_raw', 'in_accel_y_raw', 'in_accel_z_raw', 'in_accel_linear_x_raw', 'in_accel_linear_y_raw', 'in_accel_linear_z_raw', 'in_gravity_x_raw', 'in_gravity_y_raw', 'in_gravity_z_raw', 'in_deltaangl_x_raw', 'in_deltaangl_y_raw', 'in_deltaangl_z_raw', 'in_deltavelocity_x_raw', 'in_deltavelocity_y_raw', 'in_deltavelocity_z_raw', 'in_angl_raw', 'in_anglY_raw', 'in_anglvel_x_raw', 'in_anglvel_y_raw', 'in_anglvel_z_raw', 'in_incli_x_raw', 'in_incli_y_raw', 'in_incli_z_raw', 'in_magn_x_raw', 'in_magn_y_raw', 'in_magn_z_raw', 'in_accel_x_peak_raw', 'in_accel_y_peak_raw', 'in_accel_z_peak_raw', 'in_humidityrelative_peak_raw', 'in_temp_peak_raw', 'in_humidityrelative_trough_raw', 'in_temp_trough_raw', 'in_accel_xyz_squared_peak_raw', 'in_humidityrelative_raw', 'in_humidityrelative_input', 'in_Y_mean_raw', 'in_activity_still_input', 'in_activity_walking_input', 'in_activity_jogging_input', 'in_activity_running_input', 'in_distance_input', 'in_distance_raw', 'in_proximity_raw', 'in_proximity_input', 'in_proximityY_raw', 'in_illuminance_input', 'in_illuminance_raw', 'in_illuminanceY_input', 'in_illuminanceY_raw', 'in_illuminanceY_mean_raw', 'in_illuminance_ir_raw', 'in_illuminance_clear_raw', 'in_intensityY_raw', 'in_intensityY_ir_raw', 'in_intensityY_both_raw', 'in_intensityY_uv_raw', 'in_intensityY_uva_raw', 'in_intensityY_uvb_raw', 'in_intensityY_duv_raw', 'in_intensity_red_raw', 'in_intensity_green_raw', 'in_intensity_blue_raw', 'in_intensity_clear_raw', 'in_uvindex_input', 'in_rot_quaternion_raw', 'in_rot_from_north_magnetic_tilt_comp_raw', 'in_rot_from_north_true_tilt_comp_raw', 'in_rot_from_north_magnetic_raw', 'in_rot_from_north_true_raw', 'in_currentY_raw', 'in_currentY_supply_raw', 'in_altcurrentY_rms_raw', 'in_steps_en', 'in_velocity_sqrt(x^2+y^2+z^2)_input', 'in_velocity_sqrt(x^2+y^2+z^2)_raw', 'in_magn_x_oversampling_ratio', 'in_magn_y_oversampling_ratio', 'in_magn_z_oversampling_ratio', 'in_concentration_raw', 'in_concentrationY_raw', 'in_concentration_co2_raw', 'in_concentrationY_co2_raw', 'in_concentration_ethanol_raw', 'in_concentrationY_ethanol_raw', 'in_concentration_h2_raw', 'in_concentrationY_h2_raw', 'in_concentration_o2_raw', 'in_concentrationY_o2_raw', 'in_concentration_voc_raw', 'in_concentrationY_voc_raw', 'in_resistance_raw', 'in_resistanceY_raw', 'heater_enable', 'in_ph_raw', 'in_massconcentration_pm1_input', 'in_massconcentrationY_pm1_input', 'in_massconcentration_pm2p5_input', 'in_massconcentrationY_pm2p5_input', 'in_massconcentration_pm4_input', 'in_massconcentrationY_pm4_input', 'in_massconcentration_pm10_input', 'in_massconcentrationY_pm10_input', 'in_temp_thermocouple_type', 'in_intensity_x_raw', 'in_intensity_y_raw', 'in_intensity_z_raw', 'in_anglY_label', 'in_illuminance_hysteresis_relative', 'in_intensity_hysteresis_relative', 'in_powerY_sampling_frequency', 'in_currentY_sampling_frequency', 'in_rot_yaw_raw', 'in_rot_pitch_raw', 'in_rot_roll_raw', 'in_colortemp_raw']


## Class to define a IIO Device object
# Class contains the device's path, name, and attributes
# Class has one method to parse and return the attribute data
class Device:
    ## Class Constructor
    def __init__(self, devicePath):
        self.devicePath = devicePath
        self.name = ""
        self.attributes = []
        self.__initDevice()

    ## Function to handle top level device parsing
    def __initDevice(self) -> None:
        # Device Name
        with open(os.path.join(self.devicePath, "name"), "r") as f:
            self.name = f.readline().strip()

        # Attributes
        self.attributes = [attr for attr in os.listdir(self.devicePath) if attr in IIO_ATTRIBUTES]

    ## Function to parse attribute data
    # Checks for a scale if available and applies it
    def parse(self) -> dict:
        data = {}
        for attr in self.attributes:
            with open(os.path.join(self.devicePath, attr), "r") as f:
                attributeData = f.readline().strip()

                try:
                    attributeData = float(attributeData)
                    topLevelAttributeType = attr.split("_")[:2]
                    scalePathPart = f"{topLevelAttributeType[0]}_{topLevelAttributeType[1]}_scale"
                    # offsetPathPart = f"{topLevelAttributeType[0]}_{topLevelAttributeType[1]}_offset"

                    if os.path.exists(os.path.join(self.devicePath, scalePathPart)):
                        with open(os.path.join(self.devicePath, scalePathPart)) as scaleFile:
                            scaleData = float(scaleFile.readline().strip())
                            data[attr] = round(attributeData * scaleData, 2)

                except ValueError:
                    data[attr] = attributeData

        return data


def find_iio_devices() -> list[Device]:
    if not os.path.exists(IIO_BASE):
        raise FileNotFoundError(f"No IIO devices found at {IIO_BASE}")
    _devices = sorted([d for d in os.listdir(IIO_BASE) if d.startswith("iio:device")])

    return [Device(os.path.join(IIO_BASE + _device)) for _device in _devices]

if __name__ == "__main__":
    devices = find_iio_devices()
    print(devices[1].parse())