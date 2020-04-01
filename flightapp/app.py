from flask import Flask, render_template
app = Flask(__name__)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/manage")
def manage_booking(): 
    return render_template("manage_booking.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/search_flights")
def search_flights():
    return render_template("/search_flights.html")

if __name__ == "__main__":
    app.run(port=8000, debug=True)