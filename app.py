"""
A small Test application to show how to use Flask-MQTT.
"""

import eventlet
import json
from flask import Flask, render_template, current_app, abort, jsonify, make_response, request
from flask_mqtt import Mqtt
from flask_socketio import SocketIO
from flask_bootstrap import Bootstrap
from flask_restful import Api, Resource
from datetime import datetime

eventlet.monkey_patch()

app = Flask(__name__)
api = Api(app)
app.config['SECRET'] = 'my secret key'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['MQTT_BROKER_URL'] = 'broker.hivemq.com'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_CLIENT_ID'] = 'flask_mqtt'
app.config['MQTT_USERNAME'] = ''
app.config['MQTT_PASSWORD'] = ''
app.config['MQTT_KEEPALIVE'] = 5
app.config['MQTT_TLS_ENABLED'] = False
app.config['MQTT_LAST_WILL_TOPIC'] = 'home/lastwill'
app.config['MQTT_LAST_WILL_MESSAGE'] = 'bye'
app.config['MQTT_LAST_WILL_QOS'] = 2

mqtt = Mqtt(app)
socketio = SocketIO(app)
bootstrap = Bootstrap(app)


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('publish')
def handle_publish(json_str):
    data = json.loads(json_str)
    mqtt.publish(data['topic'], data['message'])


@socketio.on('subscribe')
def handle_subscribe(json_str):
    data = json.loads(json_str)
    mqtt.subscribe(data['topic'])


@socketio.on('unsubscribe_all')
def handle_unsubscribe_all():
    mqtt.unsubscribe_all()


@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )
    print(data)
    socketio.emit('mqtt_message', data=data)


@mqtt.on_log()
def handle_logging(client, userdata, level, buf):
    # print(level, buf)
    pass

class ReceiveMessage(Resource):
    #TEMP VARIABLE TO STORE INCOMING MESSAGE
    message_list = []
    def get(self):
        return make_response(jsonify(self.message_list))

    
    def post(self):
        data = request.json
        #ONLY SAVE THE MESSAGE IF HAVE 'topic' and 'message' keys in BODY
        if 'topic' in data.keys() and 'message' in data.keys():
            topic= data['topic']
            message= data['message']
            self.message_list.append({'topic':topic, 'message':message, 'timestamp':datetime.now()})
            #PUBLISH MESSAGE TO BROKER
            mqtt.publish(topic, message)

            response_text= 'Ok, message inserted'
            status_code=200
        else:
            response_text= 'Error, "topic" or "message" key not exist in body'
            status_code=500
        return make_response(jsonify(response_text), status_code)

#ENDPOINT API TO POST AND GET ALL MESSAGE
api.add_resource(ReceiveMessage, '/message')


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, use_reloader=True, debug=True)
