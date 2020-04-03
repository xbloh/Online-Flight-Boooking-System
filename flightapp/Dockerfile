FROM python:3
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY ./static ./static
COPY ./templates ./templates
COPY ./notification.py .
CMD [ "python", "notification.py" ]



# docker run -p 8000:8000 app/app:1.0.0
# docker run -p 5000:5000 booking/booking:1.0.0
# docker run -p 5001:5001 flight/flight:1.0.0
# docker run -p 5002:5002 passenger/passenger:1.0.0
# docker run -p 5003:5003 pricing/pricing:1.0.0
# docker run -p 5004:5004 billing/billing:1.0.0
# docker run notification/notification:1.0.0

# docker build -t app/app:1.0.0 . 
# docker build -t booking/booking:1.0.0 . 
# docker build -t flight/flight:1.0.0 . 
# docker build -t passenger/passenger:1.0.0 . 
# docker build -t pricing/pricing:1.0.0 . 
# docker build -t billing/billing:1.0.0 . 
# docker build -t notification/notification:1.0.0 . 

# docker pull dockerfile/rabbitmq

# docker run -d -p 5672:5672 -p 15672:15672 dockerfile/rabbitmq
