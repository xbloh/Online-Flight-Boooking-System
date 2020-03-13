from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import environ

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/book'
# set dbURL=mysql+mysqlconnector://root@localhost:3306/book
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 1800}

db = SQLAlchemy(app)
CORS(app)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    # if debug is True, The program refreshed the server if there are changes made to the code.

    # Either turn this on, or turn autosave on
    # If both on, the terminal will keep on refreshing
