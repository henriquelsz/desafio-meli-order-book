from domain.entities import Order, Trade

class OrderCreated:
    def __init__(self, order: Order):
        self.order = order

class TradeExecuted:
    def __init__(self, trade: Trade):
        self.trade = trade
    
    def __repr__(self):
        return f"{self.trade}"