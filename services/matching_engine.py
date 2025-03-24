import heapq
from typing import List
from domain.entities import Order, Trade
from domain.value_object import OrderType, OrderStatus, Price, Quantity
from domain.events import TradeExecuted
from infrastructure.event_publisher import EventPublisher

class MatchingEngine:
    def __init__(self):
        self.buy_orders = [] #Inicializando MaxHeap
        self.sell_orders = [] #Inicializando MinHeap
        self.event_publisher = EventPublisher()
    
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
                self.event_publisher.publish_event(trade)
                
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

# Testando classe MatchingEngine
if __name__ == "__main__":
    order1 = Order(id="1", user_id="userA", type=OrderType.BUY, quantity=Quantity(10), price=Price(106))
    order2 = Order(id="2", user_id="userB", type=OrderType.SELL, quantity=Quantity(10), price=Price(105))
    engine = MatchingEngine()

    engine.place_order(order1)
    engine.place_order(order2)
    trades = engine.match_orders()
    
    for t in trades:
        print(f"{t}")