import tkinter as tk
from tkinter import ttk, font
import paho.mqtt.client as mqtt
from PIL import Image, ImageTk

# MQTT Broker details
MQTT_BROKER = "broker.hivemq.com"  # Replace with your broker address
MQTT_PORT = 1883
MQTT_TOPICS = [
    "sensor/rain",
    "sensor/dht",
    "sensor/soil"
]

# Global variables to store sensor values
rain_value = 0
temperature_value = 0
humidity_value = 0
soil_moisture_value = 0

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker")
    for topic in MQTT_TOPICS:
        client.subscribe(topic)

def on_message(client, userdata, msg):
    global rain_value, temperature_value, humidity_value, soil_moisture_value
    payload = msg.payload.decode()
    print(f"Received `{payload}` from `{msg.topic}`")

    if msg.topic == "sensor/rain":
        rain_value = int(payload)
        if rain_value == 0:
            rain_status = "Rain Detected"
        else:
            rain_status = "Rain Not Detected"
        update_card(rain_card, rain_status, "rain_icon.jpg")
    elif msg.topic == "sensor/dht":
        data = payload.split(", ")
        temperature_value = float(data[0].split(": ")[1].replace(" *C", ""))
        humidity_value = float(data[1].split(": ")[1].replace(" %", ""))
        update_card(temp_card, f"Temperature: {temperature_value}°C", "temp_icon.jpg")
        update_card(humidity_card, f"Humidity: {humidity_value}%", "humidity_icon.png")
    elif msg.topic == "sensor/soil":
        soil_moisture_value = int(payload)
        if soil_moisture_value == 1:
            soil_status = "Soil Needs Water"
        else:
            soil_status = "Soil Moisture is OK"
        update_card(soil_card, soil_status, "soil_icon.png")

# Function to update cards with new data
def update_card(card, text, icon_path):
    # Update icon
    icon = Image.open(icon_path)
    icon = icon.resize((50, 50), Image.LANCZOS)
    icon = ImageTk.PhotoImage(icon)
    card.icon_label.config(image=icon)
    card.icon_label.image = icon  # Keep a reference to avoid garbage collection

    # Update text
    card.text_label.config(text=text)

# Tkinter GUI Setup
root = tk.Tk()
root.title("IoT Sensor Dashboard")
root.geometry("400x500")
root.configure(bg="#f0f0f0")

bg_image = Image.open("farm_background.jpg")  # Replace with your image path
bg_image = bg_image.resize((800, 600), Image.LANCZOS)
bg_image = ImageTk.PhotoImage(bg_image)
bg_label = tk.Label(root, image=bg_image)
bg_label.place(relwidth=1, relheight=1)

# Custom font
custom_font = font.Font(family="Helvetica", size=12, weight="bold")

# Function to create a card
def create_card(parent, icon_path, initial_text):
    frame = tk.Frame(parent, bg="white", bd=2, relief="groove")
    frame.pack(fill="x", padx=10, pady=10, ipadx=10, ipady=10)

    # Icon
    icon = Image.open(icon_path)
    icon = icon.resize((50, 50), Image.LANCZOS)
    icon = ImageTk.PhotoImage(icon)
    icon_label = tk.Label(frame, image=icon, bg="white")
    icon_label.image = icon  # Keep a reference
    icon_label.pack(side="left", padx=10)

    # Text
    text_label = tk.Label(frame, text=initial_text, bg="white", font=custom_font)
    text_label.pack(side="left", padx=10)

    # Store references
    frame.icon_label = icon_label
    frame.text_label = text_label

    return frame

# Create cards for each sensor
rain_card = create_card(root, "rain_icon.jpg", "Rain Status: Unknown")
temp_card = create_card(root, "temp_icon.jpg", "Temperature: 0°C")
humidity_card = create_card(root, "humidity_icon.png", "Humidity: 0%")
soil_card = create_card(root, "soil_icon.png", "Soil Moisture: Unknown")

# Initialize MQTT Client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Start MQTT Loop
client.loop_start()

# Run Tkinter Main Loop
root.mainloop()

# Stop MQTT Loop on exit
client.loop_stop()