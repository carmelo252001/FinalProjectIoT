import email
import imaplib
import smtplib
import time
import bluetooth
import bluetooth._bluetooth as bt
import struct
import array
import fcntl
import os
import json
import re
import RPi.GPIO as GPIO
import paho.mqtt.client as paho
import paho.mqtt.publish as publish
from paho.mqtt import client as mqtt_client
from datetime import datetime

# Set up the global variables
global client
global no_response

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.OUT)
GPIO.setup(23, GPIO.OUT)
GPIO.setup(24, GPIO.OUT)
GPIO.setup(25, GPIO.OUT)

# Set up the MQTT connection
client = paho.Client("client-001")
broker = 'localhost'
port = 1883
client_id = "Client001"
response = False

# Set up email
smtp_server = "smtp.gmail.com"
sender_email = "waterisnoticecream@gmail.com"
receiver_email = "waterisnoticecream@gmail.com"
password = "Banana123!"

#Threshold for the RSSI for Bluetooth
desired_rssi = 0


# Connect to the MQTT client
def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


# Subscribe to the MQTT topic and waits for messages
def subscribe(client: mqtt_client):
    global no_response
    no_response = True

    # Is called whenever a message is received from the subscriptions
    def on_message(client, userdata, msg):
        global desired_rssi
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")

        if msg.topic == 'IoTlab/send_email':
            print("Received a message from send email.")
            send_email("Would you like to turn on the fan? (YES or NO)")
            while no_response:
                email_watcher()
        elif msg.topic == 'IoTlab/buzzer':
            print("Received a message from buzzer.")
            turn_buzzer_on()
        elif msg.topic == 'IoTlab/message_carmelo':
            print("Received a message from message_carmelo.")
            message = "At " + current_time + " time, Carmelo was here."
            send_email(message)
        elif msg.topic == 'IoTlab/message_akash':
            print("Received a message from message_akash.")
            message = "At " + current_time + " time, Akash was here."
            send_email(message)
        elif msg.topic == 'IoTlab/get_bluetooth':
            print("The dashboard is requesting the Bluetooth information.")
            bluetooth_information()
            print("Information has been sent.")
        elif msg.topic == 'IoTlab/desired_rssi':
            print(f"Received a new desired RSSI: `{msg.payload.decode()}`")
            desired_rssi = msg.payload.decode()
            print("The new desired RSSI is: " + desired_rssi)

    client.subscribe("IoTlab/send_email")
    client.subscribe("IoTlab/buzzer")
    client.subscribe("IoTlab/message_carmelo")
    client.subscribe("IoTlab/message_akash")
    client.subscribe("IoTlab/get_bluetooth")
    client.subscribe("IoTlab/desired_rssi")
    client.on_message = on_message


# Gets the Bluetooth information
def bluetooth_information():
    global desired_rssi
    devices = os.system('sudo node bluetooth-fetcher.js > output.txt')
    deviceList = []
    rssiList = []
    informationDict = {}
    with open('output.txt',encoding='utf-8-sig', errors='ignore') as devices:
         sp = devices.read().splitlines()
        
    for line in sp:
        rssi = 0;
        transmitterId = "";
        if "transmitterId:" in line:
            transmitterId = line.split("'")[1::2]
            deviceList.append(transmitterId)
        if "rssi:" in line:
            rssi = int(re.search(r'\d+', line).group(0))
            rssiList.append(rssi)
    for i in range(len(deviceList)):
        informationDict[deviceList[i][0]] = rssiList[i]
    
    number_devices = 0
    print("There devices are available: " + str(informationDict))
    
    for x in informationDict:
        print("This is the RSSI: " + str(x) + " with RSSI: " + str(informationDict.get(x)) + " with Desired: " + str(desired_rssi))
        if str(informationDict.get(x)) > str(desired_rssi):
            number_devices = number_devices + 1
    
    print("There are: " + str(number_devices) + " devices.")
    if number_devices is not None:
        publish.single("IoTlab/bluetooth_information", int(number_devices))
    else:
        publish.single("IoTlab/bluetooth_information", 0)


# Turns the motor on
def turn_motor_on():
    print("Turning motor on...")
    publish.single("IoTlab/received_email", 'a')
    print("Starting the motor")
    GPIO.output(23, GPIO.HIGH)
    GPIO.output(24, GPIO.LOW)
    GPIO.output(25, GPIO.HIGH)
    print("Turned motor on!")


# Turns the motor off
def turn_motor_off():
    print("Turning motor off...")
    publish.single("IoTlab/received_email", 'b')   
    print("Done closing the motor")
    GPIO.output(25, GPIO.LOW)
    GPIO.cleanup()
    print("Turned motor on!")
    print("Turned motor off!")


# Sets the buzzer on for 3 seconds before turning off again
def turn_buzzer_on():
    print("Turning buzzer on!")
    GPIO.output(21, True)
    time.sleep(3)
    GPIO.output(21, False)
    GPIO.cleanup()
    print("Turned buzzer off!")


# Send an email to the user containing the desired text
def send_email(user_text):
    # Prepares the email
    sender_email = "waterisnoticecream@gmail.com"
    receiver_email = "waterisnoticecream@gmail.com"
    password = "Banana123!"
    subject = "Message from the Dashboard"
    text = user_text
    message = 'Subject: {}\n\n{}'.format(subject, text)

    # Sends the email
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message)
    print("\nEmail has been sent to ", receiver_email)
    time.sleep(2)


# Waits for a response from the user in the form of an email
def email_watcher():
    global no_response
    number_of_emails = 0

    while True:
        # Sets up the connection to the email
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login('waterisnoticecream@gmail.com', 'Banana123!')
        mail.list()
        mail.select("inbox")
        result, data = mail.search(None, "ALL")

        ids = data[0]
        id_list = ids.split()
        print("Watching the inbox...")

        # Waits for a new email to arrive before getting into the analysis
        if len(id_list) > number_of_emails:
            # Looks at the new email and gets the body out of it
            number_of_emails = len(id_list)
            latest_email_id = id_list[-1]
            result, data = mail.fetch(latest_email_id, "(RFC822)")
            raw_data = (data[0][1]).decode("utf-8")
            decoded_data = email.message_from_string(raw_data)

            # Makes sure the body is of a valid type to analyze
            if type(decoded_data.get_payload()[0]) is str:
                break
            else:
                print("\nWe received an Email!")
                body_text = decoded_data.get_payload()[0].get_payload()

            # Makes sure the message is long enough before verifying it
            if len(body_text) >= 2:
                # Verifies what is the content of the new email
                if str(body_text[0:3]).upper() == "YES":
                    print("We will turn the fan on!\n")
                    turn_motor_on()
                else:
                    print("We will not turn on the fan then!")
                    turn_motor_off()
                run()
            else:
                print("Invalid entry!\n")
        time.sleep(3)

#bluetooth_information()
# The run method
def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


# Starts the main method and loops it
if __name__ == '__main__':
    run()
