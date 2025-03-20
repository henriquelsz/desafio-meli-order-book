from value_object import Price, Quantity, OrderType, OrderStatus

class Order:
    def __init__(self, id: str, user_id: str, type: OrderType, quantity: Quantity, price: Price):
        self.id = id
        self.user_id = user_id
        self.type = type
        self.quantity = quantity
        self.price = price
        self.status = OrderStatus.OPEN

    def __lt__(self, other_order):
        """
        Define a ordem da heap:
            - BUY: Maior preco vem primeiro (define como MaxHeap)
            - SELL: Menor preco vem primeiro (define como MinHeap)
        """
        if self.type == OrderType.BUY:
            return self.price.value > other_order.price.value #inverte logica e se torna MaxHeap
        return self.price.value < other_order.price.value #MinHeap padrao da lib heapq

class Trade:
    def __init__(self, id: str, buy_order_id: str, sell_order_id: str, price: Price, quantity: Quantity, timestamp: float):
        self.id = id
        self.buy_order_id = buy_order_id
        self.sell_order_id = sell_order_id
        self.price = price
        self.quantity = quantity
        self.timestamp = timestamp

#Teste e Debug
if __name__ == '__main__':
    order1 = Order(id="1", user_id="userA", type=OrderType.BUY, quantity=Quantity(10), price=Price(105))
    print(f'Ordem criada {order1.id}, tipo {order1.type}, preco {order1.price.value} e quantidade {order1.quantity.value}')