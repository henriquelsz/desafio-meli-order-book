import pika
import json

class EventPublisher:
    def __init__(self, host='localhost'):
        self.host = host
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.host))
        self.channel = self.connection.channel()
        # Declarar as filas de eventos
        self.channel.queue_declare(queue='order_queue', durable=True)
        self.channel.queue_declare(queue='trade_queue', durable=True)

    def publish_event(self, event: dict, event_type: str):
        """Publica eventos de tipos diferentes (ordem ou trade)"""
        try:
            routing_key = ''
            if event_type == 'OrderCreated':
                routing_key = 'order_queue'  # Fila para ordens
            elif event_type == 'TradeExecuted':
                routing_key = 'trade_queue'  # Fila para trades

            # Verificar se o canal está aberto
            if self.channel.is_open:
                self.channel.basic_publish(
                    exchange='',
                    routing_key=routing_key,
                    body=json.dumps(event),
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # Mensagem persistente
                    )
                )
                print(f"Evento '{event_type}' publicado com sucesso!")
            else:
                print("Channel is closed. Unable to publish event.")
        except pika.exceptions.AMQPConnectionError as e:
            print(f"Error publishing event: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
    
    def close(self):
        """Certifique-se de fechar o canal e a conexão corretamente"""
        if self.channel.is_open:
            self.channel.close()
        if self.connection.is_open:
            self.connection.close()
