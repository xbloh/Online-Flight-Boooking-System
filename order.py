
#!/usr/bin/env python3
# The above shebang (#!) operator tells Unix-like environments
# to run this file as a python3 script

import json
import sys
import os
import random
import datetime

# Communication patterns:
# Use HTTP calls to enable interaction
import requests

shippingURL = "http://localhost:5002/shipping"
monitoringURL = "http://localhost:5003/monitoring"
errorURL = "http://localhost:5004/error"

class Order:
    # Load existing orders from a JSON file (for simplicity here). In reality, orders will be stored in DB. 
    with open('orders.json') as order_json_file:
        orders = json.load(order_json_file)
    order_json_file.close()

    # Find the max of all existing "order_id" to be used as the last order_id; if in actual DB, the uniqueness of "order_id" will be managed by DBMS
    last_order_id = max([ o["order_id"] for o in orders["orders"] ])

def orders_json():
    """return all orders as a JSON object (not a string)"""
    return Order.orders
    
def orders_save(orders_file):
    """ save all orders to a file"""
    with open(orders_file, 'w') as order_json_outfile:
        json.dump(Order.orders, order_json_outfile, indent=2, default=str) # convert a JSON object to a string
    order_json_outfile.close()

class Order_Item:
    def __init__(self):
        self.item_id = 0
        self.book_id = "0123456789abc"
        self.quantity = 0
        self.order_id = 0

    # return an order item as a JSON object
    def json(self):
        return {'item_id': self.item_id, 'book_id': self.book_id, 'quantity': self.quantity, 'order_id': self.order_id}

def get_all():
    """Return all orders as a JSON object"""
    return Order.orders
 
def find_by_order_id(order_id):
    """Return an order (orders) of the order_id"""
    order = [ o for o in Order.orders["orders"] if o["order_id"]==order_id ]
    if len(order)==1:
        return order[0]
    elif len(order)>1:
        return {'message': 'Multiple orders found for id ' + str(order_id), 'orders': order}
    else:
        return {'message': 'Order not found for id ' + str(order_id)}
 
def create_order(order_input):
    """Create a new order according to the order_input"""
    # assume status==200 indicates success
    status = 200
    message = "Success"

    # Load the order info from a cart (from a file in this case; can use DB too, or receive from HTTP requests)
    try:
        with open(order_input) as sample_order_file:
            cart_order = json.load(sample_order_file)
    except:
        status = 501
        message = "An error occurred in loading the order cart."
    finally:
        sample_order_file.close()
    if status!=200:
        print("Failed order creation.")
        return {'status': status, 'message': message}

    # Create a new order: set up data fields in the order as a JSON object (i.e., a python dictionary)
    order = dict()
    order["customer_id"] = cart_order['customer_id']
    order["order_id"] = Order.last_order_id + 1
    order["timestamp"] = datetime.datetime.now()
    order["order_item"] = []
    cart_item = cart_order['cart_item']
    for index, ci in enumerate(cart_item):
        order["order_item"].append({"book_id": cart_item[index]['book_id'],
                                "quantity": cart_item[index]['quantity'],
                                "item_id": index + 1,
                                "order_id": order["order_id"]
        })
    # check if order creation is successful
    if len(order["order_item"])<1:
        status = 404
        message = "Empty order."
    # Simulate other errors in order creation via a random bit
    result = bool(random.getrandbits(1))
    if not result:
        status = 500
        message = "A simulated error occurred when creating the order."

    if status!=200:
        print("Failed order creation.")
        return {'status': status, 'message': message}

    # Append the newly created order to the existing orders
    Order.orders["orders"].append(order)
    # Increment the last_order_id; if using a DB, DBMS can manage this
    Order.last_order_id = Order.last_order_id + 1
    # Write the newly created order back to the file for permanent storage; if using a DB, this will be done by the DBMS
    orders_save("orders.new.json")

    # Return the newly created order when creation is succssful
    if status==200:
        print("OK order creation.")
        return order

def send_order(order):
    """inform Shipping/Monitoring/Error as needed"""
    # Convert a JSON object to a string and back, to make sure the data is serializable (i.e., can be a string)
    order = json.loads(json.dumps(order, default=str)) # HTTP requests require all serializable data (but 'datatime' is not); the trick here converts 'datatime' to a string.
    # always inform Monitoring
    r = requests.post(monitoringURL, json = order) # the reply 'r' is no use
    print(">> Response from Monitoring {}".format(r))
    #print(r)

    if "status" in order: # if some error happened
        # inform Error
        r = requests.post(errorURL, data = order) # the reply 'r' is no use
        print("Order status ({:d}) sent to error handler.".format(order["status"]))
        print(">> Response from Error_handling {}".format(r))
    else:
        # inform Shipping
        r = requests.post(shippingURL, json = order)
        print("Order sent to shipping.")
        print(">> Response from Shipping {}".format(r))
        result = json.loads(r.text.lower())
        # check/print shipping's result
        if result["status"]:
            print("Order shipping OK.")
        else:
            print("Order shipping failed.")

# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is " + os.path.basename(__file__) + ": creating an order...")
    order = create_order("sample_order.txt")
    send_order(order)
#    print(get_all())
#    print(find_by_order_id(3))
