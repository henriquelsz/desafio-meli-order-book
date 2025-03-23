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
        Define a ordem da heap utilizada no match_orders():
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
    
    def __repr__(self):
        return f"Trade(id={self.id}, buy_order_id={self.buy_order_id}, sell_order_id={self.sell_order_id}, price={self.price.value}, quantity={self.quantity}, timestamp={self.timestamp}"

class Wallet:
    def __init__(self, user_id: str, balance_brl: float, balance_vibranium: int, locked_balance: float = 0.0):
        self.user_id = user_id
        self.balance_brl = balance_brl
        self.balance_vibranium = balance_vibranium
        self.locked_balance = locked_balance

    def credit(self, amount: float):
        self.balance_brl += amount
    
    def debit(self, amount: float):
        if amount > self.balance_brl:
            raise ValueError("Fundos insuficientes")
        self.balance_brl -= amount
    
    def lock_funds(self, amount: float):
        if amout > self.balance_brl:
            raise ValueError("Fundos insuficientes para travar")
        self.balance_brl -= amount
        self.locked_balance += amount
    
    def unlock_funds(self, amount: float):
        if amount > self.locked_balance:
            raise ValueError("Quantidade maior que valor de fundos travados")
        self.balance_brl += amount
        self.locked_balance -= amount

#Teste e Debug
if __name__ == '__main__':
    order1 = Order(id="1", user_id="userA", type=OrderType.BUY, quantity=Quantity(10), price=Price(105))
    print(f'Ordem criada {order1.id}, tipo {order1.type}, preco {order1.price.value} e quantidade {order1.quantity.value}')