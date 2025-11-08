import socket
import time
from threading import Event
import json
import ssl
from enum import IntEnum
from helper import *
import temp

IIO_ATTRIBUTES = {'Device Attributes': ['buffer', 'name', 'label', 'current_timestamp_clock', 'sampling_frequency', 'in_intensity_sampling_frequency', 'sampling_frequency_available', 'in_intensity_sampling_frequency_available', 'in_proximity_sampling_frequency_available', 'oversampling_ratio', 'oversampling_ratio_available', 'in_voltageY_raw', 'in_voltageY_supply_raw', 'in_voltageY-voltageZ_raw', 'in_altvoltageY_rms_raw', 'in_powerY_raw', 'in_powerY_active_raw', 'in_powerY_reactive_raw', 'in_powerY_apparent_raw', 'in_powerY_powerfactor', 'in_capacitanceY_raw', 'in_capacitanceY-capacitanceZ_raw', 'in_capacitanceY-capacitanceZ_zeropoint', 'in_temp_raw', 'in_tempY_raw', 'in_temp_x_raw', 'in_temp_y_raw', 'in_temp_ambient_raw', 'in_temp_object_raw', 'in_tempY_input', 'in_temp_input', 'in_accel_x_raw', 'in_accel_y_raw', 'in_accel_z_raw', 'in_accel_linear_x_raw', 'in_accel_linear_y_raw', 'in_accel_linear_z_raw', 'in_gravity_x_raw', 'in_gravity_y_raw', 'in_gravity_z_raw', 'in_deltaangl_x_raw', 'in_deltaangl_y_raw', 'in_deltaangl_z_raw', 'in_deltavelocity_x_raw', 'in_deltavelocity_y_raw', 'in_deltavelocity_z_raw', 'in_angl_raw', 'in_anglY_raw', 'in_positionrelative_x_raw', 'in_positionrelative_y_raw', 'in_anglvel_x_raw', 'in_anglvel_y_raw', 'in_anglvel_z_raw', 'in_incli_x_raw', 'in_incli_y_raw', 'in_incli_z_raw', 'in_magn_x_raw', 'in_magn_y_raw', 'in_magn_z_raw', 'in_accel_x_peak_raw', 'in_accel_y_peak_raw', 'in_accel_z_peak_raw', 'in_humidityrelative_peak_raw', 'in_temp_peak_raw', 'in_humidityrelative_trough_raw', 'in_temp_trough_raw', 'in_accel_xyz_squared_peak_raw', 'in_pressureY_raw', 'in_pressure_raw', 'in_pressureY_input', 'in_pressure_input', 'in_humidityrelative_raw', 'in_humidityrelative_input', 'in_Y_mean_raw', 'in_accel_offset', 'in_accel_x_offset', 'in_accel_y_offset', 'in_accel_z_offset', 'in_altvoltage_q_offset', 'in_altvoltage_i_offset', 'in_voltageY_offset', 'in_voltage_offset', 'in_voltageY_i_offset', 'in_voltageY_q_offset', 'in_currentY_offset', 'in_current_offset', 'in_tempY_offset', 'in_temp_offset', 'in_pressureY_offset', 'in_pressure_offset', 'in_humidityrelative_offset', 'in_magn_offset', 'in_rot_offset', 'in_angl_offset', 'in_capacitanceY_offset', 'in_voltageY_scale', 'in_voltageY_q_scale', 'in_voltageY_supply_scale', 'in_voltage_scale', 'in_voltage-voltage_scale', 'out_voltageY_scale', 'out_altvoltageY_scale', 'in_currentY_scale', 'in_currentY_supply_scale', 'in_current_scale', 'in_current_q_scale', 'in_accel_scale', 'in_accel_peak_scale', 'in_anglvel_scale', 'in_energy_scale', 'in_distance_scale', 'in_magn_scale', 'in_magn_x_scale', 'in_magn_y_scale', 'in_magn_z_scale', 'in_rot_from_north_magnetic_scale', 'in_rot_from_north_true_scale', 'in_rot_from_north_magnetic_tilt_comp_scale', 'in_rot_from_north_true_tilt_comp_scale', 'in_pressureY_scale', 'in_pressure_scale', 'in_humidityrelative_scale', 'in_velocity_sqrt(x^2+y^2+z^2)_scale', 'in_illuminance_scale', 'in_countY_scale', 'in_deltaangl_scale', 'in_deltavelocity_scale', 'in_angl_scale', 'in_intensity_x_scale', 'in_intensity_y_scale', 'in_intensity_z_scale', 'in_intensity_red_scale', 'in_intensity_green_scale', 'in_intensity_blue_scale', 'in_concentration_co2_scale', 'in_accel_x_calibbias', 'in_accel_y_calibbias', 'in_accel_z_calibbias', 'in_altvoltageY_i_calibbias', 'in_altvoltageY_q_calibbias', 'in_anglvel_x_calibbias', 'in_anglvel_y_calibbias', 'in_anglvel_z_calibbias', 'in_capacitance_calibbias', 'in_illuminance_calibbias', 'in_illuminance0_calibbias', 'in_intensityY_calibbias', 'in_magn_x_calibbias', 'in_magn_y_calibbias', 'in_magn_z_calibbias', 'in_pressure_calibbias', 'in_pressureY_calibbias', 'in_proximity_calibbias', 'in_proximity0_calibbias', 'in_resistance_calibbias', 'in_temp_calibbias', 'in_voltageY_calibbias', 'out_currentY_calibbias', 'out_voltageY_calibbias', 'in_accel_calibbias_available', 'in_anglvel_calibbias_available', 'in_temp_calibbias_available', 'in_proximity_calibbias_available', 'in_voltageY_calibbias_available', 'out_voltageY_calibbias_available', 'in_voltageY_convdelay', 'in_voltageY_convdelay_available', 'in_accel_x_calibscale', 'in_accel_y_calibscale', 'in_accel_z_calibscale', 'in_altvoltage_calibscale', 'in_anglvel_x_calibscale', 'in_anglvel_y_calibscale', 'in_anglvel_z_calibscale', 'in_capacitance_calibscale', 'in_illuminance_calibscale', 'in_illuminance0_calibscale', 'in_intensity_both_calibscale', 'in_intensity_calibscale', 'in_intensity_ir_calibscale', 'in_magn_x_calibscale', 'in_magn_y_calibscale', 'in_magn_z_calibscale', 'in_pressure_calibscale', 'in_pressureY_calibscale', 'in_proximity0_calibscale', 'in_voltage_calibscale', 'in_voltageY_calibscale', 'in_voltageY_supply_calibscale', 'out_currentY_calibscale', 'out_voltageY_calibscale', 'in_illuminanceY_calibscale_available', 'in_intensityY_calibscale_available', 'in_proximityY_calibscale_available', 'in_voltageY_calibscale_available', 'in_activity_calibgender', 'in_energy_calibgender', 'in_distance_calibgender', 'in_velocity_calibgender', 'in_activity_calibgender_available', 'in_energy_calibgender_available', 'in_distance_calibgender_available', 'in_velocity_calibgender_available', 'in_activity_calibheight', 'in_energy_calibheight', 'in_distance_calibheight', 'in_velocity_calibheight', 'in_energy_calibweight', 'in_accel_scale_available', 'in_anglvel_scale_available', 'in_magn_scale_available', 'in_illuminance_scale_available', 'in_intensity_scale_available', 'in_proximity_scale_available', 'in_voltageY_scale_available', 'in_voltage-voltage_scale_available', 'out_voltageY_scale_available', 'out_altvoltageY_scale_available', 'in_capacitance_scale_available', 'in_pressure_scale_available', 'in_pressureY_scale_available', 'out_voltageY_hardwaregain', 'in_intensity_hardwaregain', 'in_intensity_red_hardwaregain', 'in_intensity_green_hardwaregain', 'in_intensity_blue_hardwaregain', 'in_intensity_clear_hardwaregain', 'in_illuminance_hardwaregain', 'in_intensity_hardwaregain_available', 'in_accel_filter_low_pass_3db_frequency', 'in_magn_filter_low_pass_3db_frequency', 'in_anglvel_filter_low_pass_3db_frequency', 'in_accel_filter_high_pass_3db_frequency', 'in_anglvel_filter_high_pass_3db_frequency', 'in_magn_filter_high_pass_3db_frequency', 'out_voltageY_raw', 'out_altvoltageY_raw', 'out_voltageY&Z_raw', 'out_altvoltageY&Z_raw', 'out_voltageY_powerdown_mode', 'out_voltage_powerdown_mode', 'out_altvoltageY_powerdown_mode', 'out_altvoltage_powerdown_mode', 'out_voltageY_powerdown_mode_available', 'out_voltage_powerdown_mode_available', 'out_altvoltageY_powerdown_mode_available', 'out_altvoltage_powerdown_mode_available', 'out_voltageY_powerdown', 'out_voltage_powerdown', 'out_altvoltageY_powerdown', 'out_altvoltage_powerdown', 'out_altvoltageY_frequency', 'in_altvoltageY_i_phase', 'in_altvoltageY_q_phase', 'out_altvoltageY_phase', 'out_altvoltageY_i_phase', 'out_altvoltageY_q_phase', 'out_currentY_raw', 'events', 'bufferY', 'in_accel_type_available', 'in_activity_still_input', 'in_activity_walking_input', 'in_activity_jogging_input', 'in_activity_running_input', 'in_anglvel_z_quadrature_correction_raw', 'in_accelY_power_mode', 'in_energy_input', 'in_energy_raw', 'in_energyY_active_raw', 'in_energyY_reactive_raw', 'in_energyY_apparent_raw', 'in_distance_input', 'in_distance_raw', 'store_eeprom', 'in_proximity_raw', 'in_proximity_input', 'in_proximityY_raw', 'in_illuminance_input', 'in_illuminance_raw', 'in_illuminanceY_input', 'in_illuminanceY_raw', 'in_illuminanceY_mean_raw', 'in_illuminance_ir_raw', 'in_illuminance_clear_raw', 'in_intensityY_raw', 'in_intensityY_ir_raw', 'in_intensityY_both_raw', 'in_intensityY_uv_raw', 'in_intensityY_uva_raw', 'in_intensityY_uvb_raw', 'in_intensityY_duv_raw', 'in_intensity_red_raw', 'in_intensity_green_raw', 'in_intensity_blue_raw', 'in_intensity_clear_raw', 'in_uvindex_input', 'in_intensity_integration_time', 'in_intensity_red_integration_time', 'in_intensity_green_integration_time', 'in_intensity_blue_integration_time', 'in_intensity_clear_integration_time', 'in_illuminance_integration_time', 'in_velocity_sqrt(x^2+y^2+z^2)_integration_time', 'in_rot_quaternion_raw', 'in_rot_from_north_magnetic_tilt_comp_raw', 'in_rot_from_north_true_tilt_comp_raw', 'in_rot_from_north_magnetic_raw', 'in_rot_from_north_true_raw', 'in_currentY_raw', 'in_currentY_supply_raw', 'in_altcurrentY_rms_raw', 'in_energy_en', 'in_distance_en', 'in_velocity_sqrt(x^2+y^2+z^2)_en', 'in_steps_en', 'in_steps_input', 'in_velocity_sqrt(x^2+y^2+z^2)_input', 'in_velocity_sqrt(x^2+y^2+z^2)_raw', 'in_steps_debounce_count', 'in_steps_debounce_time', 'in_temp_calibemissivity', 'in_tempY_calibemissivity', 'in_temp_object_calibemissivity', 'in_tempY_object_calibemissivity', 'in_magn_x_oversampling_ratio', 'in_magn_y_oversampling_ratio', 'in_magn_z_oversampling_ratio', 'in_concentration_raw', 'in_concentrationY_raw', 'in_concentration_co2_raw', 'in_concentrationY_co2_raw', 'in_concentration_ethanol_raw', 'in_concentrationY_ethanol_raw', 'in_concentration_h2_raw', 'in_concentrationY_h2_raw', 'in_concentration_o2_raw', 'in_concentrationY_o2_raw', 'in_concentration_voc_raw', 'in_concentrationY_voc_raw', 'in_resistance_raw', 'in_resistanceY_raw', 'out_resistance_raw', 'out_resistanceY_raw', 'heater_enable', 'in_ph_raw', 'mount_matrix', 'in_mount_matrix', 'out_mount_matrix', 'in_anglvel_mount_matrix', 'in_accel_mount_matrix', 'in_electricalconductivity_raw', 'in_countY_raw', 'in_indexY_raw', 'in_count_count_direction_available', 'in_countY_count_direction', 'in_voltageY_label', 'out_voltageY_label', 'in_phaseY_raw', 'in_massconcentration_pm1_input', 'in_massconcentrationY_pm1_input', 'in_massconcentration_pm2p5_input', 'in_massconcentrationY_pm2p5_input', 'in_massconcentration_pm4_input', 'in_massconcentrationY_pm4_input', 'in_massconcentration_pm10_input', 'in_massconcentrationY_pm10_input', 'in_filter_notch_center_frequency', 'in_temp_thermocouple_type', 'in_temp_object_calibambient', 'in_tempY_object_calibambient', 'in_intensity_x_raw', 'in_intensity_y_raw', 'in_intensity_z_raw', 'in_anglY_label', 'in_illuminance_hysteresis_relative', 'in_intensity_hysteresis_relative', 'calibration_auto_enable', 'calibration_forced_value', 'calibration_forced_value_available', 'in_voltageY_sampling_frequency', 'in_powerY_sampling_frequency', 'in_currentY_sampling_frequency', 'in_rot_yaw_raw', 'in_rot_pitch_raw', 'in_rot_roll_raw', 'serialnumber', 'filter_type_available', 'in_voltage-voltage_filter_type_available', 'filter_type', 'in_voltageY-voltageZ_filter_type', 'in_colortemp_raw', 'in_chromaticity_x_raw', 'in_chromaticity_y_raw', 'in_shunt_resistor', 'in_current_shunt_resistor', 'in_power_shunt_resistor', 'in_attention_input'], 'Event Attributes': ['sampling_frequency', 'in_accel_x_thresh_rising_en', 'in_accel_x_thresh_falling_en', 'in_accel_y_thresh_rising_en', 'in_accel_y_thresh_falling_en', 'in_accel_z_thresh_rising_en', 'in_accel_z_thresh_falling_en', 'in_anglvel_x_thresh_rising_en', 'in_anglvel_x_thresh_falling_en', 'in_anglvel_y_thresh_rising_en', 'in_anglvel_y_thresh_falling_en', 'in_anglvel_z_thresh_rising_en', 'in_anglvel_z_thresh_falling_en', 'in_magn_x_thresh_rising_en', 'in_magn_x_thresh_falling_en', 'in_magn_y_thresh_rising_en', 'in_magn_y_thresh_falling_en', 'in_magn_z_thresh_rising_en', 'in_magn_z_thresh_falling_en', 'in_rot_from_north_magnetic_thresh_rising_en', 'in_rot_from_north_magnetic_thresh_falling_en', 'in_rot_from_north_true_thresh_rising_en', 'in_rot_from_north_true_thresh_falling_en', 'in_rot_from_north_magnetic_tilt_comp_thresh_rising_en', 'in_rot_from_north_magnetic_tilt_comp_thresh_falling_en', 'in_rot_from_north_true_tilt_comp_thresh_rising_en', 'in_rot_from_north_true_tilt_comp_thresh_falling_en', 'in_voltageY_supply_thresh_rising_en', 'in_voltageY_supply_thresh_falling_en', 'in_voltageY_thresh_rising_en', 'in_voltageY_thresh_falling_en', 'in_voltageY_thresh_either_en', 'in_tempY_thresh_rising_en', 'in_tempY_thresh_falling_en', 'in_capacitanceY_thresh_rising_en', 'in_capacitanceY_thresh_falling_en', 'in_accel_x_roc_rising_en', 'in_accel_x_roc_falling_en', 'in_accel_y_roc_rising_en', 'in_accel_y_roc_falling_en', 'in_accel_z_roc_rising_en', 'in_accel_z_roc_falling_en', 'in_anglvel_x_roc_rising_en', 'in_anglvel_x_roc_falling_en', 'in_anglvel_y_roc_rising_en', 'in_anglvel_y_roc_falling_en', 'in_anglvel_z_roc_rising_en', 'in_anglvel_z_roc_falling_en', 'in_magn_x_roc_rising_en', 'in_magn_x_roc_falling_en', 'in_magn_y_roc_rising_en', 'in_magn_y_roc_falling_en', 'in_magn_z_roc_rising_en', 'in_magn_z_roc_falling_en', 'in_rot_from_north_magnetic_roc_rising_en', 'in_rot_from_north_magnetic_roc_falling_en', 'in_rot_from_north_true_roc_rising_en', 'in_rot_from_north_true_roc_falling_en', 'in_rot_from_north_magnetic_tilt_comp_roc_rising_en', 'in_rot_from_north_magnetic_tilt_comp_roc_falling_en', 'in_rot_from_north_true_tilt_comp_roc_rising_en', 'in_rot_from_north_true_tilt_comp_roc_falling_en', 'in_voltageY_supply_roc_rising_en', 'in_voltageY_supply_roc_falling_en', 'in_voltageY_roc_rising_en', 'in_voltageY_roc_falling_en', 'in_tempY_roc_rising_en', 'in_tempY_roc_falling_en', 'in_capacitanceY_adaptive_thresh_rising_en', 'in_capacitanceY_adaptive_thresh_falling_en', 'in_accel_thresh_rising_value', 'in_accel_thresh_falling_value', 'in_accel_x_raw_thresh_rising_value', 'in_accel_x_raw_thresh_falling_value', 'in_accel_y_raw_thresh_rising_value', 'in_accel_y_raw_thresh_falling_value', 'in_accel_z_raw_thresh_rising_value', 'in_accel_z_raw_thresh_falling_value', 'in_anglvel_x_raw_thresh_rising_value', 'in_anglvel_x_raw_thresh_falling_value', 'in_anglvel_y_raw_thresh_rising_value', 'in_anglvel_y_raw_thresh_falling_value', 'in_anglvel_z_raw_thresh_rising_value', 'in_anglvel_z_raw_thresh_falling_value', 'in_magn_x_raw_thresh_rising_value', 'in_magn_x_raw_thresh_falling_value', 'in_magn_y_raw_thresh_rising_value', 'in_magn_y_raw_thresh_falling_value', 'in_magn_z_raw_thresh_rising_value', 'in_magn_z_raw_thresh_falling_value', 'in_rot_from_north_magnetic_raw_thresh_rising_value', 'in_rot_from_north_magnetic_raw_thresh_falling_value', 'in_rot_from_north_true_raw_thresh_rising_value', 'in_rot_from_north_true_raw_thresh_falling_value', 'in_rot_from_north_magnetic_tilt_comp_raw_thresh_rising_value', 'in_rot_from_north_magnetic_tilt_comp_raw_thresh_falling_value', 'in_rot_from_north_true_tilt_comp_raw_thresh_rising_value', 'in_rot_from_north_true_tilt_comp_raw_thresh_falling_value', 'in_voltageY_supply_raw_thresh_rising_value', 'in_voltageY_supply_raw_thresh_falling_value', 'in_voltageY_raw_thresh_rising_value', 'in_voltageY_raw_thresh_falling_value', 'in_tempY_raw_thresh_rising_value', 'in_tempY_raw_thresh_falling_value', 'in_illuminance0_thresh_falling_value', 'in_illuminance0_thresh_rising_value', 'in_proximity0_thresh_falling_value', 'in_proximity0_thresh_rising_value', 'in_illuminance_thresh_rising_value', 'in_illuminance_thresh_falling_value', 'in_capacitanceY_thresh_rising_value', 'in_capacitanceY_thresh_falling_value', 'in_capacitanceY_thresh_adaptive_rising_value', 'in_capacitanceY_thresh_falling_rising_value', 'in_accel_scale', 'in_accel_peak_scale', 'in_anglvel_scale', 'in_magn_scale', 'in_rot_from_north_magnetic_scale', 'in_rot_from_north_true_scale', 'in_voltage_scale', 'in_voltage_supply_scale', 'in_temp_scale', 'in_illuminance_scale', 'in_proximity_scale', 'in_accel_x_thresh_rising_hysteresis', 'in_accel_x_thresh_falling_hysteresis', 'in_accel_x_thresh_either_hysteresis', 'in_accel_y_thresh_rising_hysteresis', 'in_accel_y_thresh_falling_hysteresis', 'in_accel_y_thresh_either_hysteresis', 'in_accel_z_thresh_rising_hysteresis', 'in_accel_z_thresh_falling_hysteresis', 'in_accel_z_thresh_either_hysteresis', 'in_anglvel_x_thresh_rising_hysteresis', 'in_anglvel_x_thresh_falling_hysteresis', 'in_anglvel_x_thresh_either_hysteresis', 'in_anglvel_y_thresh_rising_hysteresis', 'in_anglvel_y_thresh_falling_hysteresis', 'in_anglvel_y_thresh_either_hysteresis', 'in_anglvel_z_thresh_rising_hysteresis', 'in_anglvel_z_thresh_falling_hysteresis', 'in_anglvel_z_thresh_either_hysteresis', 'in_magn_x_thresh_rising_hysteresis', 'in_magn_x_thresh_falling_hysteresis', 'in_magn_x_thresh_either_hysteresis', 'in_magn_y_thresh_rising_hysteresis', 'in_magn_y_thresh_falling_hysteresis', 'in_magn_y_thresh_either_hysteresis', 'in_magn_z_thresh_rising_hysteresis', 'in_magn_z_thresh_falling_hysteresis', 'in_magn_z_thresh_either_hysteresis', 'in_rot_from_north_magnetic_thresh_rising_hysteresis', 'in_rot_from_north_magnetic_thresh_falling_hysteresis', 'in_rot_from_north_magnetic_thresh_either_hysteresis', 'in_rot_from_north_true_thresh_rising_hysteresis', 'in_rot_from_north_true_thresh_falling_hysteresis', 'in_rot_from_north_true_thresh_either_hysteresis', 'in_rot_from_north_magnetic_tilt_comp_thresh_rising_hysteresis', 'in_rot_from_north_magnetic_tilt_comp_thresh_falling_hysteresis', 'in_rot_from_north_magnetic_tilt_comp_thresh_either_hysteresis', 'in_rot_from_north_true_tilt_comp_thresh_rising_hysteresis', 'in_rot_from_north_true_tilt_comp_thresh_falling_hysteresis', 'in_rot_from_north_true_tilt_comp_thresh_either_hysteresis', 'in_voltageY_thresh_rising_hysteresis', 'in_voltageY_thresh_falling_hysteresis', 'in_voltageY_thresh_either_hysteresis', 'in_tempY_thresh_rising_hysteresis', 'in_tempY_thresh_falling_hysteresis', 'in_tempY_thresh_either_hysteresis', 'in_illuminance0_thresh_falling_hysteresis', 'in_illuminance0_thresh_rising_hysteresis', 'in_illuminance0_thresh_either_hysteresis', 'in_proximity0_thresh_falling_hysteresis', 'in_proximity0_thresh_rising_hysteresis', 'in_proximity0_thresh_either_hysteresis', 'in_accel_x_raw_roc_rising_value', 'in_accel_x_raw_roc_falling_value', 'in_accel_y_raw_roc_rising_value', 'in_accel_y_raw_roc_falling_value', 'in_accel_z_raw_roc_rising_value', 'in_accel_z_raw_roc_falling_value', 'in_anglvel_x_raw_roc_rising_value', 'in_anglvel_x_raw_roc_falling_value', 'in_anglvel_y_raw_roc_rising_value', 'in_anglvel_y_raw_roc_falling_value', 'in_anglvel_z_raw_roc_rising_value', 'in_anglvel_z_raw_roc_falling_value', 'in_magn_x_raw_roc_rising_value', 'in_magn_x_raw_roc_falling_value', 'in_magn_y_raw_roc_rising_value', 'in_magn_y_raw_roc_falling_value', 'in_magn_z_raw_roc_rising_value', 'in_magn_z_raw_roc_falling_value', 'in_rot_from_north_magnetic_raw_roc_rising_value', 'in_rot_from_north_magnetic_raw_roc_falling_value', 'in_rot_from_north_true_raw_roc_rising_value', 'in_rot_from_north_true_raw_roc_falling_value', 'in_rot_from_north_magnetic_tilt_comp_raw_roc_rising_value', 'in_rot_from_north_magnetic_tilt_comp_raw_roc_falling_value', 'in_rot_from_north_true_tilt_comp_raw_roc_rising_value', 'in_rot_from_north_true_tilt_comp_raw_roc_falling_value', 'in_voltageY_supply_raw_roc_rising_value', 'in_voltageY_supply_raw_roc_falling_value', 'in_voltageY_raw_roc_rising_value', 'in_voltageY_raw_roc_falling_value', 'in_tempY_raw_roc_rising_value', 'in_tempY_raw_roc_falling_value', 'in_accel_x_thresh_rising_period', 'in_accel_x_thresh_falling_period', 'in_accel_x_roc_rising_period', 'in_accel_x_roc_falling_period', 'in_accel_y_thresh_rising_period', 'in_accel_y_thresh_falling_period', 'in_accel_y_roc_rising_period', 'in_accel_y_roc_falling_period', 'in_accel_z_thresh_rising_period', 'in_accel_z_thresh_falling_period', 'in_accel_z_roc_rising_period', 'in_accel_z_roc_falling_period', 'in_anglvel_x_thresh_rising_period', 'in_anglvel_x_thresh_falling_period', 'in_anglvel_x_roc_rising_period', 'in_anglvel_x_roc_falling_period', 'in_anglvel_y_thresh_rising_period', 'in_anglvel_y_thresh_falling_period', 'in_anglvel_y_roc_rising_period', 'in_anglvel_y_roc_falling_period', 'in_anglvel_z_thresh_rising_period', 'in_anglvel_z_thresh_falling_period', 'in_anglvel_z_roc_rising_period', 'in_anglvel_z_roc_falling_period', 'in_magn_x_thresh_rising_period', 'in_magn_x_thresh_falling_period', 'in_magn_x_roc_rising_period', 'in_magn_x_roc_falling_period', 'in_magn_y_thresh_rising_period', 'in_magn_y_thresh_falling_period', 'in_magn_y_roc_rising_period', 'in_magn_y_roc_falling_period', 'in_magn_z_thresh_rising_period', 'in_magn_z_thresh_falling_period', 'in_magn_z_roc_rising_period', 'in_magn_z_roc_falling_period', 'in_rot_from_north_magnetic_thresh_rising_period', 'in_rot_from_north_magnetic_thresh_falling_period', 'in_rot_from_north_magnetic_roc_rising_period', 'in_rot_from_north_magnetic_roc_falling_period', 'in_rot_from_north_true_thresh_rising_period', 'in_rot_from_north_true_thresh_falling_period', 'in_rot_from_north_true_roc_rising_period', 'in_rot_from_north_true_roc_falling_period', 'in_rot_from_north_magnetic_tilt_comp_thresh_rising_period', 'in_rot_from_north_magnetic_tilt_comp_thresh_falling_period', 'in_rot_from_north_magnetic_tilt_comp_roc_rising_period', 'in_rot_from_north_magnetic_tilt_comp_roc_falling_period', 'in_rot_from_north_true_tilt_comp_thresh_rising_period', 'in_rot_from_north_true_tilt_comp_thresh_falling_period', 'in_rot_from_north_true_tilt_comp_roc_rising_period', 'in_rot_from_north_true_tilt_comp_roc_falling_period', 'in_voltageY_supply_thresh_rising_period', 'in_voltageY_supply_thresh_falling_period', 'in_voltageY_supply_roc_rising_period', 'in_voltageY_supply_roc_falling_period', 'in_voltageY_thresh_rising_period', 'in_voltageY_thresh_falling_period', 'in_voltageY_roc_rising_period', 'in_voltageY_roc_falling_period', 'in_tempY_thresh_rising_period', 'in_tempY_thresh_falling_period', 'in_tempY_roc_rising_period', 'in_tempY_roc_falling_period', 'in_accel_x&y&z_mag_falling_period', 'in_intensity0_thresh_period', 'in_proximity0_thresh_period', 'in_activity_still_thresh_rising_period', 'in_activity_still_thresh_falling_period', 'in_activity_walking_thresh_rising_period', 'in_activity_walking_thresh_falling_period', 'in_activity_jogging_thresh_rising_period', 'in_activity_jogging_thresh_falling_period', 'in_activity_running_thresh_rising_period', 'in_activity_running_thresh_falling_period', 'in_illuminance_thresh_either_period', 'in_accel_thresh_rising_low_pass_filter_3db', 'in_anglvel_thresh_rising_low_pass_filter_3db', 'in_magn_thresh_rising_low_pass_filter_3db', 'in_accel_thresh_rising_high_pass_filter_3db', 'in_anglvel_thresh_rising_high_pass_filter_3db', 'in_magn_thresh_rising_high_pass_filter_3db', 'in_activity_still_thresh_rising_en', 'in_activity_still_thresh_falling_en', 'in_activity_walking_thresh_rising_en', 'in_activity_walking_thresh_falling_en', 'in_activity_jogging_thresh_rising_en', 'in_activity_jogging_thresh_falling_en', 'in_activity_running_thresh_rising_en', 'in_activity_running_thresh_falling_en', 'in_activity_still_thresh_rising_value', 'in_activity_still_thresh_falling_value', 'in_activity_walking_thresh_rising_value', 'in_activity_walking_thresh_falling_value', 'in_activity_jogging_thresh_rising_value', 'in_activity_jogging_thresh_falling_value', 'in_activity_running_thresh_rising_value', 'in_activity_running_thresh_falling_value', 'in_accel_mag_en', 'in_accel_mag_rising_en', 'in_accel_mag_falling_en', 'in_accel_x_mag_en', 'in_accel_x_mag_rising_en', 'in_accel_x_mag_falling_en', 'in_accel_y_mag_en', 'in_accel_y_mag_rising_en', 'in_accel_y_mag_falling_en', 'in_accel_z_mag_en', 'in_accel_z_mag_rising_en', 'in_accel_z_mag_falling_en', 'in_accel_x&y&z_mag_rising_en', 'in_accel_x&y&z_mag_falling_en', 'in_accel_raw_mag_value', 'in_accel_x_raw_mag_rising_value', 'in_accel_y_raw_mag_rising_value', 'in_accel_z_raw_mag_rising_value', 'in_accel_mag_referenced_en', 'in_accel_mag_referenced_rising_en', 'in_accel_mag_referenced_falling_en', 'in_accel_y_mag_referenced_en', 'in_accel_y_mag_referenced_rising_en', 'in_accel_y_mag_referenced_falling_en', 'in_accel_mag_referenced_value', 'in_accel_mag_referenced_rising_value', 'in_accel_mag_referenced_falling_value', 'in_accel_y_mag_referenced_value', 'in_accel_y_mag_referenced_rising_value', 'in_accel_y_mag_referenced_falling_value', 'in_steps_change_en', 'in_steps_change_value', 'in_illuminance_period_available', 'in_accel_gesture_singletap_en', 'in_accel_gesture_doubletap_en', 'in_accel_gesture_singletap_value', 'in_accel_gesture_doubletap_value', 'in_accel_gesture_tap_value_available', 'in_accel_gesture_singletap_reset_timeout', 'in_accel_gesture_doubletap_reset_timeout', 'in_accel_gesture_tap_reset_timeout_available', 'in_accel_gesture_doubletap_tap2_min_delay', 'in_accel_gesture_doubletap_tap2_min_delay_available', 'in_accel_gesture_tap_maxtomin_time', 'in_accel_gesture_tap_maxtomin_time_available', 'in_proximity_thresh_either_runningperiod', 'in_proximity_thresh_either_runningcount', 'in_altvoltageY_mag_either_label', 'in_altvoltageY_mag_rising_label', 'in_altvoltageY_thresh_falling_label', 'in_altvoltageY_thresh_rising_label', 'in_anglvelY_mag_rising_label', 'in_anglY_thresh_rising_label', 'in_phaseY_mag_rising_label', 'in_accel_gesture_tap_wait_timeout', 'in_accel_gesture_tap_wait_dur', 'in_accel_gesture_tap_wait_dur_available'], 'Trigger Attributes': ['sampling_frequency', 'sampling_frequency_available', 'current_trigger'], 'Buffer Attributes': ['sampling_frequency', 'sampling_frequency_available', 'in_capacitanceY_adaptive_thresh_rising_timeout', 'in_capacitanceY_adaptive_thresh_falling_timeout', 'length', 'enable', 'in_accel_x_en', 'in_accel_y_en', 'in_accel_z_en', 'in_deltaangl_x_en', 'in_deltaangl_y_en', 'in_deltaangl_z_en', 'in_deltavelocity_x_en', 'in_deltavelocity_y_en', 'in_deltavelocity_z_en', 'in_anglvel_x_en', 'in_anglvel_y_en', 'in_anglvel_z_en', 'in_magn_x_en', 'in_magn_y_en', 'in_magn_z_en', 'in_rot_from_north_magnetic_en', 'in_rot_from_north_true_en', 'in_rot_from_north_magnetic_tilt_comp_en', 'in_rot_from_north_true_tilt_comp_en', 'in_timestamp_en', 'in_voltageY_supply_en', 'in_voltageY_en', 'in_voltageY-voltageZ_en', 'in_incli_x_en', 'in_incli_y_en', 'in_pressureY_en', 'in_pressure_en', 'in_rot_quaternion_en', 'in_proximity_en', 'in_accel_type', 'in_deltaangl_type', 'in_deltavelocity_type', 'in_anglvel_type', 'in_magn_type', 'in_incli_type', 'in_voltageY_type', 'in_voltage_type', 'in_voltageY_supply_type', 'in_timestamp_type', 'in_pressureY_type', 'in_pressure_type', 'in_rot_quaternion_type', 'in_proximity_type', 'in_voltageY_index', 'in_voltageY_supply_index', 'in_accel_x_index', 'in_accel_y_index', 'in_accel_z_index', 'in_deltaangl_x_index', 'in_deltaangl_y_index', 'in_deltaangl_z_index', 'in_deltavelocity_x_index', 'in_deltavelocity_y_index', 'in_deltavelocity_z_index', 'in_anglvel_x_index', 'in_anglvel_y_index', 'in_anglvel_z_index', 'in_magn_x_index', 'in_magn_y_index', 'in_magn_z_index', 'in_rot_from_north_magnetic_index', 'in_rot_from_north_true_index', 'in_rot_from_north_magnetic_tilt_comp_index', 'in_rot_from_north_true_tilt_comp_index', 'in_incli_x_index', 'in_incli_y_index', 'in_timestamp_index', 'in_pressureY_index', 'in_pressure_index', 'in_rot_quaternion_index', 'in_proximity_index', 'watermark', 'data_available', 'hwfifo_enabled', 'hwfifo_timeout', 'hwfifo_watermark', 'hwfifo_watermark_min', 'hwfifo_watermark_max', 'hwfifo_watermark_available'], 'Missed Attributes': {'devices': 'triggerX'}}
HOST = "homeassistant"
PORT = 1883
CLIENTID = "client-1"
MAX_QOS_PACKET_ATTEMPTS = 10

