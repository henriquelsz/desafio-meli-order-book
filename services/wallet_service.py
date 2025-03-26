import pika
import json
import threading
from infrastructure.database import DatabaseWallet

class WalletService:
    def __init__(self, wallet_repository: DatabaseWallet):
        self.wallet_repository = wallet_repository  # Repositório de wallets (pode ser um banco de dados NoSQL)
        self.start_consumer_thread()  # Inicia a thread do consumidor

    def credit_brl_debit_vibranium(self, wallet_id: str, amount: float, quantity: int):
        """Credita o saldo e debita vibranium na wallet do usuário (ordem de venda)"""
        wallet = self.wallet_repository.get_wallet(wallet_id)
        
        if wallet:
            wallet.credit_brl(amount)
            wallet.debit_vibranium(quantity)

            # Atualiza no banco de dados após as alterações
            self.wallet_repository.save_wallet(wallet)
        else:
            raise ValueError(f"Wallet {wallet_id} not found")

    def debit_brl_credit_vibranium(self, wallet_id: str, amount: float, quantity: int):
        """Debita o saldo e credita vibranium na wallet do usuário (ordem de compra)"""
        wallet = self.wallet_repository.get_wallet(wallet_id)
        if wallet:
            wallet.debit_brl(amount)
            wallet.credit_vibranium(quantity)

            # Atualiza no banco de dados após as alterações
            self.wallet_repository.save_wallet(wallet)
        else:
            raise ValueError(f"Wallet {wallet_id} not found")

    def lock_funds(self, wallet_id: str, amount: float):
        """Bloqueia fundos na wallet do usuário"""
        wallet = self.wallet_repository.get_wallet(wallet_id)
        if wallet:
            wallet.lock_funds(amount)
            self.wallet_repository.update_wallet(wallet)
        else:
            raise ValueError(f"Wallet {wallet_id} not found")

    def unlock_funds(self, wallet_id: str, amount: float):
        """Desbloqueia fundos na wallet do usuário"""
        wallet = self.wallet_repository.get_wallet(wallet_id)
        if wallet:
            wallet.unlock_funds(amount)
            self.wallet_repository.update_wallet(wallet)
        else:
            raise ValueError(f"Wallet {wallet_id} not found")


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

                # Verifica se as carteiras existem antes de processar o trade
                buy_wallet = self.wallet_repository.get_wallet(buy_wallet_id)
                sell_wallet = self.wallet_repository.get_wallet(sell_wallet_id)

                if not buy_wallet or not sell_wallet:
                    print(f"Ignorando trade: Carteira não encontrada (Buy: {buy_wallet_id}, Sell: {sell_wallet_id})")
                    ch.basic_ack(delivery_tag=method.delivery_tag)  # Confirma que a mensagem foi consumida
                    return

                print(f"Processando trade: Buy Wallet {buy_wallet_id}, Sell Wallet {sell_wallet_id}")

                # Atualiza as wallets
                self.credit_brl_debit_vibranium(sell_wallet_id, amount=price * quantity, quantity=quantity)
                self.debit_brl_credit_vibranium(buy_wallet_id, amount=price * quantity, quantity=quantity)

                print(f"Trade processado com sucesso: Buy Wallet {buy_wallet_id}, Sell Wallet {sell_wallet_id}")

            ch.basic_ack(delivery_tag=method.delivery_tag)

        channel.basic_consume(queue='trade_queue', on_message_callback=callback, auto_ack=False)
        print(" [*] Waiting for trade events")
        channel.start_consuming()

    def start_consumer_thread(self):
        """ Inicia o consumidor do RabbitMQ em uma thread separada """
        consumer_thread = threading.Thread(target=self.init_consumer, daemon=True)
        consumer_thread.start()