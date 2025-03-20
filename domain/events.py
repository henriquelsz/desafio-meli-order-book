from entities import Order, Trade

class OrderCreated:
    def __init__(self, order: Order):
        self.order = order

class TradeExecuted:
    def __init__(self, trade: Trade):
        self.trade = trade