STOP = Event()

class ControlHeaderType(IntEnum):
    CONNECT     = 0x10  # Client → Server
    CONNACK     = 0x20  # Server → Client
    PUBLISH     = 0x30  # Client or Server
    PUBACK      = 0x40
    PUBREC      = 0x50
    PUBREL      = 0x60
    PUBCOMP     = 0x70
    SUBSCRIBE   = 0x80
    SUBACK      = 0x90
    UNSUBSCRIBE = 0xA0
    UNSUBACK    = 0xB0
    PINGREQ     = 0xC0
    PINGRESP    = 0xD0
    DISCONNECT  = 0xE0

class MQTTFlags(IntEnum):
    RETAIN          = 0x01  # RETAIN = 1 (for PUBLISH)
    QOS1            = 0x02  # QoS level 1
    QOS2            = 0x04  # QoS level 2
    DUP             = 0x08  # DUP flag
    SUBSCRIBE_FLAG  = 0x02  # SUBSCRIBE requires QoS1 (0b0010)

# CONNECT flags bitfield (MQTT v3.1.1)
class MQTTConnectFlags(IntEnum):
    RESERVED       = 0x01            # must be 0
    CLEAN_SESSION  = 0x02            # bit 1
    WILL_FLAG      = 0x04            # bit 2
    WILL_RETAIN    = 0x20            # bit 5
    PASSWORD       = 0x40            # bit 6
    USERNAME       = 0x80            # bit 7

