from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import environ
import json

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://flight_admin:6kKVm7C2PHtVtgGT@esd-g7t6-rds.cs2kfkrucphj.ap-southeast-1.rds.amazonaws.com:3306/flight_name'

# set dbURL=mysql+mysqlconnector://root@localhost:3306/book

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 1800}

db = SQLAlchemy(app)
CORS(app)


class Flight(db.Model):
    __tablename__ = 'flight'

    flightNo = db.Column(db.String(8), primary_key=True)
    departDest = db.Column(db.String(5), nullable=False)
    arrivalDest = db.Column(db.String(5), nullable=False)
    deptTime = db.Column(db.DateTime, nullable=False)
    arrivalTime = db.Column(db.DateTime, nullable=False)
    basePrice = db.Column(db.String(30), nullable=False)
    type = db.Column(db.String(1), nullable=False)

    def __init__(self, flightNo, departDest, arrivalDest, deptTime, arrivalTime, basePrice, type):
        self.flightNo = flightNo
        self.departDest = departDest
        self.arrivalDest = arrivalDest
        self.deptTime = deptTime
        self.arrivalTime = arrivalTime
        self.basePrice = basePrice
        self.type = type

    def json(self):
        return {
            "flightNo" : self.flightNo,
            "departDest" : self.departDest,
            "arrivalDest" : self.arrivalDest,
            "deptTime" : str(self.deptTime),
            "arrivalTime" : str(self.arrivalTime),
            "basePrice" : self.basePrice,
            "type" : self.type
        }


@app.route("/flight")
def get_all():
    '''
    Returns GET
    # 127.0.0.1 - - [16/Jan/2020 14:27:52] "GET /book HTTP/1.1" 200 -
    '''

    # print('get all books')
    # return 'get all books'

    # print([book.json() for book in Book.query.all()])
    return {"flight": [flight.json() for flight in Flight.query.all()]}

@app.route("/flight/<string:departDest>/<string:arrivalDest>")
def get_flight_by_dept_arr(departDest, arrivalDest):
    flights = Flight.query.filter_by(departDest=departDest, arrivalDest=arrivalDest)
    if len(flights.all()) != 0:
        return {"flight": [flight.json() for flight in flights]}
    return jsonify({"message": "Flight not found."}), 404

@app.route("/flight/<string:flightNo>")
def get_flight_by_flight_no(flightNo):
    flight = Flight.query.filter_by(flightNo=flightNo).first()
    if flight:
        return jsonify(flight.json())
    return jsonify({"message": "Passenger not found"}), 404

if __name__ == "__main__":
    app.run(port=5001, debug=True)

