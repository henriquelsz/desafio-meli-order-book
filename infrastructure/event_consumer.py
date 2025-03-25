import pika
import json
from services.wallet_service import WalletService
from infrastructure.database import DatabaseOrder

class EventConsumer:
    def __init__(self, rabbitmq_host: str = 'localhost', wallet_service: WalletService = None):
        self.rabbitmq_host = rabbitmq_host
        self.wallet_service = wallet_service  # Aqui estamos passando o WalletService
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.rabbitmq_host))
        self.channel = self.connection.channel()

    def consume_event(self, event_name: str, callback):
        """Consumir um evento de uma fila do RabbitMQ"""
        self.channel.queue_declare(queue=event_name, durable=True)
        self.channel.basic_consume(queue=event_name, on_message_callback=callback, auto_ack=True)
        print(f"Esperando eventos da fila '{event_name}'...")
        self.channel.start_consuming()

    def close(self):
        """Fecha a conexão com o RabbitMQ"""
        self.connection.close()

# Exemplo de um consumidor que processa um evento TradeExecuted
def process_trade_event(ch, method, properties, body):
    event = json.loads(body)

    if event["event_type"] == "TradeExecuted":
        trade = event["trade"]
        buy_order_id = trade["buy_order_id"]
        sell_order_id = trade["sell_order_id"]
        price = trade["price"]
        quantity = trade["quantity"]
        buy_wallet_id = trade["buy_wallet_id"]
        sell_wallet_id = trade["sell_wallet_id"] 

        # O vendedor credita BRL e debita Vibranium
        self.wallet_service.credit_brl_debit_vibranium(sell_wallet_id, amount= price * quantity, quantity=quantity)  

        # O comprador debita BRL e credita Vibranium
        self.wallet_service.debit_brl_credit_vibranium(buy_wallet_id, price * quantity)  

        print(f"Trade processada: Buy Order {buy_order_id}, Sell Order {sell_order_id}")

    ch.basic_ack(delivery_tag=method.delivery_tag)