class HeaderType(IntEnum):
    CONNECT = 0

class MQTTWillQoS(IntEnum):
    QOS0    = (0 & 0x03) << 3   # Little hack to push the numbers in to bits 3 and 4
    QOS1    = (1 & 0x03) << 3
    QOS2    = (2 & 0x03) << 3



class MQTTProtocolLevel(IntEnum):
    V3_1_1 = 0x04


def constructControlHeader(packetType: ControlHeaderType, variableHeaderSize: int, payloadSize: int, flags: int = 0x00) -> bytearray:
    fixedHeader = bytearray()

    fixedHeader += (packetType | flags).to_bytes(1, byteorder='big')

    remainingLength = variableHeaderSize + payloadSize

    fixedHeader += encodeVarint(remainingLength)

    return fixedHeader

def constructVariableHeader(headerFlags: bytes) -> bytearray:

    '''
    Protocol Name Length 2x bytes
    Protocol Name
    Protocol Level i.e. version
    Content Flag 1x bytes
    Keep Alive
    '''

    variableHeader = bytearray()

    # Variable Header Boiler Plate

    protocolName = b"MQTT"

    variableHeader += len(protocolName).to_bytes(2, byteorder='big')
    variableHeader += protocolName
    variableHeader += MQTTProtocolLevel.V3_1_1.to_bytes(1, byteorder='big')
    variableHeader += headerFlags

    return variableHeader

