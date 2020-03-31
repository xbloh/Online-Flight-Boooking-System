from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import environ
from passlib.hash import sha256_crypt, pbkdf2_sha256
import json,sys,os,datetime
# Communication patterns:
# Use HTTP calls to enable interaction
import requests

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://flight_admin:6kKVm7C2PHtVtgGT@esd-g7t6-rds.cs2kfkrucphj.ap-southeast-1.rds.amazonaws.com:3306/flight_passenger'

# set dbURL=mysql+mysqlconnector://root@localhost:3306/book

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 1800}

db = SQLAlchemy(app)
CORS(app)


class Passenger(db.Model):
    __tablename__ = 'passenger'

    pid = db.Column(db.String(20), primary_key=True)
    password = db.Column(db.String(20), nullable=False)
    firstName = db.Column(db.String(10), nullable=False)
    lastName = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30), nullable=False)
    dateOfBirth = db.Column(db.String(30), nullable=False)
    contactNo = db.Column(db.Integer)

    def __init__(self, email, password, pid, firstName, lastName, dateOfBirth, contactNo):
        self.pid = pid
        self.firstName = firstName
        self.password = password
        self.lastName = lastName
        self.email = email
        self.dateOfBirth = dateOfBirth
        self.contactNo = contactNo

    def json(self):
        return {
            "pid": self.pid,
            "firstName": self.firstName,
            "lastName": self.lastName,
            "email": self.email,
            "dateOfBirth": self.dateOfBirth,
            "contactNo": self.contactNo
        }

    def get_password(self):
        return self.password

@app.route("/passenger")
def get_all():
    return jsonify({"passengers": [passenger.json() for passenger in Passenger.query.all()]})


@app.route("/passenger/email/<string:email>")
def get_passenger_by_email(email):
    passenger = Passenger.query.filter_by(email=email).first()
    if passenger:
        return jsonify(passenger.json())
    return jsonify({"message": "Passenger not found"}), 404

@app.route("/passenger/<string:pid>")
def get_passenger_by_pid(pid):
    passenger = Passenger.query.filter_by(pid=pid).first()
    if passenger:
        return jsonify(passenger.json())
    return jsonify({"message": "Passenger not found"}), 404

@app.route("/getpassengerpid/<string:email>")
def get_pid_by_email(email):
    passenger = Passenger.query.filter_by(email=email).first()
    pid = passenger.pid
    if pid:
        #store
        return jsonify(passenger.pid)
    return jsonify({"message": "Email not registered. Please create an account!"}), 404
    

@app.route("/passenger/register/<string:email>", methods=['POST'])
# create_passenger(pid, password, lastName, firstname, email, dob, contactNo)
def create_passenger(email):
    if(Passenger.query.filter_by(email=email).first()):
        return jsonify({"message": "A passenger account with '{}' already exists.".format(email)}), 400

    data = request.get_json()

    pwd = data["password"]
    pid = data["pid"]
    firstName = data["firstName"]
    lastName = data["lastName"]
    dateOfBirth = data["dateOfBirth"]
    contactNo = data["contactNo"]
    
    password_hashed = sha256_crypt.hash(pwd) 
    passenger = Passenger(email, password_hashed, pid, firstName, lastName, dateOfBirth, contactNo)
    # passenger = Passenger(email, password_hashed, firstName, lastName, dateOfBirth, contactNo)

    try:
        db.session.add(passenger)
        db.session.commit()
    except:
        return jsonify({"message": "An error occurred creating your account."}), 500

    return jsonify(passenger.json()), 201

@app.route("/passenger/login", methods=['POST'])
def check():
    data = request.get_json()
    if data:
        email = data['email']
        passenger = Passenger.query.filter_by(email=email).first()
        if passenger:
            password_hashed = passenger.get_password()
            entered_pwd = data['password']
            if sha256_crypt.verify(entered_pwd, password_hashed):
                return jsonify({"message": "Login success"}), 200
            else:
                return jsonify({"message": "Wrong password"}), 400
        else:
            return jsonify({"message": "Wrong username"}), 400





if __name__ == "__main__":
    app.run(port=5002, debug=True)
