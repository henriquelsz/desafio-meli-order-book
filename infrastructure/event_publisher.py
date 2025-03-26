import pika
import json

class EventPublisher:
    def __init__(self, host='localhost'):
        self.host = host

    def publish_event(self, event: dict, event_type: str):
        """Abre e fecha a conexão a cada publicação para evitar problemas de conexão"""
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(self.host))
            channel = connection.channel()

            # Declarar as filas para garantir que existem
            channel.queue_declare(queue='order_queue', durable=True)
            channel.queue_declare(queue='trade_queue', durable=True)

            routing_key = 'order_queue' if event_type == 'OrderCreated' else 'trade_queue'

            channel.basic_publish(
                exchange='',
                routing_key=routing_key,
                body=json.dumps(event),
                properties=pika.BasicProperties(delivery_mode=1),
            )

            print(f"Evento '{event_type}' publicado com sucesso!")

            # ✅ Fecha a conexão corretamente após publicar
            channel.close()
            connection.close()

        except pika.exceptions.AMQPConnectionError as e:
            print(f"Erro de conexão ao publicar evento: {e}")
        except Exception as e:
            print(f"Erro inesperado: {e}")
