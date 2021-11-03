import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html

from paho.mqtt import client as mqtt_client

#MQTT connection
broker = 'localhost'
port = 1883
topic = "room/light"
topic2 = "IoTlab/temperature"
topic3 = "IoTlab/humidity"
client_id = "1234"

#MQTT methods used for the connection to the client
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
    answer = 0
    def on_message(client, userdata, msg):
        answer = msg.payload.decode()
        answer = float(answer.lstrip())
    print("something")
    client.subscribe(topic2)
    client.on_message = on_message
    
    #return answer


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()



# #Setup for the dashboard
# external_stylesheets = ['style.css']
# app = dash.Dash()
# 
# #Graphs
# humidity = go.Figure(go.Indicator(
#     mode = "gauge+number+delta",
#     value = 79,
#     domain = {'x': [0, 1], 'y': [0, 1]},
#     title = {'text': "Humidity"},
#     gauge = {'axis': {'range': [None, 100]},
#              'steps' : [
#                  {'range': [0, 25], 'color': "#faff63"},
#                  {'range': [25, 50], 'color': "#ff9a26"},
#                  {'range': [50, 75], 'color': "#ff6224"},
#                  {'range': [75, 100], 'color': "#ff2f1c"}
#                  ],}
#     ))
# temperature = go.Figure(go.Indicator(
#     mode = "gauge+number+delta",
#     value = 5,
#     domain = {'x': [0, 1], 'y': [0, 1]},
#     title = {'text': "Temperature"},
#     gauge = {'axis': {'range': [-40, 40]},
#              'steps' : [
#                  {'range': [-40, -20], 'color': "#faff63"},
#                  {'range': [-20, 0], 'color': "#ff9a26"},
#                  {'range': [0, 20], 'color': "#ff6224"},
#                  {'range': [20, 40], 'color': "#ff2f1c"}
#                  ],}
#     ))
# 
# #Draw the gauges
# app.layout = html.Div(children=[
#     html.H1(children='Project Dashboard'),
#     html.Button('Toggle Light'),
#     dcc.Graph(id='humidity',figure=humidity),
#     dcc.Graph(id='gauge',figure=temperature),
# ])

#Run the dashboard
if __name__ == '__main__':
    #app.run_server(debug=True)
    run()