def constructPayload(self, payload: str) -> bytearray:
    pass

class MQTTSocketClient:
    def __init__(self, clientID: str, username: str = None, password: str = None, host: str = "homeassistant", port: int = 1883, tls=False, keepalive=60, timeout=10):
        self.clientID = clientID
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.tls = tls
        self.keepalive = keepalive
        self.timeout = timeout
        self.sock: socket.socket = None
        self.last_receive = time.time()
        self.last_send = time.time()
        self.connectionTime = None
        self.packet_id = 1

    def __handle_tls(self):
        tlsHandler = ssl.create_default_context()
        return tlsHandler.wrap_socket(self.sock, server_hostname=self.host)

    def __receiveAmountOfBytes(self, n: int) -> bytes:
        packetChunks = []
        receivedBytes = 0

        while receivedBytes < n:
            packetChunk = self.sock.recv(n - receivedBytes)
            if not packetChunk:
                raise ConnectionError("Connection closed during receiving.")
            packetChunks.append(packetChunk)
            receivedBytes += len(packetChunk)

        self.last_receive = time.time()

        return b''.join(packetChunks)

    def __receive_packet(self) -> tuple[int, bytes]:

        byte1 = self.__receiveAmountOfBytes(1)[0]
        packetType = byte1 & 0xF0

        remaining = decodeVarint(self.__receiveAmountOfBytes)

        payload = self.__receiveAmountOfBytes(remaining) if remaining else b''

        return packetType, payload

    def __constructConnectPacket(self,  client_id: str, keepalive: int, username: str, password: str, will_topic: bytes, will_payload: bytes, will_retain: bool = True, clean_start: bool = True, will_qos: MQTTWillQoS = MQTTWillQoS.QOS1) -> bytes:

        # Construct CONNECT Packet Variable Header flags
        variableFlags = b'\x00'

        if clean_start:
            variableFlags = bitwiseOrForBytes(variableFlags, MQTTConnectFlags.CLEAN_SESSION.to_bytes(1, "big")) # cause supporting bitwise operations would make too much sense

        if username is not None:
            variableFlags = bitwiseOrForBytes(variableFlags, MQTTConnectFlags.USERNAME.to_bytes(1, "big"))

        if password is not None:
            variableFlags = bitwiseOrForBytes(variableFlags, MQTTConnectFlags.PASSWORD.to_bytes(1, "big"))


        willExists = (will_topic is not None) and (will_payload is not None)
        '''

        if willExists:
            pass
            #variableFlags = bitwiseOrForBytes(variableFlags, MQTTConnectFlags.WILL_FLAG.to_bytes())
            #variableFlags = bitwiseOrForBytes(variableFlags, will_qos.to_bytes())

            if will_retain:
                pass
                #variableFlags = bitwiseOrForBytes(variableFlags, MQTTConnectFlags.WILL_RETAIN.to_bytes())
        '''


        variableHeader = constructVariableHeader(variableFlags)

        # Add the keep alive timer
        variableHeader += struct.pack("!H", keepalive)


        # Construct Payload
        payload = bytearray()
        payload += len(client_id.encode("utf-8")).to_bytes(2, byteorder='big')
        payload += client_id.encode("utf-8")


        if username is not None:
            payload += len(username.encode("utf-8")).to_bytes(2, byteorder='big')
            payload += username.encode("utf-8")

        if password is not None:
            payload += len(password.encode("utf-8")).to_bytes(2, byteorder='big')
            payload += password.encode("utf-8")


        # Construct Fixed Header
        fixedHeader = constructControlHeader(ControlHeaderType.CONNECT, len(variableHeader), len(payload))

        print(f"Fixed Header: {fixedHeader}")
        print(f"Fixed Header Hex: {fixedHeader.hex()}")
        print(f"Variable Header: {variableHeader}")
        print(f"Variable Header Hex: {variableHeader.hex()}")
        print(f"Payload: {payload}")
        print(f"Payload Hex: {payload.hex()}")


        return fixedHeader + variableHeader + payload

    def __constructDisconnectPacket(self) -> bytes:
        return bytes([ControlHeaderType.DISCONNECT, 0])

    def __constructPingReqPacket(self) -> bytes:
        return bytes([ControlHeaderType.PINGREQ, 0x00])

    def __constructPublishPacket(self, topic: str, payloadIn: str, qosLevel: MQTTFlags, qosPacketIdentifier: int, duplicate: bool = False) -> bytes:
        '''
        Fixed Header                    Variable Header                 Payload
        PacketType - 4 Bits             Topic Name Length - 2 Bytes     Payload Length - 2 Bytes
        []                              Topic Name                      Data
        Flags - 4 Bits                  Packet Identifier(Qos > 0)
        [Duplicate, Qos, Retain]
        Remaining Length - 1-4 Bytes
        Retain Always True
        Duplicate - Input
        Qos - Input
        '''

        topicBytes = enc_utf8(topic)

        variableHeader = bytearray(topicBytes)

        if qosPacketIdentifier is not None:
            variableHeader += qosPacketIdentifier.to_bytes(2, byteorder='big')


        payload = payloadIn.encode('utf-8')

        controlFlags = 0x00
        controlFlags |= MQTTFlags.RETAIN
        controlFlags |= qosLevel
        if duplicate:
            controlFlags |= MQTTFlags.DUP

        fixedHeader = constructControlHeader(ControlHeaderType.PUBLISH, len(variableHeader), len(payload), controlFlags)

        return fixedHeader + variableHeader + payload

    def __constructPubRelPacket(self) -> bytes:
        return bytes([ControlHeaderType.PUBREL, 0x00])

    def __connect(self):

        self.sock = socket.create_connection((self.host, self.port), self.timeout)

        if self.tls:
            self.sock = self.__handle_tls()

        self.sock.settimeout(self.timeout)

        connectPacket = self.__constructConnectPacket(self.clientID, self.keepalive, self.username, self.password, b"home/bme680/status", b"offline")

        print(connectPacket)
        print(f"Connect Packet Hex: {connectPacket.hex()}")

        self.sock.sendall(connectPacket)
        self.last_send = time.time()
        self.connectionTime = self.last_send

        print("Connect Packet Sent")

        # Confirm The Connection
        connackPacket = self.__receive_packet()

        if connackPacket[0] == ControlHeaderType.CONNACK:
            print("Connack Packet Received")

        self.sock.sendall(self.__constructPingReqPacket())
        type, payload = self.__receive_packet()
        assert type == ControlHeaderType.PINGRESP and payload == b''

        print("CONNACK Packet Received")

    def __disconnect(self):
        self.sock.sendall(self.__constructDisconnectPacket())
        self.sock.close()
        self.sock = None

    def ping(self):
        pass

    def __publish(self, topicLevel: str, topicData, qosLevel: MQTTFlags):
        constructedTopics = {}

        if isinstance(topicData, (str, int, float, bool)):
            constructedTopics[topicLevel] = str(topicData)

        elif isinstance(topicData, dict):
            for key, value in topicData.items():
                constructedTopics[key] = str(value)

        successfulPackets = 0

        for key, value in constructedTopics.items():
            itterations = 1
            packet = self.__constructPublishPacket(key, value, qosLevel, itterations, False)

            if MQTTFlags.QOS1:
                while True:
                    self.sock.sendall(packet)
                    print(packet)
                    print(packet.hex())

                    inPacket = self.__receive_packet()

                    if inPacket[0] == ControlHeaderType.PUBACK:
                        successfulPackets += 1
                        print(f"PUBACK Packet Received. Successful Packets: {successfulPackets}")
                        break

                    itterations += 1
                    if itterations > MAX_QOS_PACKET_ATTEMPTS:
                        print(f"Max QoS1 Send Attempts Reached.\nPacket: {packet}")
                        break

                    packet = self.__constructPublishPacket(key, value, qosLevel, itterations, True)

            elif MQTTFlags.QOS2:
                while True:
                    self.sock.sendall(packet)
                    inPacket = self.__receive_packet()

                    if inPacket[0] == ControlHeaderType.PUBREC:
                        self.sock.sendall(self.__constructPubRelPacket())
                        inPacket == self.__receive_packet()
                        if inPacket[0] == ControlHeaderType.PUBCOMP:
                            successfulPackets += 1
                            break

                    itterations += 1
                    if itterations > MAX_QOS_PACKET_ATTEMPTS:
                        print(f"Max QoS1 Send Attempts Reached.\nPacket: {packet}")
                        break

                    packet = self.__constructPublishPacket(key, value, qosLevel, itterations, False)

    def run(self):
        print("Starting MQTT Client")
        try:
            self.__connect()
        except Exception as e:
            print(f"Failed to connect to MQTT server at {self.host}:{self.port}. Error: {e}")
            self.sock.close()
            quit()

        print("connection succeeded")

        sensorData = temp.parse_Data()

        bme680topic = "homeassistant/sensor/bme680/state"

        bme680config = {
            "homeassistant/sensor/bme680_temperature/config": {
                "name": "BME680 Temperature", "unique_id": "bme680_temperature",
                "state_topic": "homeassistant/sensor/bme680/state",
                "device_class": "temperature", "unit_of_measurement": "°F",
                "value_template": "{{ value_json.Temperature }}",
                "device": {"identifiers": ["bme680_bridge"], "name": "BME680 Bridge"},
                "availability_topic": "homeassistant/sensor/bme680/availability"
            },
            "homeassistant/sensor/bme680_humidity/config": {
                "name": "BME680 Humidity", "unique_id": "bme680_humidity",
                "state_topic": "homeassistant/sensor/bme680/state",
                "device_class": "humidity", "unit_of_measurement": "%",
                "value_template": "{{ value_json.Humidity }}",
                "device": {"identifiers": ["bme680_bridge"]},
                "availability_topic": "homeassistant/sensor/bme680/availability"
            },
            "homeassistant/sensor/bme680_pressure/config": {
                "name": "BME680 Pressure", "unique_id": "bme680_pressure",
                "state_topic": "homeassistant/sensor/bme680/state",
                "device_class": "pressure", "unit_of_measurement": "hPa",
                "value_template": "{{ value_json.Pressure }}",
                "device": {"identifiers": ["bme680_bridge"]},
                "availability_topic": "homeassistant/sensor/bme680/availability"
            },
            "homeassistant/sensor/bme680_gas/config": {
                "name": "BME680 Gas", "unique_id": "bme680_gas",
                "state_topic": "homeassistant/sensor/bme680/state",
                "unit_of_measurement": "Ω",
                "value_template": "{{ value_json.Gas }}",
                "device": {"identifiers": ["bme680_bridge"]},
                "availability_topic": "homeassistant/sensor/bme680/availability"
            }
        }

        payload = json.dumps(sensorData)


        for topic, config in bme680config.items():
            self.__publish(topic, json.dumps(config), MQTTFlags.QOS1)

        self.__publish("homeassistant/sensor/bme680/availability", "online", MQTTFlags.QOS1)
        self.__publish("homeassistant/sensor/bme680/state", payload, MQTTFlags.QOS1)


        for i in range(20, 0, -1):
            print(f"Stopping in {i}...")
            time.sleep(1)

        self.__disconnect()


client = MQTTSocketClient(CLIENTID, username="oniic", password="Saltersimp5904", host=HOST, port=PORT)
client.run()