import pika
import json

class EventPublisher:
    def __init__(self, queue_name='trade_events', host='localhost'):
        self.queue_name = queue_name
        self.host = host
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.host))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name, durable=True) #Inicializa a fila

    def publish_event(self, event: dict):
        try:
            # Verificar se o canal está aberto
            if self.channel.is_open:
                self.channel.basic_publish(
                    exchange='',
                    routing_key='TradeExecuted',
                    body=json.dumps(event),
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # Mensagem persistente
                    )
                )
            else:
                print("Channel is closed. Unable to publish event.")
        except pika.exceptions.AMQPConnectionError as e:
            print(f"Error publishing event: {e}")
            # Reconnection logic if needed
        except Exception as e:
            print(f"Unexpected error: {e}")
    
    def close(self):
        """Certifique-se de fechar o canal e a conexão corretamente"""
        if self.channel.is_open:
            self.channel.close()
        if self.connection.is_open:
            self.connection.close()
