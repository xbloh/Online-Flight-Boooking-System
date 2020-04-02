from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import requests

app = Flask(__name__)

CORS(app)
bookingURL = "http://localhost:5000/booking/status"

# @app.route("/billing", methods = ['POST', 'GET'])

# def index():
#     if request.method == 'POST':
#         data = request.get_json()
#         price = data['price']
#         refCode = data['refCode']
#         return render_template("paypal.html", price = price, refCode = refCode)
#     if request.method == "GET":
#         return render_template("paypal.html")

@app.route('/billing/status/<string:stt>/<string:refCode>', methods = ['OPTIONS'])
def receive_status(stt, refCode):
    status = json.loads(json.dumps({"status" : stt, "refCode": refCode}, default = str))
    r = requests.options(bookingURL, json = status)
    return jsonify({"status" : stt, "refCode": refCode})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004, debug=True)