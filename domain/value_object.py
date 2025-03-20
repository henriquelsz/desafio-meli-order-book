from enum import Enum

class OrderType(Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderStatus(Enum):
    OPEN = "OPEN"
    FILLED = "FILLED"
    CANCELED = "CANCELED"

class Price:
    def __init__(self, value: float):
        if value <= 0:
            raise ValueError("Preço deve ser positivo")
        self.value = value

class Quantity:
    def __init__(self, value: int):
        if value <= 0:
            raise ValueError("Quantidade deve ser positiva")
        self.value = value