import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
import time
import logging
import threading
import paho.mqtt.client as paho
from dash.dependencies import Input, Output 

global temperature
global humidity
global client
global thread1
global thread2
global light_state

broker = "localhost"
client = paho.Client("client-001")

temperature = 0
humidity = 50
light_state = 1


#Fetching the information from the MQTT server
def on_message(client, userdata, message):
    time.sleep(1)
    answer = message.payload.decode("utf-8")
    if message.topic == 'IoTlab/temperature':
        temperature = float(answer.lstrip())
        print("received temperature =", temperature)
    if message.topic == 'IoTlab/humidity':
        humidity = float(answer.lstrip())
        print("received humidity =", humidity)


#Setting up the MQTT server to receive temperature and humidity
def mqtt_server():
    client.subscribe("IoTlab/temperature")
    time.sleep(2)
    
    client.subscribe("IoTlab/humidity")
    time.sleep(2)
    
#Changing the light ON
def turn_light_on():
    print("publishing ")
    client.publish("IoTlab/light","ON")

#Changing the light OFF
def turn_light_off():
    print("publishing ")
    client.publish("IoTlab/light","OFF")



#Setup for the dashboard
external_stylesheets = ['style.css']
app = dash.Dash()

#Graphs
humidity = go.Figure(go.Indicator(
    mode = "gauge+number+delta",
    value = humidity,
    domain = {'x': [0, 1], 'y': [0, 1]},
    title = {'text': "Humidity"},
    gauge = {'axis': {'range': [None, 100]},
             'steps' : [
                 {'range': [0, 25], 'color': "#faff63"},
                 {'range': [25, 50], 'color': "#ff9a26"},
                 {'range': [50, 75], 'color': "#ff6224"},
                 {'range': [75, 100], 'color': "#ff2f1c"}
                 ],}
    ))
temperature = go.Figure(go.Indicator(
    mode = "gauge+number+delta",
    value = temperature,
    domain = {'x': [0, 1], 'y': [0, 1]},
    title = {'text': "Temperature"},
    gauge = {'axis': {'range': [-40, 40]},
             'steps' : [
                 {'range': [-40, -20], 'color': "#faff63"},
                 {'range': [-20, 0], 'color': "#ff9a26"},
                 {'range': [0, 20], 'color': "#ff6224"},
                 {'range': [20, 40], 'color': "#ff2f1c"}
                 ],}
    ))

#Draw the dashboard
app.layout = html.Div(children=[
    html.Div(id="title", children='Project Dashboard'),
    html.Button(id='light_toggle', children='Toggle Light'),
    dcc.Graph(id='humidity',figure=humidity),
    dcc.Graph(id='gauge',figure=temperature),
])

@app.callback(Output(component_id='title', component_property= 'children'),
              [Input(component_id='light_toggle', component_property= 'value')])
def update_light_state(value):
    light_state = 0
    if light_state == 1:
        turn_light_off()
        light_state = 0
    else:
        turn_light_on()
        light_state = 1
        print("hello from the callback")


def setup():
    client.on_message = on_message
    print("connecting to broker ",broker)
    client.connect(broker)

def run():
    setup()
    client.loop_start()
    mqtt_server()
    
    temperature = 10
    humidity = 70
    app.run_server(debug=True)

#Run the application
run()




# while True:
#     
#     while True:
#         client.loop_start()
#         mqtt_server()
#         
#         turn_button_on()
#         time.sleep(5)
#         turn_button_off()










