import streamlit as st
import serial
import time
import pandas as pd

# Set page configuration
st.set_page_config(page_title="DHT11 Data Logger", page_icon=":chart_with_upwards_trend:")

# Replace with the correct port for your Arduino
serial_port = '/dev/cu.usbserial-110'  # Change this to the actual port you found

try:
    ser = serial.Serial(serial_port, 9600)  # Connect to Arduino over serial
    time.sleep(2)  # Wait for the serial connection to initialize
except serial.SerialException as e:
    st.error(f"Error: {e}")
    ser = None

# Header section
st.title("DHT11 Data Logger")

if ser:
    # Display real-time data
    st.header("Real-time Data")

    start_logging = st.button("Start Logging")

    if start_logging:
        stop_logging = st.button("Stop Logging")
        placeholder = st.empty()  # Create an empty container

        # Initialize lists to store readings
        temperatures = []
        humidities = []
        timestamps = []

        chart_placeholder = st.empty()  # Placeholder for the chart

        while not stop_logging:
            # Read data from serial
            if ser.in_waiting > 0:
                data = ser.readline().decode('utf-8').strip()

                try:
                    temperature, humidity = data.split(',')
                    temperature = float(temperature)
                    humidity = float(humidity)

                    # Append new readings to the lists
                    temperatures.append(temperature)
                    humidities.append(humidity)
                    timestamps.append(time.time())

                    # Create a DataFrame from the lists
                    data_dict = {
                        "Timestamp": timestamps,
                        "Temperature (°C)": temperatures,
                        "Humidity (%)": humidities
                    }
                    df = pd.DataFrame(data_dict)
                    df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='s')

                    # Update the placeholder with new data
                    with placeholder.container():
                        st.subheader("Updated every 5 seconds")
                        st.write(f"**Temperature:** {temperature} °C")
                        st.write(f"**Humidity:** {humidity} %")

                    # Update the chart less frequently (every 10 seconds)
                    if len(timestamps) % 2 == 0:  # Update chart every 10 seconds
                        with chart_placeholder.container():
                            st.line_chart(df.set_index('Timestamp'))
                    
                except ValueError:
                    st.error("Received data is not in the expected format: 'temperature,humidity'")
                
                time.sleep(5)  # Refresh every 5 seconds

            else:
                time.sleep(0.1)  # Add a small delay to avoid busy-waiting

else:
    st.write("Could not open serial port.")
