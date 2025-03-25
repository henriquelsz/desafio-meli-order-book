from fastapi import APIRouter, HTTPException
from domain.entities import Order, Wallet
from domain.value_object import OrderType, Price, Quantity
from services.matching_engine import MatchingEngine
from services.wallet_service import WalletService
from infrastructure.event_consumer import EventConsumer, process_trade_event
from infrastructure.database import DatabaseOrder, DatabaseWallet
import threading

router = APIRouter()
matching_engine = MatchingEngine()

# Inicializando Banco de Dados
shared_wallet_db = DatabaseWallet()
shared_order_db = DatabaseOrder()

#Inicializando wallet
wallet_service = WalletService(wallet_repository=shared_wallet_db)

# Consumidor 
def start_event_consumer():
    """
    Inicia o EventConsumer em uma thread separada para não travar a API.
    """
    consumer = EventConsumer(wallet_service=wallet_service)
    consumer.consume_event('TradeExecuted', process_trade_event)

# Criar uma thread para rodar o EventConsumer sem bloquear a API
event_consumer_thread = threading.Thread(target=start_event_consumer, daemon=True)
event_consumer_thread.start()

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
        #appenda ordem no databse
        shared_order_db.save_order(order)
        #addiciona order a matching engine
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

@router.post("/wallets")
def create_wallet(wallet_id: str, initial_brl: float = 0.0, initial_vibranium: float = 0.0):
    """
    Cria uma nova wallet com os saldos iniciais de BRL e Vibranium.
    """
    # Verifica se já existe uma wallet com esse ID
    existing_wallet = shared_wallet_db.get_wallet(wallet_id)
    if existing_wallet:
        raise HTTPException(status_code=400, detail=f"Wallet {wallet_id} já existe.")

    # Cria a carteira e salva no DatabaseWallet
    new_wallet = Wallet(
        id=wallet_id,
        balance_brl=initial_brl,
        balance_vibranium=initial_vibranium
    )
    shared_wallet_db.save_wallet(new_wallet)

    return {
        "message": "Wallet criada com sucesso!",
        "wallet_id": wallet_id,
        "balance_brl": initial_brl,
        "balance_vibranium": initial_vibranium
    }

@router.get("/wallets/{wallet_id}")
def get_wallet(wallet_id: str):
    """
    Retorna a wallet correspondente ao ID informado.
    """
    wallet = shared_wallet_db.get_wallet(wallet_id)
    if not wallet:
        raise HTTPException(status_code=404, detail=f"Wallet {wallet_id} não encontrada.")

    return {
        "wallet_id": wallet.id,
        "balance_brl": wallet.balance_brl,
        "balance_vibranium": wallet.balance_vibranium,
        "locked_balance": wallet.locked_balance
    }
