from fastapi import APIRouter, HTTPException
from domain.entities import Order, Wallet
from domain.value_object import OrderType, Price, Quantity
from services.matching_engine import MatchingEngine
from services.wallet_service import WalletService
from services.order_service import OrderService
from infrastructure.database import DatabaseOrder, DatabaseWallet
from event_store.event_store import EventStore

router = APIRouter()

#Inicializando Banco de Dados
shared_wallet_db = DatabaseWallet()
shared_order_db = DatabaseOrder()
event_store_db = EventStore()

# Inicializando serviços
wallet_service = WalletService(wallet_repository=shared_wallet_db, event_store=event_store_db)
order_service = OrderService(order_repository=shared_order_db, event_store=event_store_db)
matching_engine = MatchingEngine(event_store=event_store_db)

@router.post("/orders")
def create_order(wallet_id: str, order_type: OrderType, quantity: int, price: float):
    # Recebendo uma order de compra ou venda e adicionando no Order Book
    try:
        order = order_service.create_order(wallet_id, order_type, quantity, price)
        return {"message": "Order criada com sucesso", "order": order}   
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/orderbook")
def get_order_book():
    # Retorna o order book no estado atual
    return {
        "buy_orders": [order.__dict__ for order in matching_engine.buy_orders],
        "sell_orders": [order.__dict__ for order in matching_engine.sell_orders]
    }

@router.post("/wallets")
def create_wallet(wallet_id: str, balance_brl: float = 0.0, balance_vibranium: float = 0.0):
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
        balance_brl=balance_brl,
        balance_vibranium=balance_vibranium
    )
    shared_wallet_db.save_wallet(new_wallet)

    return {
        "message": "Wallet criada com sucesso!",
        "wallet_id": wallet_id,
        "balance_brl": balance_brl,
        "balance_vibranium": balance_vibranium
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

@router.get("/events")
def get_events():
    """
    Retorna os eventos armazenados no EventStoreDB.
    """
    events = event_store_db.get_events()
    return {"events": events}