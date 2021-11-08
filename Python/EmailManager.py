import email
import imaplib
import smtplib
import time

import paho.mqtt.client as paho
import paho.mqtt.publish as publish
from paho.mqtt import client as mqtt_client

# Set up the global variables
global client
global no_response

# Set up the MQTT connection
client = paho.Client("client-001")
broker = 'localhost'
port = 1883
topic = "IoTlab/send_email"
client_id = "Client001"
response = False

# Set up email
smtp_server = "smtp.gmail.com"
sender_email = "waterisnoticecream@gmail.com"
receiver_email = "waterisnoticecream@gmail.com"
password = "Banana123!"


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


# Subscribe to the MQTT topic
def subscribe(client: mqtt_client):
    global no_response
    no_response = True

    # Is called whenever a message is received from the subscriptions
    def on_message(client, userdata, msg):
        if msg.topic == 'IoTlab/send_email':
            print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
            send_email("Would you like to turn on the fan? (YES or NO)")
            while no_response:
                email_watcher()
    client.subscribe("IoTlab/send_email")
    client.on_message = on_message


# Sends a message to the NodeMCU to turn the motor on
def turn_motor_on():
    print("Turning motor on...")
    publish.single("IoTlab/received_email", 'a')
    print("Turned motor on!")


# Sends a message to the NodeMCU to turn the motor off
def turn_motor_off():
    print("Turning motor off...")
    publish.single("IoTlab/received_email", 'b')
    print("Turned motor off!")


# Send an email to the user containing the desired text
def send_email(user_text):
    # Prepares the email
    sender_email = "waterisnoticecream@gmail.com"
    receiver_email = "waterisnoticecream@gmail.com"
    password = "Banana123!"
    subject = "Temperature has reached threshold!"
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


# The run method
def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


# Starts the main method and loops it
if __name__ == '__main__':
    run()
