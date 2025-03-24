import pika
import json
from wallet_service import WalletService

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
    event_data = json.loads(body)
    print(f"Evento recebido: {event_data}")
    
    # A lógica de crédito e débito é delegada ao WalletService
    user_id = event_data['trade']['buy_user_id'] if event_data['trade']['type'] == 'BUY' else event_data['trade']['sell_user_id']
    amount = event_data['trade']['amount']
    quantity = event_data['trade']['quantity']

    # Aqui estamos processando uma compra ou venda
    if event_data['event_type'] == 'TradeExecuted':
        trade_data = event_data['trade']
        print(f"Processando trade: {trade_data}")
        
        if trade_data['type'] == 'BUY':
            # Compra: debitamos o valor da conta e creditamos o Vibranium
            wallet_service.debit(user_id, amount)
            # Se for uma compra, o usuário ganha Vibranium, então creditamos isso na wallet.
            wallet_service.lock_funds(user_id, amount)  # Bloqueia o valor que o usuário está comprando
        elif trade_data['type'] == 'SELL':
            # Venda: creditamos o valor na conta e debitamos o Vibranium
            wallet_service.credit(user_id, amount)
            # Se for uma venda, o usuário perde o Vibranium, então debitamos isso na wallet.
            wallet_service.unlock_funds(user_id, amount)  # Desbloqueia o valor após a venda.

        print(f"Trade processada com sucesso!")

# Inicialização do consumidor
wallet_service = WalletService(wallet_repository)  # Agora passando o WalletService
consumer = EventConsumer(wallet_service=wallet_service)
consumer.consume_event('TradeExecuted', process_trade_event)
