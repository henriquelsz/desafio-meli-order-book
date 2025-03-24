from fastapi import APIRouter, HTTPException
from domain.entities import Order
from domain.value_object import OrderType, Price, Quantity
from services.matching_engine import MatchingEngine

router = APIRouter()
matching_engine = MatchingEngine()

@router.post("/orders")
def place_order(wallet_id: str, order_type: OrderType, quantity: int, price: float):
    #Recebendo uma order de compra ou venda e adicionando no Order Book
    try:
        order = Order(
            id=f"order-{wallet_id}-{price}",
            wallet_id = wallet_id,
            type = order_type,
            quantity = Quantity(quantity),
            price = Price(price)
        )
        event = matching_engine.place_order(order)
        return  {"message": "Ordem adicionada com sucesso!", "event": event}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/orderbook")
def get_order_book():
    #Retorna o order book no estado atual
    return {
        "buy_orders": [order.__dict__ for order in matching_engine.buy_orders],
        "sell_orders": [order.__dict__ for order in matching_engine.sell_orders]
    }

@router.post("/match")
def match_orders():
    #Executa o casamento das ordens
    executed_trades = matching_engine.match_orders()
    return {"trades_executadas": executed_trades}
