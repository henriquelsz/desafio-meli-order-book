import pika
import json

class EventPublisher:
    def __init__(self, queue_name='trade_events', host='localhost'):
        self.queue_name = queue_name
        self.host = host
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.host))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name, durable=True) #Inicializa a fila

    def publish_event(self, event):
        event_data = {
            "trade_id": event.trade_id,
            "buy_order_id": event.buy_order_id,
            "sell_order_id": event.sell_order_id,
            "price": event.price.value,
            "quantity": event.quantity.value,
            "timestamp": event.timestamp
        }

        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            body=json.dumps(event_data),
            properties=pika.BasicProperties(delivery_mode=2) #Torna a mensagem persistente
        )

    def close(self):
        self.connection.close() #Fecha a conexao com o Rabbit
