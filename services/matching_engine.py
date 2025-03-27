import heapq
import json
import pika
import time
import threading
from typing import List
from domain.entities import Order, Trade
from domain.value_object import OrderType, OrderStatus, Price, Quantity
from domain.events import TradeExecuted
from infrastructure.event_publisher import EventPublisher
from event_store.event_store import EventStore

class MatchingEngine:
    def __init__(self, event_store: EventStore):
        self.buy_orders = [] #Inicializando MaxHeap
        self.sell_orders = [] #Inicializando MinHeap
        self.event_publisher = EventPublisher()
        self.event_store = event_store
        self.start_consumer_thread() #Funcao que incializa a thread do consumer
    
    def place_order(self, order: Order):
        if order.type == OrderType.BUY:
            heapq.heappush(self.buy_orders, order) #adiciona o No da MaxHeap a ordem do tipo Buy
        else:
            heapq.heappush(self.sell_orders, order) #adiciona o No da MinHeap a ordem do tipo Sell

    def match_orders(self) -> List[TradeExecuted]:
        trades = []
        
        while self.buy_orders and self.sell_orders:
            buy = self.buy_orders[0] #Ordem com MAIOR preco de compra
            sell = self.sell_orders[0] #Ordem com menor preco de venda

            if buy.price.value >= sell.price.value:
                trade_quantity = min(buy.quantity.value, sell.quantity.value)

                trade = Trade(
                    id = f"{buy.id}-{sell.id}",
                    buy_order_id = buy.id,
                    sell_order_id = sell.id,
                    price = sell.price,
                    quantity = min(buy.quantity.value,sell.quantity.value),
                    timestamp = 0.0 #placeholder
                )

                trades.append(TradeExecuted(trade))

                #Publica evento no Rabbit
                event = {
                    "event_type": "TradeExecuted",
                    "trade": {
                        "id": trade.id,
                        "buy_order_id": trade.buy_order_id,
                        "buy_wallet_id": buy.wallet_id,
                        "sell_order_id": trade.sell_order_id,
                        "sell_wallet_id": sell.wallet_id,
                        "price": trade.price.value,
                        "quantity": trade.quantity,
                        "timestamp": time.time()  
                    }
                }

                #Armazena evento TradeExecuted
                self.event_store.append_event(event_type="TradeExecuted", event_data=[event])

                #Publica evento no Rabbit
                self.event_publisher.publish_event(event, event_type="TradeExecuted")
                
                #Subtrai a quantidade negociada nas ordens
                buy.quantity.value -= trade_quantity
                sell.quantity.value -= trade_quantity

                #Remove ordens completamente preenchidas
                if buy.quantity.value == 0:
                    heapq.heappop(self.buy_orders) #remove no raiz (maior preco de compra)
                    buy.status = OrderStatus.FILLED
                if sell.quantity.value == 0:
                    heapq.heappop(self.sell_orders) #remove no raiz (menor preco de compra)
                    sell.status = OrderStatus.FILLED

            else:
                break
        
        return trades


    def init_consumer(self):
        """ Inicializa o consumidor do RabbitMQ para processar novas ordens """
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        channel = connection.channel()
        channel.queue_declare(queue='order_queue', durable=True)

        def callback(ch, method, properties, body):
            """ Callback chamado ao receber uma nova ordem do RabbitMQ """
            order_data = json.loads(body)
            order_data = order_data["order"]
            order = Order(
                id=order_data["id"],
                wallet_id=order_data["wallet_id"],
                type=OrderType(order_data["type"]),
                quantity=Quantity(order_data["quantity"]),
                price=Price(order_data["price"])
            )
            self.place_order(order)
            self.match_orders()  # Tenta casar ordens imediatamente

            #Enviar ACK para remover a mensagem da fila apos ser consumida
            ch.basic_ack(delivery_tag=method.delivery_tag)

        channel.basic_consume(queue='order_queue', on_message_callback=callback, auto_ack=False)
        print(" [*] Waiting for order events")
        channel.start_consuming()

    def start_consumer_thread(self):
        """ Inicia o consumidor do RabbitMQ em uma thread separada """
        consumer_thread = threading.Thread(target=self.init_consumer, daemon=True)
        consumer_thread.start()
