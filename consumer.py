from dotenv import load_dotenv
import pika, jwt
import os, json, django
load_dotenv() 

secret_key = os.getenv('SECRET_KEY')

connection_params = pika.ConnectionParameters(
    host='docker-taskyflow-microservice-rabbitmq-container-1',
    port=5672,
    virtual_host='/',
    credentials=pika.PlainCredentials(username='taskyapp', password='1345'),
    heartbeat=600,
)

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "taskyuser.settings")

# Configure Django settings
django.setup()
from useraccount.models import CustomUser

def establish_connection():
    while True:
        try:
            connection = pika.BlockingConnection(connection_params)
            return connection
        except Exception as e:
            raise e
            
from django.shortcuts import get_object_or_404
connection = establish_connection()
channel = connection.channel()

def on_request_message_received(ch, method, properties, body):
    access_token = json.loads(body).get("access")
    manager = json.loads(body).get('manager', None)
    try:
        payload = jwt.decode(access_token, secret_key, algorithms=['HS256'])
        user_id = payload['user_id']
        if manager is None:
            available = CustomUser.objects.filter(id=user_id).exists()
        else:
            user = get_object_or_404(CustomUser, id=user_id, role='manager')
            if user:
                available=True
            else:
                available=False
        response_data = {'bool': available}  
      
    except jwt.ExpiredSignatureError:
        response_data = {'bool': False}
    except jwt.InvalidTokenError:
        response_data = {'bool': False}
    except Exception as e:
        response_data = {'bool': False}
        
    data = json.dumps(response_data)
    ch.basic_publish(
        exchange='', 
        routing_key=properties.reply_to, 
        body=data,
        properties=pika.BasicProperties(
            correlation_id=properties.correlation_id,
        )
        )

channel.queue_declare(queue='api_gateway', durable=True)

channel.basic_consume(
    queue='api_gateway',
    on_message_callback=on_request_message_received,
    auto_ack=True
)

print("starting server")
channel.start_consuming()
