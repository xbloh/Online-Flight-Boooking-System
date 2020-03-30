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
        return {"baggage_price": baggage.price, "status": 200}
    return jsonify({"message": "Couldn't find baggage"}), 404

@app.route("/pricing/meal/<int:meal_id>")
def get_meal_price(meal_id):
    meal = Meal.query.filter_by(meal_id=meal_id).first()
    if meal:
        return {"meal_price": meal.price, "status": 200}
    return jsonify({"message": "Couldn't find meal"}), 404

@app.route("/pricing/class/<string:class_name>")
def get_class_percentage(class_name):
    class_name = Class_type.query.filter_by(class_name=class_name).first()
    if class_name:
        return {"class_type_percentage": class_name.percentage, "status": 200}
    return jsonify({"message": "Couldn't find class type"}), 404

@app.route("/pricing/receive", methods=['POST'])
def receive_info():
    details = request.get_json()
    meal_price = get_meal_price(details['meal_id'])
    baggage_price = get_baggage_price(details['baggage_id'])
    class_type_percentage = get_class_percentage(details['class_type'])
    if meal_price['status'] == 200 and baggage_price['status'] == 200 and class_type_percentage['status'] == 200:
        result = {"meal_price" : meal_price['meal_price'], "baggage_price" : baggage_price['baggage_price'], "class_type_percentage" : class_type_percentage['class_type_percentage'], "status" : 200}
    replymessage = json.dumps(result)
    if result['status'] == 200:
        return replymessage, 200
    else:
        return replymessage, 502

@app.route("/pricing/getmeal/<string:meal_id>")
def get_mealobj_by_meal_id(meal_id):
    meal = Meal.query.filter_by(meal_id=meal_id).first()
    if meal:
        return jsonify(meal.json())
    return jsonify({"message": "Couldn't find meal"}), 404

@app.route("/pricing/getmeal/<string:meal_desc>")
def get_mealobj_by_meal_desc(meal_desc):
    meal = Meal.query.filter_by(meal_desc=meal_desc).first()
    if meal:
        return jsonify(meal.json())
    return jsonify({"message": "Couldn't find meal"}), 404

@app.route("/pricing/getbaggage/<string:baggage_id>")
def get_mealobj_by_meal_id(baggage_id):
    baggage = Baggage.query.filter_by(baggage_id=baggage_id).first()
    if baggage:
        return jsonify(baggage.json())
    return jsonify({"message": "Couldn't find baggage"}), 404

@app.route("/pricing/getbaggage/<string:baggage_desc>")
def get_baggageobj_by_meal_desc(baggage_desc):
    baggage = Meal.query.filter_by(baggage_desc=baggage_desc).first()
    if baggage:
        return jsonify(baggage.json())
    return jsonify({"message": "Couldn't find baggage"}), 404



if __name__ == "__main__":
    app.run(port=5003, debug=True)
    
