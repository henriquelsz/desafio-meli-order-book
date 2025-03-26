from domain.value_object import Price, Quantity, OrderType, OrderStatus

class Order:
    def __init__(self, id: str, wallet_id: str, type: OrderType, quantity: Quantity, price: Price):
        self.id = id
        self.wallet_id = wallet_id
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
    def __init__(self, id: str, balance_brl: float, balance_vibranium: int, locked_balance: float = 0.0):
        self.id = id
        self.balance_brl = balance_brl
        self.balance_vibranium = balance_vibranium
        self.locked_balance = locked_balance

    def credit_brl(self, amount: float):
        self.balance_brl += amount
    
    def debit_brl(self, amount: float):
        if amount > self.balance_brl:
            raise ValueError("Fundos insuficientes")
        self.balance_brl -= amount
    
    def credit_vibranium(self, amount: int):
        self.balance_vibranium += amount

    def debit_vibranium(self, amount: int):
        self.balance_vibranium -= amount
            
