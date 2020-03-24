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
    result = send_email(body)
    # print processing result; not really needed
    json.dump(result, sys.stdout, default=str) # convert the JSON object to a string and print out on screen
    print() # print a new line feed to the previous json dump
    print() # print another new line as a separator


def send_email(booking):
    json_obj = json.loads(booking)
    email = json_obj['email']
    name = json_obj['first name']
    msg = json.dumps(json_obj)
    data = {
    'Messages': [
        {
        "From": {
            "Email": "ingsin.bak.2017@sis.smu.edu.sg",
            "Name": "ESD TRAVEL ASIA"
        },
        "To": [
            {
            "Email": email,
            # "Email": 'ingsin.bak.2017@sis.smu.edu.sg',
            "Name": name
            }
        ],
        "Subject": "Greetings from Mailjet.",
        "TextPart": "My first Mailjet email",
        # "HTMLPart": "<h3>Dear passenger 1, welcome to <a href='https://www.mailjet.com/'>Mailjet</a>!</h3><br />May the delivery force be with you!",
        "HTMLPart": msg,
        "CustomID": "AppGettingStartedTest"
        }
    ]
    }
    result = mailjet.send.create(data=data)
    print(result.status_code)
    print(result.json())
    return

if __name__ == "__main__": 
    print("This is " + os.path.basename(__file__) + ": sending an email...")
    receive_booking()