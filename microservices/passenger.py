from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import environ

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

    def __init__(self, pid, password, firstName, lastName, email, dateOfBirth, contactNo):
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


@app.route("/passenger")
def get_all():
    '''
    Returns GET
    # 127.0.0.1 - - [16/Jan/2020 14:27:52] "GET /book HTTP/1.1" 200 -
    '''

    # print('get all books')
    # return 'get all books'

    # print([book.json() for book in Book.query.all()])
    return jsonify({"passengers": [passenger.json() for passenger in Passenger.query.all()]})


if __name__ == "__main__":
    app.run(port=5000, debug=True)
