# import email
# import imaplib
# import smtplib
# import time
#
# import paho.mqtt.client as paho
#
# global client
# global no_response
#
# broker = "localhost"
# client = paho.Client("client-001")
#
# response = False
#
# # Set up email
# smtp_server = "smtp.gmail.com"
# sender_email = "waterisnoticecream@gmail.com"
# receiver_email = "waterisnoticecream@gmail.com"
# password = "Banana123!"
#
#
# # Fetching the information from the MQTT server
# def on_message(client, userdata, message):
#     time.sleep(1)
#     answer = message.payload.decode("utf-8")
#     if message.topic == 'IoTlab/send_email':
#         print("Sending the email!")
#         sendEmail("Do you want to turn the light on ('Yes' or 'No')?")
#         response = False
#         while not response:
#             emailWatcher()
#
#
# # Setting up the MQTT server to receive temperature and humidity
# def mqtt_server():
#     client.subscribe("IoTlab/send_email")
#     time.sleep(2)
#
#
# # Turning motor ON
# def turn_motor_on():
#     print("Turning Motor On")
#     client.publish("IoTlab/motor", "ON")
#
#
# # Turning motor OFF
# def turn_motor_off():
#     print("Turning Motor Off")
#     client.publish("IoTlab/motor", "OFF")
#
#
# def sendEmail(userText):
#     sender_email = "waterisnoticecream@gmail.com"
#     receiver_email = "waterisnoticecream@gmail.com"
#     password = "Banana123!"
#     subject = "Would you like to turn on the fan? (YES or NO)"
#     text = userText
#
#     message = 'Subject: {}\n\n{}'.format(subject, text)
#
#     server = smtplib.SMTP('smtp.gmail.com', 587)
#     server.starttls()
#     server.login(sender_email, password)
#     server.sendmail(sender_email, receiver_email, message)
#     print("\nEmail has been sent to ", receiver_email)
#     time.sleep(2)
#
#
# def emailWatcher():
#     numberOfEmails = 0
#
#     while True:
#         mail = imaplib.IMAP4_SSL('imap.gmail.com')
#         mail.login('waterisnoticecream@gmail.com', 'Banana123!')
#         mail.list()
#         mail.select("inbox")
#         result, data = mail.search(None, "ALL")
#
#         ids = data[0]
#         id_list = ids.split()
#         print("Watching the inbox...")
#
#         if len(id_list) > numberOfEmails:
#             numberOfEmails = len(id_list)
#             latest_email_id = id_list[-1]
#             result, data = mail.fetch(latest_email_id, "(RFC822)")
#             raw_data = (data[0][1]).decode("utf-8")
#             decoded_data = email.message_from_string(raw_data)
#
#             if type(decoded_data.get_payload()[0]) is str:
#                 break
#             else:
#                 print("\nWe received an Email!")
#                 bodytext = decoded_data.get_payload()[0].get_payload();
#
#             if len(bodytext) >= 2:
#                 if str(bodytext[0:3]).upper() == "YES":
#                     print("On!\n")
#                 else:
#                     print("We will not turn on the fan then!")
#             else:
#                 print("Invalid entry!\n")
#
#         time.sleep(3)
#
#
# def setup():
#     client.on_message = on_message
#     print("connecting to broker ", broker)
#     client.connect(broker)
#
#
# def run():
#     setup()
#     client.loop_start()
#     mqtt_server()
#
#
# # Run the application
# run()

import email
import imaplib
import smtplib
import time

import paho.mqtt.client as paho
from paho.mqtt import client as mqtt_client

global client
global no_response

broker = "localhost"
client = paho.Client("client-001")

response = False

# Set up email
smtp_server = "smtp.gmail.com"
sender_email = "waterisnoticecream@gmail.com"
receiver_email = "waterisnoticecream@gmail.com"
password = "Banana123!"



broker = 'localhost'
port = 1883
topic = "IoTlab/send_email"
client_id = "Client001"


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


def subscribe(client: mqtt_client):
    global no_response
    no_response = True

    def on_message(client, userdata, msg):
        if msg.topic == 'IoTlab/send_email':
            print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
            sendEmail("Would you like to turn on the fan? (YES or NO)")
            while no_response:
                emailWatcher()

    client.subscribe("IoTlab/send_email")
    client.on_message = on_message


def turn_motor_on():
    client.publish("IoTlab/received_email", "YES")


def turn_motor_off():
    client.publish("IoTlab/received_email", "NO")


def sendEmail(userText):
    sender_email = "waterisnoticecream@gmail.com"
    receiver_email = "waterisnoticecream@gmail.com"
    password = "Banana123!"
    subject = "Temperature has reached threshold!"
    text = userText

    message = 'Subject: {}\n\n{}'.format(subject, text)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message)
    print("\nEmail has been sent to ", receiver_email)
    time.sleep(2)


def emailWatcher():
    global no_response
    numberOfEmails = 0

    while True:
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login('waterisnoticecream@gmail.com', 'Banana123!')
        mail.list()
        mail.select("inbox")
        result, data = mail.search(None, "ALL")

        ids = data[0]
        id_list = ids.split()
        print("Watching the inbox...")

        if len(id_list) > numberOfEmails:
            numberOfEmails = len(id_list)
            latest_email_id = id_list[-1]
            result, data = mail.fetch(latest_email_id, "(RFC822)")
            raw_data = (data[0][1]).decode("utf-8")
            decoded_data = email.message_from_string(raw_data)

            if type(decoded_data.get_payload()[0]) is str:
                break
            else:
                print("\nWe received an Email!")
                bodytext = decoded_data.get_payload()[0].get_payload();

            if len(bodytext) >= 2:
                if str(bodytext[0:3]).upper() == "YES":
                    print("We will turn the fan on!\n")
                    turn_motor_on()
                else:
                    print("We will not turn on the fan then!")
                    turn_motor_off()
                run()
            else:
                print("Invalid entry!\n")
        time.sleep(3)

def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    run()
