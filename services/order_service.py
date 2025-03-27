from domain.entities import Order
from domain.value_object import OrderType, OrderStatus, Price, Quantity
from infrastructure.event_publisher import EventPublisher
from infrastructure.database import DatabaseOrder
from event_store.event_store import EventStore
import time
import uuid

class OrderService:
    def __init__(self, order_repository: DatabaseOrder, event_store: EventStore):
        self.order_repository = order_repository
        self.event_publisher = EventPublisher()
        self.event_store = event_store
    
    def create_order(self, wallet_id: str, order_type: OrderType, quantity: float, price: float) -> Order:
        """Cria uma nova ordem, persiste no banco e publica evento para o Matching Engine"""
        
        # Criando entidade Order
        order = Order(
            id=str(uuid.uuid4()),
            wallet_id=wallet_id,
            type=order_type,
            quantity=Quantity(quantity),
            price=Price(price)
        )
        
        # Persistindo no banco
        self.order_repository.save_order(order)
        
        # Criando evento para o Matching Engine
        event = {
            "event_type": "OrderCreated",
            "order": {
                "id": order.id,
                "wallet_id": order.wallet_id,
                "type": order.type.value,
                "quantity": order.quantity.value,
                "price": order.price.value,
                "status": order.status.value,
                "timestamp": time.time()
            }
        }

        #Armazena evento OrderCreated
        self.event_store.append_event(event_type="OrderCreated", event_data=[event])

        # Publicando no RabbitMQ
        self.event_publisher.publish_event(event, event_type="OrderCreated")
        
        return order
