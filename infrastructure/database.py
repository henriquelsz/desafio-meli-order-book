from domain.entities import Wallet, Order
from typing import Dict

class DatabaseWallet:
    def __init__(self):
        # Usando um dicionário simples para simular o banco de dados.
        self.wallets: Dict[str, Wallet] = {}

    def get_wallet(self, wallet_id: str) -> Wallet:
        """Obtém a carteira do usuário"""
        if wallet_id not in self.wallets:
            # Se a carteira não existir, cria uma nova
            self.wallets[wallet_id] = Wallet(wallet_id=wallet_id, balance_brl=0.0, balance_vibranium=0.0)
        return self.wallets[wallet_id]

    def save_wallet(self, wallet: Wallet) -> None:
        """Salva ou atualiza a carteira no banco de dados"""
        self.wallets[wallet.wallet_id] = wallet
        print(f"Carteira de {wallet.wallet_id} salva com sucesso!")

class DatabaseOrder:
    def __init__(self):
        self.orders: Dict[str, Order] = {}
    
    def get_order(self, order_id: str) -> Order:
        if order_id not in self.orders:
            return "Order nao encontrada no Banco"
        return self.orders[order_id]
    
    def save_order(self, order: Order) -> None:
        self.orders[order.id] = order
