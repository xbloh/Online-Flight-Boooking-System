from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import environ
import pika
import json

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://flight_admin:6kKVm7C2PHtVtgGT@esd-g7t6-rds.cs2kfkrucphj.ap-southeast-1.rds.amazonaws.com:3306/flight_pricing'

# set dbURL=mysql+mysqlconnector://root@localhost:3306/book

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 1800}

db = SQLAlchemy(app)
CORS(app)

class Baggage(db.Model):
    __tablename__ = 'baggage'

    baggage_id = db.Column(db.Integer, primary_key=True)
    baggage_desc = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __init__(self, baggage_id, baggage_desc, price):
        self.baggage_id = baggage_id
        self.baggage_desc = baggage_desc
        self.price = price

    def json(self):
        return {
            "baggage_id": self.baggage_id,
            "baggage_desc": self.baggage_desc,
            "price": self.price
        }

class Class_type(db.Model):
    __tablename__ = 'class_type'

    class_name = db.Column(db.String(20), primary_key=True)
    percentage = db.Column(db.Float, nullable=False)

    def __init__(self, class_name, price):
        self.class_name = class_name
        self.percentage = percentage

    def json(self):
        return {
            "class_name": self.class_name,
            "percentage": self.percentage
        }

class Meal(db.Model):
    __tablename__ = 'meal'

    meal_id = db.Column(db.Integer, primary_key=True)
    meal_desc = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __init__(self, meal_id, meal_desc, price):
        self.meal_id = meal_id
        self.meal_desc = meal_desc
        self.price = price

    def json(self):
        return {
            "meal_id": self.meal_id,
            "meal_desc": self.meal_desc,
            "price": self.price
        }


# Setting up for Communication AMQP Direct
hostname = "localhost" # default hostname
port = 5672 # default port
# connect to the broker and set up a communication channel in the connection
connection = pika.BlockingConnection(pika.ConnectionParameters(host=hostname, port=port))
    # Note: various network firewalls, filters, gateways (e.g., SMU VPN on wifi), may hinder the connections;
    # If "pika.exceptions.AMQPConnectionError" happens, may try again after disconnecting the wifi and/or disabling firewalls
channel = connection.channel()
# set up the exchange if the exchange doesn't exist
exchangename="booking_direct"
channel.exchange_declare(exchange=exchangename, exchange_type='direct')

def receiveBooking():
    print('receiving  booking')
    # prepare a queue for receiving messages
    channelqueue = channel.queue_declare(queue="pricing", durable=True) # 'durable' makes the queue survive broker restarts so that the messages in it survive broker restarts too
    queue_name = channelqueue.method.queue
    channel.queue_bind(exchange=exchangename, queue=queue_name, routing_key='pricing.booking') # bind the queue to the exchange via the key

    # set up a consumer and start to wait for coming messages
    channel.basic_qos(prefetch_count=1) # The "Quality of Service" setting makes the broker distribute only one message to a consumer if the consumer is available (i.e., having finished processing and acknowledged all previous messages that it receives)
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True) # 'auto_ack=True' acknowledges the reception of a message to the broker automatically, so that the broker can assume the message is received and processed and remove it from the queue
    channel.start_consuming() # an implicit loop waiting to receive messages; it doesn't exit by default. Use Ctrl+C in the command window to terminate it.

def callback(channel, method, properties, body): # required signature for the callback; no return
    print("Received an order by " + __file__)
    result = processBooking(json.loads(body))
    # print processing result; not really needed
    json.dump(result, sys.stdout, default=str) # convert the JSON object to a string and print out on screen
    print() # print a new line feed to the previous json dump
    print() # print another new line as a separator

    # prepare the reply message and send it out
    replymessage = json.dumps(result, default=str) # convert the JSON object to a string
    replyqueuename="pricing.reply"
    # A general note about AMQP queues: If a queue or an exchange doesn't exist before a message is sent,
    # - the broker by default silently drops the message;
    # - So, if really need a 'durable' message that can survive broker restarts, need to
    #  + declare the exchange before sending a message, and
    #  + declare the 'durable' queue and bind it to the exchange before sending a message, and
    #  + send the message with a persistent mode (delivery_mode=2).
    channel.queue_declare(queue=replyqueuename, durable=True) # make sure the queue used for "reply_to" is durable for reply messages
    channel.queue_bind(exchange=exchangename, queue=replyqueuename, routing_key=replyqueuename) # make sure the reply_to queue is bound to the exchange
    channel.basic_publish(exchange=exchangename,
            routing_key=properties.reply_to, # use the reply queue set in the request message as the routing key for reply messages
            body=replymessage, 
            properties=pika.BasicProperties(delivery_mode = 2, # make message persistent (stored to disk, not just memory) within the matching queues; default is 1 (only store in memory)
                correlation_id = properties.correlation_id, # use the correlation id set in the request message
            )
    )
    channel.basic_ack(delivery_tag=method.delivery_tag) # acknowledge to the broker that the processing of the request message is completed

def processBooking(booking): 

    # booking now is a json object, turn it into a dictionary:
    booking_dict = json.loads(booking)
    print("Processing booking:")
    print(booking)
    print(booking_dict)

    meal = booking_dict['meal']
    baggage = booking_dict['baggage']
    class_type = booking_dict['class_type']

     #get meal, baggage, class price
    meal_price = get_meal_price(meal)
    baggage_price = get_baggage_price(baggage)
    class_price = get_class_price(class_type)

    #compute total price for add-ons
    total_addon_price = meal_price + baggage_price 

    channel.queue_declare(queue='pricing', durable=True) # make sure the queue used by the error handler exist and durable
    channel.queue_bind(exchange=exchangename, queue='pricing', routing_key='pricing.booking') # make sure the queue is bound to the exchange
    channel.basic_publish(exchange=exchangename, routing_key="pricing.booking", body=total_addon_price,
        properties=pika.BasicProperties(delivery_mode = 2) # make message persistent within the matching queues until it is received by some receiver (the matching queues have to exist and be durable and bound to the exchange)
    )

# End of communication setting


@app.route("/pricing")
def get_all():
    return jsonify({
        "baggages": [baggage.json() for baggage in Baggage.query.all()],
        "classes": [class_type.json() for class_type in Class_type.query.all()],
        "meals": [meal.json() for meal in Meal.query.all()]
        })

@app.route("/pricing/baggage/<int:baggage_id>")
def get_baggage_price(baggage_id):
    baggage = Baggage.query.filter_by(baggage_id=baggage_id).first()
    if baggage:
        return jsonify(baggage.json())
    return jsonify({"message": "Couldn't find baggage"}), 404

@app.route("/pricing/meal/<int:meal_id>")
def get_meal_price(meal_id):
    meal = Meal.query.filter_by(meal_id=meal_id).first()
    if meal:
        return jsonify(meal.json())
    return jsonify({"message": "Couldn't find meal"}), 404

@app.route("/pricing/class/<string:class_name>")
def get_class_price(class_name):
    class_name = Class_type.query.filter_by(class_name=class_name).first()
    if class_name:
        return jsonify(class_name.json())
    return jsonify({"message": "Couldn't find class type"}), 404





if __name__ == "__main__":
    app.run(port=5001, debug=True)
    
