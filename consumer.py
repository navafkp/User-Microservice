import os
import django
import pika
import json


# # Set the DJANGO_SETTINGS_MODULE environment variable
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "usermenu.settings")

# # Configure Django settings
# django.setup()

# from user.models import Product

params = pika.URLParameters('amqps://tamelmkg:bAGQhUGeH658A5vM9E5wFA6wzQNaAkPc@puffin.rmq2.cloudamqp.com/tamelmkg')
connection = pika.BlockingConnection(params)
channel = connection.channel()

channel.queue_declare(queue='main')

def callback(ch, method, properties, body):
    print("Received in main")
    data = json.loads(body)
    print(data)

    # if properties.content_type == 'product_created':
    #     Product.objects.create(id=data['id'], title=data['title'], image=data['image'])
    #     print('Product created')
   

channel.basic_consume(queue='main', on_message_callback=callback, auto_ack=True)

print('Started consuming')
try:
    channel.start_consuming()
except KeyboardInterrupt:
    # Handle keyboard interrupt (Ctrl+C) gracefully
    pass
finally:
    connection.close()
