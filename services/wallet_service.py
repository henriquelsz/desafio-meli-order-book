from infrastructure.database import DatabaseWallet, DatabaseOrder

class WalletService:
    def __init__(self, wallet_repository: DatabaseWallet):
        self.wallet_repository = wallet_repository  # Repositório de wallets (pode ser um banco de dados NoSQL)

    def credit_brl_debit_vibranium(self, wallet_id: str, amount: float, quantity: int):
        """Credita o saldo e debita vibranium na wallet do usuário (ordem de venda)"""
        wallet = self.wallet_repository.get_wallet(wallet_id)
        
        if wallet:
            wallet.credit_brl(amount)
            wallet.debit_vibranium(quantity)
        else:
            raise ValueError(f"Wallet {wallet_id} not found")

    def debit_brl_credit_vibranium(self, wallet_id: str, amount: float, quantity: int):
        """Debita o saldo e credita vibranium na wallet do usuário (ordem de compra)"""
        wallet = self.wallet_repository.get_wallet(wallet_id)
        if wallet:
            wallet.debit_brl(amount)
            wallet.credit_vibranium(quantity)
        else:
            raise ValueError(f"Wallet {wallet_id} not found")

    def lock_funds(self, wallet_id: str, amount: float):
        """Bloqueia fundos na wallet do usuário"""
        wallet = self.wallet_repository.get_wallet(wallet_id)
        if wallet:
            wallet.lock_funds(amount)
            self.wallet_repository.update_wallet(wallet)
        else:
            raise ValueError(f"Wallet {wallet_id} not found")

    def unlock_funds(self, wallet_id: str, amount: float):
        """Desbloqueia fundos na wallet do usuário"""
        wallet = self.wallet_repository.get_wallet(wallet_id)
        if wallet:
            wallet.unlock_funds(amount)
            self.wallet_repository.update_wallet(wallet)
        else:
            raise ValueError(f"Wallet {wallet_id} not found")
