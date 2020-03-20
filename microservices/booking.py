from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from os import environ
import requests

import pika
import json
app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://flight_admin:6kKVm7C2PHtVtgGT@esd-g7t6-rds.cs2kfkrucphj.ap-southeast-1.rds.amazonaws.com:3306/flight_booking'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 1800}

db = SQLAlchemy(app)
CORS(app)

flightURL = 'http://localhost:5001/flight/receive_choice'
passengerURL = 'http://localhost:5002'
pricingURL = 'http://localhost:5003/pricing/receive'

# TODO communication between Booking microservice and Booking UI
# TODO communication between Booking microservice and Paypal API

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
    return jsonify({"bookings": [booking.json() for booking in Booking.query.all()]})


@app.route("/booking/<string:pid>")
def get_booking_by_pid(pid):
    all_booking = Booking.query.filter_by(pid=pid).all()
    # Translates to Select... WHERE>... LIMIT 1
    
    if all_booking:
        return jsonify([booking.json() for booking in all_booking])

    return jsonify({"message": "Book not found."}), 404


@app.route("/booking/create", methods=['POST'])
def create_booking():
    data = request.get_json()
    
    pid = data['pid']
    flightNo = data['flightNo']
    departDate = data['departDate']
    class_type = data['class_type']
    baggage = data['baggage']
    meal = data['meal']

    base_price = choose_flight(flightNo)['basePrice']

    add_on_price = get_price(meal, baggage, class_type)
    meal_price = add_on_price['meal_price']
    baggage_price = add_on_price['baggage_price']
    class_type_percentage = add_on_price['class_type_percentage']

    total_price = (base_price + meal_price + baggage_price) * class_type_percentage

    booking = Booking(
        pid = data['pid'],
        flightNo = data['flightNo'],
        departDate = data['departDate'],
        price = total_price,
        class_type = data['class_type'],
        baggage = data['baggage'],
        meal = data['meal']
    )

    try:
        db.session.add(booking)
        db.session.commit()
        print('a')
    except:
        print('a2')
        return jsonify({"message": "An error occurred creating the book."}), 500

    return jsonify(booking.json()), 201


@app.route("/booking/send/<string:pid>")
def send_booking(pid):
    return


def get_flight_detail(departDest, arrivalDest):
    details = json.loads(json.dumps({"departDest" : departDest, "arrivalDest" : arrivalDest}, default = str))
    r = requests.post(flightURL, json = details)
    result = json.loads(r.text)
    if result['status'] == 200:
        print(result['flight'])
        return result['flight']

def choose_flight(flightNo):
    details = json.loads(json.dumps({"flightNo" : flightNo}, default = str))
    r = requests.post(flightURL, json = details)
    result = json.loads(r.text)
    if result['status'] == 200:
        print(result['flight'])
        return result['flight']
    

def get_price(meal_id, baggage_id, class_type):
    details = json.loads(json.dumps({"meal_id" : meal_id, "baggage_id" : baggage_id, "class_type" : class_type}, default = str))
    r = requests.post(pricingURL, json = details)
    result = json.loads(r.text)
    if result['status'] == 200:
        print(result)
        return result

'''

BOOKING TO NOTIFICATION
COMMUNICATION TECHNOLOGIES AMQP

'''

# get booking details by booking reference code
@app.route("/booking/<int:refCode>")
def get_booking_by_refCode(refCode):
    booking = Booking.query.filter_by(refCode=refCode).first()
    if booking:
        return jsonify(booking.json())
    return jsonify({"message": "Passenger not found"}), 404

# create content (boarding pass details) to be sent to email
# TODO i change function name here, please update your code accordingly 
# so that it's not hardcoded like this
def create_booking_for_notification():

    # call passenger microservice api to get passenger details 
    passenger_url = 'http://127.0.0.1:5002/passenger/pid_0004'
    passenger = requests.get(passenger_url).json()
    json_dump = json.dumps(passenger)
    passenger_data = json.loads(json_dump)
    first_name = passenger_data['firstName']
    last_name = passenger_data['lastName']
    email = passenger_data['email']

    # call flight microservice api to get flight details 
    flight_url = 'http://127.0.0.1:5001/flight/200'
    flight = requests.get(flight_url).json()
    json_dump = json.dumps(flight)
    flight_data = json.loads(json_dump)
    arrival_dest  = flight_data['arrivalDest']
    dept_dest  = flight_data['departDest']
    dept_time = flight_data['deptTime']
    flight_no = flight_data['flightNo']

    booking = {
        'first name': first_name,
        'last name': last_name,
        'flight no': flight_no,
        "depart time": dept_time,
        'depart destination': dept_dest ,
        'arrival destination':arrival_dest,
        'email': email
    }
    return booking


# send Booking to Notification through AMQP
def send_booking(booking):
    """send booking, flight and passenger details to Notification """
    hostname = "localhost"
    port = 5672
    # connect to the broker and set up a communication channel in the connection
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=hostname, port=port))
    channel = connection.channel()
 
    # set up the exchange if the exchange doesn't exist
    exchangename="booking_direct"
    channel.exchange_declare(exchange=exchangename, exchange_type='direct')

    # prepare the message body content
    message = json.dumps(booking, default=str) # convert a JSON object to a string

    # send message to Notifications
    # prepare the channel and send a message to Notifications
    channel.queue_declare(queue='notification', durable=True)
    # make sure the queue is bound to the exchange
    channel.queue_bind(exchange=exchangename, queue='notification', routing_key='notification.booking')
    channel.basic_publish(exchange=exchangename, routing_key="notification.booking", body=message,
        properties=pika.BasicProperties(delivery_mode = 2, 
        )
    )
    # close the connection to the broker
    connection.close()

if __name__ == "__main__":
    # booking = create_booking()
    # send_booking(booking)
    app.run(port=5000, debug=True)