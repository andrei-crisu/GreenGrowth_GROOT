"""
Firebase Realtime Database - Read ESP32 Sensor Data

This module provides functionality to retrieve sensor data from Firebase Realtime Database.
Data structure: devices/{mac_address}/readings/{timestamp}/sensor_data

Example data format:
- mac_address: "004B1233F3E0"
- humidity: 45
- light_level: 335
- moisture: 32
- pressure: 1024
- temperature: 25
- timestamp: "2025-10-19T01:06:26"
"""

import json
from datetime import datetime
from app.firebase_client import get_db

def format_mac_address(mac_address):
    """
    Format MAC address from continuous string to proper format with colons.
    
    Args:
        mac_address (str): MAC address as continuous string (e.g., "004B1233F3E0")
    
    Returns:
        str: Properly formatted MAC address (e.g., "00:4B:12:33:F3:E0")
    """
    if not mac_address or len(mac_address) != 12:
        return mac_address
    
    # Convert to uppercase and add colons every 2 characters
    mac_upper = mac_address.upper()
    formatted = ':'.join([mac_upper[i:i+2] for i in range(0, 12, 2)])
    return formatted

def format_timestamp(timestamp_str):
    """
    Format timestamp from ISO format to user-friendly format.
    
    Args:
        timestamp_str (str): ISO timestamp (e.g., "2025-10-19T01:06:42")
    
    Returns:
        str: Formatted timestamp (e.g., "Oct 19, 2025 01:06:42")
    """
    if not timestamp_str or timestamp_str == 'N/A':
        return 'N/A'
    
    try:
        # Parse ISO format timestamp
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        # Format as "Oct 19, 2025 01:06:42"
        formatted = dt.strftime("%b %d, %Y %H:%M:%S")
        return formatted
    except (ValueError, TypeError):
        # If parsing fails, return original
        return timestamp_str

def sort_readings_by_timestamp(readings_dict):
    """
    Sort readings by timestamp key (most recent first).
    
    Args:
        readings_dict (dict): Dictionary of readings with timestamp keys
    
    Returns:
        list: Sorted list of (timestamp_key, reading) tuples
    """
    if not readings_dict:
        return []
    
    # Convert to list and sort by timestamp key as integer
    readings_list = list(readings_dict.items())
    
    # Sort by timestamp key (most recent first)
    # Handle both numeric and string timestamps
    def sort_key(item):
        timestamp_key = item[0]
        try:
            # Try to convert to integer first
            return int(timestamp_key)
        except (ValueError, TypeError):
            try:
                # Try to convert to float
                return float(timestamp_key)
            except (ValueError, TypeError):
                # If all else fails, use string comparison
                return timestamp_key
    
    sorted_readings = sorted(readings_list, key=sort_key, reverse=True)
    return sorted_readings


