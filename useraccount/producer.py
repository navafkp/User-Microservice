import pika, json

params = pika.URLParameters('amqps://tamelmkg:bAGQhUGeH658A5vM9E5wFA6wzQNaAkPc@puffin.rmq2.cloudamqp.com/tamelmkg')
try:
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue='notification', durable=True)
    channel.queue_declare(queue='api_gateway', durable=True)
    
    
    
except pika.exceptions.AMQPConnectionError as connection_error:
    print(f"AMQP Connection Error: {connection_error}")

def publish_to_notification(method, body):
    
    try:
        properties = pika.BasicProperties(content_type='application/json',delivery_mode=2)
        channel.basic_publish(
        exchange='',
        routing_key='notification',
        body=json.dumps(body),
       
        properties=properties   # Make the message persistent
        
    )
    except pika.exceptions.AMQPChannelError as channel_error:
        print(f"AMQP Channel Error: {channel_error}")
        
 
 
# def on_request_message_received(ch, method, properties, body):
#     print(f'recived new message: {properties.correlation_id}')
#     ch.basic_publish('', routing_key=properties.reply_to, body=f'i am the reply to {properties.correlation_id}')
 
 
# channel.basic_consume(queue='api_gateway', auto_ack=True, on_message_callback =on_request_message_received)
 
 
 
# print("started user")
# channel.start_consuming()

        
# def callback_api_gateway(ch, method, properties, body):
#     try:
#         data = json.loads(body)
#         print("Received message from API Gateway:", data)

#         # Perform necessary operations based on the received data
#         # ...

#         # Send a reply back to the API Gateway
#         reply_body = {"response": "Data processed successfully"}
#         reply_properties = pika.BasicProperties(
#             content_type='application/json',
#             delivery_mode=2,
#             correlation_id=properties.correlation_id
#         )

#         # Use the reply_to field to send the response back to the API Gateway
#         ch.basic_publish(
#             exchange='',
#             routing_key=properties.reply_to,
#             body=json.dumps(reply_body),
#             properties=reply_properties
#         )

#         # Acknowledge the message
#         ch.basic_ack(delivery_tag=method.delivery_tag)

#     except Exception as e:
#         print(f"Error processing message from API Gateway: {e}")
    
