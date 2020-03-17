'''
Created by Jia Cheng
2020/03/14 

Purpose: 
    - flight bookings - micro service
'''

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import environ

import pika
import json
app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://flight_admin:6kKVm7C2PHtVtgGT@esd-g7t6-rds.cs2kfkrucphj.ap-southeast-1.rds.amazonaws.com:3306/flight_booking'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 1800}

db = SQLAlchemy(app)
CORS(app)


class Booking(db.Model):

    __tablename__ = 'booking'

    refCode = db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.String(20), nullable=False)
    flightNo = db.Column(db.String(8), nullable=False)
    departDate = db.Column(db.DateTime(), nullable=False)
    price = db.Column(db.Float, nullable=False)
    class_type = db.Column(db.String(20), nullable=False)
    baggage = db.Column(db.Integer)
    meal = db.Column(db.Integer)

    # (pid, flightNo, departDate, price, class_type, baggage, meal)
    # def __init__(self, refCode, pid, flightNo, departDate, price, class_type, baggage, meal):
    #     self.refCode = refCode
    #     self.pid = pid
    #     self.flightNo = flightNo
    #     self.departDate = departDate
    #     self.price = price
    #     self.class_type = class_type
    #     self.baggage = baggage
    #     self.meal = meal

    def json(self):
        return {
            "refCode": self.refCode,
            "pid": self.pid,
            "flightNo": self.flightNo,
            "departDate": self.departDate,
            "price": self.price,
            "class_type": self.class_type,
            "baggage": self.baggage,
            "meal": self.meal
        }

# booking = {
#     "baggage": 2,
#     "class_type": "short_economy",
#     "departDate": "Sun, 15 Mar 2020 00:00:00 GMT",
#     "flightNo": "200",
#     "meal": 1,
#     "pid": "pid_0002",
#     "price": 128,
#     "refCode": 5
#     }


@app.route("/booking")
def get_all():
    '''
    Returns GET
    # 127.0.0.1 - - [16/Jan/2020 14:27:52] "GET /book HTTP/1.1" 200 -
    '''

    return jsonify({"bookings": [booking.json() for booking in Booking.query.all()]})


@app.route("/booking/<string:pid>")
def get_booking_by_pid(pid):
    all_booking = Booking.query.filter_by(pid=pid).all()
    # Translates to Select... WHERE>... LIMIT 1
    
    if all_booking:
        return jsonify([booking.json() for booking in all_booking])

    return jsonify({"message": "Book not found."}), 404


@app.route("/booking/create/", methods=['POST'])
def create_booking():
    # if (Book.query.filter_by(isbn13=isbn13).first()):
    #     return jsonify({"message": "A book with isbn13 '{}' already exists.".format(isbn13)}), 400
    '''
    SQL Statement:
    INSERT INTO `flight_booking`.`booking` (`pid`, `flightNo`, `departDate`, `price`, `class_type`, `baggage`, `meal`) VALUES ('pid_0001', '200', '2020-03-15', '128', 'short_economy', '2', '1');

    '''
    data = request.get_json()
    # It comes in as a <class 'dict'>
    # for k, v in data.items():
    #     print(f'{k} : {v}')
    # pid : pid_0001
    # flightNo : 200
    # departDate : 2020-03-15
    # price : 128
    # class_type : short_economy
    # baggage : 2
    # meal : 1
    # print(data)
    # print(jsonify(data))
    booking = Booking(
        pid=data['pid'],
        flightNo=data['flightNo'],
        departDate=data['departDate'],
        price=data['price'],
        class_type=data['class_type'],
        baggage=data['baggage'],
        meal=data['meal']
    )

    try:
        db.session.add(booking)
        db.session.commit()
    except:
        return jsonify({"message": "An error occurred creating the book."}), 500

    return jsonify(booking.json()), 201


@app.route("/booking/send/<string:pid>")
def send_booking(pid):
    booking = get_booking_by_pid(pid)
    print('send booking')
    print(booking)
    # default username / password to the borker are both 'guest'
    hostname = "localhost" # default broker hostname. Web management interface default at http://localhost:15672
    port = 5672 # default messaging port.
    # connect to the broker and set up a communication channel in the connection
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=hostname, port=port))
        # Note: various network firewalls, filters, gateways (e.g., SMU VPN on wifi), may hinder the connections;
        # If "pika.exceptions.AMQPConnectionError" happens, may try again after disconnecting the wifi and/or disabling firewalls
    channel = connection.channel()

    # set up the exchange if the exchange doesn't exist
    exchangename="booking_direct"
    channel.exchange_declare(exchange=exchangename, exchange_type='direct')

    # prepare the message body content
    message = json.dumps(booking, default=str) # convert a JSON object to a string

    # send the message
    # always inform Monitoring for logging no matter if successful or not
    # channel.basic_publish(exchange=exchangename, routing_key="shipping.info", body=message)
        # By default, the message is "transient" within the broker;
        #  i.e., if the monitoring is offline or the broker cannot match the routing key for the message, the message is lost.
        # If need durability of a message, need to declare the queue in the sender (see sample code below).

    # if "status" in order: # if some error happened in order creation
    #     # inform Error handler
    #     channel.queue_declare(queue='errorhandler', durable=True) # make sure the queue used by the error handler exist and durable
    #     channel.queue_bind(exchange=exchangename, queue='errorhandler', routing_key='shipping.error') # make sure the queue is bound to the exchange
    #     channel.basic_publish(exchange=exchangename, routing_key="shipping.error", body=message,
    #         properties=pika.BasicProperties(delivery_mode = 2) # make message persistent within the matching queues until it is received by some receiver (the matching queues have to exist and be durable and bound to the exchange)
    #     )
    #     print("Order status ({:d}) sent to error handler.".format(order["status"]))
    # else: # inform Shipping and exit, leaving it to order_reply to handle replies
    #     # Prepare the correlation id and reply_to queue and do some record keeping
    #     corrid = str(uuid.uuid4())
    #     row = {"order_id": order["order_id"], "correlation_id": corrid}
    #     csvheaders = ["order_id", "correlation_id", "status"]
    #     with open("corrids.csv", "a+", newline='') as corrid_file: # 'with' statement in python auto-closes the file when the block of code finishes, even if some exception happens in the middle
    #         csvwriter = csv.DictWriter(corrid_file, csvheaders)
    #         csvwriter.writerow(row)
    #     replyqueuename = "shipping.reply"
    #     # prepare the channel and send a message to Shipping
    channel.queue_declare(queue='pricing', durable=True) # make sure the queue used by Shipping exist and durable
    channel.queue_bind(exchange=exchangename, queue='pricing', routing_key='pricing.booking') # make sure the queue is bound to the exchange
    channel.basic_publish(exchange=exchangename, routing_key="pricing.booking", body=message,
        properties=pika.BasicProperties(delivery_mode = 2, # make message persistent within the matching queues until it is received by some receiver (the matching queues have to exist and be durable and bound to the exchange, which are ensured by the previous two api calls)
            # reply_to=replyqueuename, # set the reply queue which will be used as the routing key for reply messages
            # correlation_id=corrid # set the correlation id for easier matching of replies
        )
    )
    # print("Order sent to shipping.")
    # close the connection to the broker
    connection.close()
    print('close')


if __name__ == "__main__":
    app.run(port=5000, debug=True)
    # send_booking(booking)