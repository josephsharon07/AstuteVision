import network
import urequests
import time
from machine import Pin, UART, PWM
from dfplayermini import Player


# Define global variables
button = None
button1 = None
vib = None
music = None
detected = None

# Voice command mappings
voice_commands = {
    10: 1,
    20: 2,
    50: 3,
    100: 4,
    200: 5,
    500: 6,
    2000: 7,
    0: 9,
    -1: 8
}

# Vibration patterns for each denomination
patterns = {
    10: [0.2],
    20: [0.2, 0.2],
    50: [0.2, 0.2, 0.2],
    100: [0.2, 0.8],
    200: [0.2, 0.2, 0.8],
    500: [0.2, 0.2, 0.2, 0.8],
    2000: [0.2, 0.2, 0.2, 0.2, 0.8],
    0: [0.8, 0.8],
    -1: [0.8]
}

# Function to connect to Wi-Fi
def connect_to_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)  # Create a station interface
    wlan.active(True)  # Activate the interface
    wlan.connect(ssid, password)  # Connect to the specified network

    print("Connecting to WiFi...", end="")
    while not wlan.isconnected():  # Wait until the connection is established
        print(".", end="")
        time.sleep(1)
    print("\nConnected to WiFi!")
    print("Network configuration:", wlan.ifconfig())

# Function to play a voice command based on the detected denomination
def play_voice_command(denomination):
    try:
        command_number = voice_commands.get(denomination)
        if command_number:
            music.play(command_number)
            print("Playing voice command for denomination ", denomination)
        else:
            print("No voice command found for the detected denomination.")
    except Exception as e:
        print("Error playing voice command:", e)

# Function to handle button press for voice command
def handle_button1_press():
    global detected
    if detected is not None:
        play_voice_command(detected)
    else:
        print("No denomination detected.")

# Function to vibrate in a pattern based on the detected denomination
def vibrate_pattern(denomination):
    pattern = patterns.get(denomination, [0.0, 0.0])
    for duration in pattern:
        vib.on()
        time.sleep(duration)
        vib.off()
        time.sleep(0.1)

# Main function
def main():
    global button, button1, vib, music, detected

    time.sleep(5)
    connect_to_wifi("hackathon", "spectrawifi")
    time.sleep(1)

    button = Pin(6, Pin.IN, Pin.PULL_UP)
    print("Button 1 Initiated")
    time.sleep(1)
    
    ir = Pin(17, Pin.IN, Pin.PULL_UP)
    print("IR Sensor")
    time.sleep(1)

    button1 = Pin(7, Pin.IN, Pin.PULL_UP)
    print("Button 2 Initiated")
    time.sleep(1)

    vib = Pin(9, Pin.OUT)
    print("Vibrator Initiated")
    time.sleep(1)
    
    music = Player(pin_TX=12, pin_RX=13)
    print("Player Initiated")
    time.sleep(1)

    vib.on()
    time.sleep(3)
    vib.off()

    try:
        while True:
            if not button.value():
                if not ir.value():
                    detected = 0
                    handle_button1_press()
                    vibrate_pattern(detected)
                else:
                    print("Button Pressed!...")
                    detected = int(urequests.get("http://192.168.20.237:5050/predictions").text)
                    vibrate_pattern(detected)
                    if detected == -1:
                        handle_button1_press()
                    else:
                        print("Detected denomination:", detected)
                        vibrate_pattern(detected)
                        time.sleep(1)

            if not button1.value():
                handle_button1_press()
                time.sleep(2)

    except Exception as e:
        print("An error occurred:", e)

# Start the main function
if __name__ == "__main__":
    main()
