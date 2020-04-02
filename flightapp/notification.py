# run 'pip install mailjet_rest'
from mailjet_rest import Client
import json
import sys
import os
import pika

api_key = 'fec706b46ad234571c192c730c6f5bc6'
api_secret = 'bdbe11e863fb9cffb824091bedf5c51c'
mailjet = Client(auth=(api_key, api_secret), version='v3.1')

hostname = "localhost" 
port = 5672 
# connect to the broker and set up a communication channel in the connection
connection = pika.BlockingConnection(pika.ConnectionParameters(host=hostname, port=port))
channel = connection.channel()
# set up the exchange if the exchange doesn't exist
exchangename="booking_direct"
channel.exchange_declare(exchange=exchangename, exchange_type='direct')

def receive_booking():
    # prepare a queue for receiving messages
    channelqueue = channel.queue_declare(queue="notification", durable=True) 
    queue_name = channelqueue.method.queue
    channel.queue_bind(exchange=exchangename, queue=queue_name, routing_key='notification.booking')

    # set up a consumer and start to wait for coming messages
    channel.basic_qos(prefetch_count=1) # The "Quality of Service" setting makes the broker distribute only one message to a consumer if the consumer is available (i.e., having finished processing and acknowledged all previous messages that it receives)
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True) # 'auto_ack=True' acknowledges the reception of a message to the broker automatically, so that the broker can assume the message is received and processed and remove it from the queue
    channel.start_consuming() # an implicit loop waiting to receive messages; it doesn't exit by default. Use Ctrl+C in the command window to terminate it.

def callback(channel, method, properties, body): # required signature for the callback; no return
    print("Received an booking by " + __file__)
    result = send_email(json.loads(body))
    # print processing result; not really needed
    json.dump(result, sys.stdout, default=str) # convert the JSON object to a string and print out on screen
    print() # print a new line feed to the previous json dump
    print() # print another new line as a separator


def send_email(message):
    email = message['email']
    name = message['name']
    flightNo = message['flightNo']
    deptTime = message['deptTime']
    departDate = message['departDate']
    refCode = message['refCode']
    msg = 'Thank you for choosing our service! Your flight number is ' + flightNo + " will take part on " + departDate + " at " + deptTime + " .Please show your reference code: " + refCode + " upon checking in. Thank you for travelling with us during this period! Stay safe 😊 Warm Regards, Flight Like T6"
    data = {
    'Messages': [
        {
        "From": {
            "Email": "ingsin.bak.2017@sis.smu.edu.sg",
            "Name": "Flight Like T6"
        },
        "To": [
            {
            "Email": email,
            "Name": name
            }
        ],
        "Subject": "Booking Confirmation. REF CODE: " + refCode ,
        "TextPart": msg,
        "HTMLPart": "<img style='display:block;margin-left:auto;margin-right:auto;width:50%;' src='https://i.gifer.com/JFi.gif'><h2 style='text-align:center'>Thank you for choosing our service!</h2> Your flight number is <b>" + flightNo + "</b> will take part on <b>" + departDate + "</b> at <b>" + deptTime + "</b>.<br> Please show your reference code: <b>" + refCode + "</b> upon checking in. <br><br> Thank you for travelling with us during this period! Stay safe 😊 <br><br>Warm Regards, <br> <i>Flight Like T6</i>",
        "CustomID": "AppGettingStartedTest"
        }
    ]
    }
    result = mailjet.send.create(data=data)
    print(result.status_code)
    print(result.json())
    return result.json()

if __name__ == "__main__": 
    print("This is " + os.path.basename(__file__) + ": sending an email...")
    receive_booking()