class SensorDataReader:
    def __init__(self):
        """Initialize sensor data reader with Firebase Realtime Database connection."""
        self.db = get_db()
        if not self.db:
            raise Exception("Firebase Realtime Database not initialized")
    
    def get_all_devices_data(self):
        """
        Retrieve all data from devices path
        
        Returns:
            dict: All device data organized by mac_address and timestamp
        """
        try:
            ref = self.db.child('devices')
            data = ref.get()
            
            if data:
                print(f"✅ Retrieved device data for {len(data)} devices")
                return data
            else:
                print("ℹ️ No device data found")
                return {}
            
        except Exception as e:
            print(f"❌ Error retrieving device data: {str(e)}")
            raise
    
    def get_device_data(self, mac_address):
        """
        Retrieve all sensor data for a specific device
        
        Args:
            mac_address (str): Device MAC address (e.g., "004B1233F3E0")
        
        Returns:
            dict: All sensor readings for the device, organized by timestamp
        """
        try:
            ref = self.db.child(f'devices/{mac_address}/readings')
            data = ref.get()
            
            if data:
                print(f"✅ Retrieved {len(data)} sensor readings for device {mac_address}")
                return data
            else:
                print(f"ℹ️ No data found for device {mac_address}")
                return {}
            
        except Exception as e:
            print(f"❌ Error retrieving device data: {str(e)}")
            raise
    
    def get_specific_reading(self, mac_address, timestamp):
        """
        Retrieve a specific sensor reading by device and timestamp
        
        Args:
            mac_address (str): Device MAC address
            timestamp (str or int): Timestamp key (e.g., "6286")
        
        Returns:
            dict: Sensor reading data
        """
        try:
            ref = self.db.child(f'devices/{mac_address}/readings/{timestamp}')
            data = ref.get()
            
            if data:
                print(f"✅ Retrieved sensor reading at timestamp {timestamp}")
                return data
            else:
                print(f"ℹ️ No data found for timestamp {timestamp}")
                return None
            
        except Exception as e:
            print(f"❌ Error retrieving specific reading: {str(e)}")
            raise
    
    def get_latest_readings(self, mac_address, limit=10):
        """
        Retrieve the latest N sensor readings for a device
        
        Args:
            mac_address (str): Device MAC address
            limit (int): Number of latest readings to retrieve
        
        Returns:
            dict: Latest sensor readings
        """
        try:
            ref = self.db.child(f'devices/{mac_address}/readings')
            # Query last N entries ordered by key (timestamp)
            query = ref.order_by_key().limit_to_last(limit)
            data = query.get()
            
            if data:
                print(f"✅ Retrieved {len(data)} latest readings for device {mac_address}")
                return data
            else:
                print(f"ℹ️ No data found for device {mac_address}")
                return {}
            
        except Exception as e:
            print(f"❌ Error retrieving latest readings: {str(e)}")
            raise
    
    def get_all_devices_list(self):
        """
        Get list of all available devices (MAC addresses)
        
        Returns:
            list: List of device MAC addresses
        """
        try:
            all_devices = self.get_all_devices_data()
            if all_devices:
                device_list = list(all_devices.keys())
                print(f"✅ Found {len(device_list)} devices")
                return device_list
            else:
                print("ℹ️ No devices found")
                return []
            
        except Exception as e:
            print(f"❌ Error retrieving devices list: {str(e)}")
            raise
    
    def get_device_summary(self, mac_address):
        """
        Get a summary of sensor data for a device
        
        Args:
            mac_address (str): Device MAC address
        
        Returns:
            dict: Summary statistics
        """
        try:
            device_data = self.get_device_data(mac_address)
            if not device_data:
                return {
                    'total_readings': 0,
                    'mac_address': mac_address,
                    'latest_temperature': None,
                    'latest_humidity': None,
                    'latest_pressure': None,
                    'latest_light_level': None,
                    'latest_moisture': None
                }
            
            temperatures = []
            humidities = []
            pressures = []
            light_levels = []
            moistures = []
            
            for timestamp, reading in device_data.items():
                if reading.get('temperature') is not None:
                    temperatures.append(float(reading['temperature']))
                if reading.get('humidity') is not None:
                    humidities.append(float(reading['humidity']))
                if reading.get('pressure') is not None:
                    pressures.append(float(reading['pressure']))
                if reading.get('light_level') is not None:
                    light_levels.append(float(reading['light_level']))
                if reading.get('moisture') is not None:
                    moistures.append(float(reading['moisture']))
            
            # Get latest values
            latest_reading = None
            if device_data:
                latest_timestamp = max(device_data.keys())
                latest_reading = device_data[latest_timestamp]
            
            summary = {
                'total_readings': len(device_data),
                'mac_address': mac_address,
                'latest_temperature': latest_reading.get('temperature') if latest_reading else None,
                'latest_humidity': latest_reading.get('humidity') if latest_reading else None,
                'latest_pressure': latest_reading.get('pressure') if latest_reading else None,
                'latest_light_level': latest_reading.get('light_level') if latest_reading else None,
                'latest_moisture': latest_reading.get('moisture') if latest_reading else None,
                'avg_temperature': sum(temperatures) / len(temperatures) if temperatures else None,
                'avg_humidity': sum(humidities) / len(humidities) if humidities else None,
                'avg_pressure': sum(pressures) / len(pressures) if pressures else None,
                'avg_light_level': sum(light_levels) / len(light_levels) if light_levels else None,
                'avg_moisture': sum(moistures) / len(moistures) if moistures else None
            }
            
            return summary
            
        except Exception as e:
            print(f"❌ Error generating device summary: {str(e)}")
            raise
    
    def format_sensor_reading(self, reading, timestamp_key=None):
        """
        Format a sensor reading for display
        
        Args:
            reading (dict): Sensor reading data
            timestamp_key (str): Optional timestamp key to display
        
        Returns:
            dict: Formatted sensor reading
        """
        if not reading:
            return {}
        
        # Format MAC address properly
        mac_address = reading.get('mac_address', 'N/A')
        if mac_address != 'N/A':
            mac_address = format_mac_address(mac_address)
        
        # Format timestamp properly
        timestamp = reading.get('timestamp', 'N/A')
        if timestamp != 'N/A':
            timestamp = format_timestamp(timestamp)
        
        formatted = {
            'timestamp_key': timestamp_key,
            'mac_address': mac_address,
            'temperature': reading.get('temperature', 'N/A'),
            'humidity': reading.get('humidity', 'N/A'),
            'pressure': reading.get('pressure', 'N/A'),
            'light_level': reading.get('light_level', 'N/A'),
            'moisture': reading.get('moisture', 'N/A'),
            'timestamp': timestamp
        }
        
        return formatted
