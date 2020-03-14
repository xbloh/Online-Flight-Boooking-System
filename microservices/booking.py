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
    def __init__(self, pid, flightNo, departDate, price, class_type, baggage, meal):
        self.pid = pid
        self.flightNo = flightNo
        self.departDate = departDate
        self.price = price
        self.class_type = class_type
        self.baggage = baggage
        self.meal = meal

    def json(self):
        return {
            "pid": self.pid,
            "flightNo": self.flightNo,
            "departDate": self.departDate,
            "price": self.price,
            "class_type": self.class_type,
            "baggage": self.baggage,
            "meal": self.meal
        }


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
    
    # return jsonify({'jesus': 'take the wheel'})
    if all_booking:
        return jsonify([booking.json() for booking in all_booking])

    return jsonify({"message": "Book not found."}), 404


if __name__ == "__main__":
    app.run(port=5001, debug=True)
