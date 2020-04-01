from flask import Flask, request, jsonify, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
import random
import requests

import pika
import json
app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://flight_admin:6kKVm7C2PHtVtgGT@esd-g7t6-rds.cs2kfkrucphj.ap-southeast-1.rds.amazonaws.com:3306/flight_booking'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 1800}

db = SQLAlchemy(app)


flightURL = 'http://localhost:5001/flight/receive_choice'
passengerURL = 'http://localhost:5002'
pricingURL = 'http://localhost:5003/pricing/receive'
billingURL = 'http://localhost:5004/billing'

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
    seat_number = db.Column(db.String(5))

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
            "meal": self.meal,
            "seatNumber": self.seat_number
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
        return jsonify([booking.json() for booking in all_booking]), 200

    return jsonify({"message": "Booking not found."}), 404


@app.route("/booking/assignSeat/<string:refCode>")
def assign_seat_for_booking(refCode):
    print(f'refCode: {refCode}')
    booking = Booking.query.filter_by(refCode=refCode).first()
    # booking = session.query(Booking).filter(Booking.refCode==refCode).one()

    print(booking.json())

    # Translates to Select... WHERE>... LIMIT 1
    seat_columns = ['A', 'B', 'C', 'D', 'E', 'F']
    seat_rows = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30']
    all_seats = []
    for one_num in seat_rows: # 1, 2, 3
        for one_letter in seat_columns: # A, B, C
            all_seats.append(one_letter + one_num)
    # all_seats = ['A1', 'B2' .... ]
    # all_seats -= [all assigned seats]
    
    
    flightCode = booking.flightNo
    flightDate = booking.departDate # '2020-03-15'
    print(f'flightCode : {flightCode}')
    print(f'flightDate : {flightDate}')

    assigned_seats = [booking.seat_number for booking in Booking.query.filter_by(flightNo=flightCode, departDate=flightDate).all() if booking.seat_number != '']
    print(assigned_seats)

    for one_seat in assigned_seats:
        if one_seat in all_seats:
            all_seats.remove(one_seat)
    # print(all_seats[:80])
    booking.seat_number = all_seats[0]
    
    try: 
        db.session.commit()
    except:
        return jsonify({"message": "An error occurred when assigning seats."}), 500

    return jsonify(booking.json()), 200 


@app.route("/booking/filter", methods=['POST'])
def get_booking_by_flightCode_date():
    
    data = request.get_json()
    print(data)
    flightCode = data["flightCode"]
    date = data["date"]
    # print(f'flightCode: {flightCode}')
    # print(f'date: {date}')
    
    selected_booking = Booking.query.filter_by(flightNo=flightCode, departDate=date).all()
    # for b in selected_booking:
    #     print(b.departDate)
    #     print(type(b.departDate)) # <class 'datetime.date'>
    
    if selected_booking:
        return jsonify([booking.json() for booking in selected_booking]), 200

    return jsonify([]), 201 # return empty list 

    # return jsonify({"message": "Bookings not found."}), 404
    

@app.route("/booking/create", methods=['POST'])
def create_booking():
    data = request.get_json()
    
    pid = data['pid'] # SESSION
    flightNo = data['flightNo'] 
    departDate = data['departDate']
    base_price = data['base_price'] 
    class_type = data['class_type']
    baggage = data['baggage']
    meal = data['meal']

    # base_price = choose_flight(flightNo)['basePrice']

    add_on_price = get_price(meal, baggage, class_type)
    meal_price = add_on_price['meal_price']
    baggage_price = add_on_price['baggage_price']
    class_type_percentage = add_on_price['class_type_percentage']

    total_price = (base_price + meal_price + baggage_price) * class_type_percentage/100

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
        
    except:
        return jsonify({"message": "An error occurred creating the booking."}), 500

    return jsonify(booking.json()), 201 # send to Booking UI (confirm page)


# this function currently not in use (based on new diagram)
def get_flight_detail(departDest, arrivalDest):
    details = json.loads(json.dumps({"departDest" : departDest, "arrivalDest" : arrivalDest}, default = str))
    r = requests.post(flightURL, json = details)
    result = json.loads(r.text)
    if result['status'] == 200:
        # print(result['flight'])
        return result['flight']
    

