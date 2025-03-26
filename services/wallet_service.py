import pika
import json
import threading
import redis
from infrastructure.database import DatabaseWallet
from redis.exceptions import LockError

class WalletService:
    def __init__(self, wallet_repository: DatabaseWallet):
        self.wallet_repository = wallet_repository  # Repositório de wallets (banco em memória)
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)  # Conexão com Redis
        self.start_consumer_thread()  # Inicia a thread do consumidor

    def credit_brl_debit_vibranium(self, wallet_id: str, amount: float, quantity: int):
        """Credita saldo em BRL e debita Vibranium da carteira (ordem de venda)"""
        lock_key = f"wallet_lock:{wallet_id}"
        lock = self.redis_client.lock(lock_key, timeout=5)  # Lock com timeout de 5s

        if lock.acquire(blocking=True):  # Aguarda lock
            try:
                wallet = self.wallet_repository.get_wallet(wallet_id)
                if wallet:
                    wallet.credit_brl(amount)
                    wallet.debit_vibranium(quantity)
                    self.wallet_repository.save_wallet(wallet)
                else:
                    raise ValueError(f"Wallet {wallet_id} not found")
            finally:
                lock.release()  # Libera o lock
        else:
            print(f"Não conseguiu adquirir lock para Wallet {wallet_id}")

    def debit_brl_credit_vibranium(self, wallet_id: str, amount: float, quantity: int):
        """Debita saldo em BRL e credita Vibranium na carteira (ordem de compra)"""
        lock_key = f"wallet_lock:{wallet_id}"
        lock = self.redis_client.lock(lock_key, timeout=5)

        if lock.acquire(blocking=True):
            try:
                wallet = self.wallet_repository.get_wallet(wallet_id)
                if wallet:
                    wallet.debit_brl(amount)
                    wallet.credit_vibranium(quantity)
                    self.wallet_repository.save_wallet(wallet)
                else:
                    raise ValueError(f"Wallet {wallet_id} not found")
            finally:
                lock.release()
        else:
            print(f"Não conseguiu adquirir lock para Wallet {wallet_id}")

    def init_consumer(self):
        """ Inicializa o consumidor do RabbitMQ para processar eventos TradeExecuted """
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='trade_queue', durable=True)

        def callback(ch, method, properties, body):
            """ Callback chamado ao receber um novo evento TradeExecuted """
            event = json.loads(body)

            if event["event_type"] == "TradeExecuted":
                trade = event["trade"]
                buy_wallet_id = trade["buy_wallet_id"]
                sell_wallet_id = trade["sell_wallet_id"]
                price = trade["price"]
                quantity = trade["quantity"]

                print(f"Recebido trade: Buy Wallet {buy_wallet_id}, Sell Wallet {sell_wallet_id}")

                # Evita processamento duplicado
                trade_id = trade["id"]
                if self.redis_client.get(f"processed_trade:{trade_id}"):
                    print(f"Trade {trade_id} já processado, ignorando...")
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    return

                # Atualiza carteiras com LOCK
                self.credit_brl_debit_vibranium(sell_wallet_id, amount=price * quantity, quantity=quantity)
                self.debit_brl_credit_vibranium(buy_wallet_id, amount=price * quantity, quantity=quantity)

                # Marca trade como processado no Redis (para evitar duplicações)
                self.redis_client.setex(f"processed_trade:{trade_id}", 3600, "1")  # Expira em 1 hora

                print(f"Trade processado com sucesso: Buy Wallet {buy_wallet_id}, Sell Wallet {sell_wallet_id}")

            ch.basic_ack(delivery_tag=method.delivery_tag)

        channel.basic_consume(queue='trade_queue', on_message_callback=callback, auto_ack=False)
        print(" [*] Aguardando eventos de trade...")
        channel.start_consuming()

    def start_consumer_thread(self):
        """ Inicia o consumidor do RabbitMQ em uma thread separada """
        consumer_thread = threading.Thread(target=self.init_consumer, daemon=True)
        consumer_thread.start()
