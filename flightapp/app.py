from flask import Flask, render_template, redirect
app = Flask(__name__)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/create_account")
def create_account():
    return render_template("create_account.html")

@app.route("/manage")
def manage_booking(): 
    return render_template("manage_booking.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/logout")
def logout():
    return render_template("logout.html")

@app.route("/search_flights")
def search_flights():
    return render_template("/search_flights.html")

@app.route("/admin_search")
def admin_search_flights():
    return render_template("/admin_search.html")

@app.route("/cart")
def cart():
    return render_template("/cart.html")

@app.route("/paypal")
def paypal():
    return render_template("/paypal.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)