def get_price(meal_id, baggage_id, class_type):
    details = json.loads(json.dumps({"meal_id" : meal_id, "baggage_id" : baggage_id, "class_type" : class_type}, default = str))
    r = requests.post(pricingURL, json = details)
    result = json.loads(r.text)
    if result['status'] == 200:
        print(result)
        return result

@app.route('/booking/<int:refCode>')
def get_booking_by_refCode(refCode):
    booking = Booking.query.filter_by(refCode=refCode).first()
    if booking:
        url2 = 'http://localhost:5001/flight/' +str(booking.flightNo)
        r2 = requests.get(url2)
        result2 = json.loads(r2.text)
        return_json = {"pid": booking.pid, "refCode" : booking.refCode, "flightNo": booking.flightNo, "departDate" :booking.departDate, "deptTime": result2['flight']['deptTime'], "class_type": booking.class_type, "seat_number": booking.seat_number, "price":booking.price }

        return {"booking": return_json, "status": 200}
    return jsonify({"message": "Booking not found"}), 404



# @app.route("/booking/confirm", methods=['POST'])
# def booking_confirm():
#     data = request.get_json()
    
#     refCode = data['refCode']
#     pid = data['pid']
#     flightNo = data['flightNo']
#     departDate = data['departDate']
#     class_type = data['class_type']
#     baggage = data['baggage']
#     meal = data['meal']
#     price = data['price']

#     send_price = json.loads(json.dumps(
#         {"refCode":refCode, "pid":pid, 
#         "flightNo":flightNo, "departDate":departDate,
#         "price":price, "class_type":class_type, 
#         "baggage":baggage,"meal":meal}, 
#         default = str))
#     r = requests.post(billingURL, json = send_price)
#     return r.text

@app.route("/booking/confirm/<string:price>/<string:refCode>", methods=['GET'])
def booking_confirm(price, refCode):
    send_price = json.loads(json.dumps({"price" : price, "refCode":refCode} , default = str))
    r = requests.post(billingURL, json = send_price)
    return r.text
 

@app.route("/booking/status", methods=['POST'])
def get_status():
    data = request.get_json()
    status = data['status']
    refCode = data['refCode']
    
    if status == "yes":
        return jsonify({"message": "Successful payment. Booking confirm!"}), 201

    if status == "no":
        Booking.query.filter_by(refCode = refCode).delete()
        db.session.commit()
    else:
        message = create_message(refCode)
        send_booking(message)
    return status, refCode


@app.route("/booking/checkin/<string:refCode>", methods=['GET'])
def create_checkin_status(refCode):
    # data = request.get_json()
    # refCode = data['refCode']
    ls =['yes', 'no']
    status = random.choice(ls)
    if status == 'yes':
        seat = assign_seat_for_booking(refCode)

    return render_template("checkin.html", refCode = refCode, status = status)

@app.route("/booking/boarding/<string:refCode>", methods=['GET'])
def get_boarding(refCode):
    return render_template("boarding.html", refCode = refCode)

# @app.route("/manage")
# def manage_booking(): 
#     return render_template("manage_booking.html")


'''

BOOKING TO NOTIFICATION
COMMUNICATION TECHNOLOGIES AMQP

'''

# get booking details by booking reference code
@app.route("/booking/message/<int:refCode>")
def create_message(refCode):
    booking = Booking.query.filter_by(refCode=refCode).first()
    if booking:
        url1 = passengerURL + "/passenger/" + str(booking.pid)
        r1 = requests.get(url1)
        result1 = json.loads(r1.text)
        url2 = 'http://localhost:5001/flight/' +str(booking.flightNo)
        r2 = requests.get(url2)
        result2 = json.loads(r2.text)
        return_json = {"name": result1['firstName'] + " " + result1['lastName'], "email" : result1['email'], "refCode" : refCode, "flightNo": booking.flightNo, "departDate" :booking.departDate, "deptTime": result2['flight']['deptTime'], "price":booking.price, "class_type": booking.class_type, "seat_number": booking.seat_number }
        return return_json
    return jsonify({"message": "Passenger not found"}), 404


# send Booking to Notification through AMQP
def send_booking(message):
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
    message = json.dumps(message, default=str) # convert a JSON object to a string

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
    # this part i still hardcoded bc need to get passenger id when logged in from frontend but frontend not up yet
    # booking = create_booking_for_notification('pid_0004')
    # send_booking(booking)
    app.run(port=5000, debug=True)