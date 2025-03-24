class WalletService:
    def __init__(self, wallet_repository):
        self.wallet_repository = wallet_repository  # Repositório de wallets (pode ser um banco de dados)

    def credit(self, user_id: str, amount: float):
        """Credita a quantidade na wallet do usuário"""
        wallet = self.wallet_repository.get_wallet(user_id)
        if wallet:
            wallet.credit(amount)
            self.wallet_repository.update_wallet(wallet)
        else:
            raise ValueError(f"Wallet for user {user_id} not found")

    def debit(self, user_id: str, amount: float):
        """Debita a quantidade na wallet do usuário"""
        wallet = self.wallet_repository.get_wallet(user_id)
        if wallet:
            wallet.debit(amount)
            self.wallet_repository.update_wallet(wallet)
        else:
            raise ValueError(f"Wallet for user {user_id} not found")

    def lock_funds(self, user_id: str, amount: float):
        """Bloqueia fundos na wallet do usuário"""
        wallet = self.wallet_repository.get_wallet(user_id)
        if wallet:
            wallet.lock_funds(amount)
            self.wallet_repository.update_wallet(wallet)
        else:
            raise ValueError(f"Wallet for user {user_id} not found")

    def unlock_funds(self, user_id: str, amount: float):
        """Desbloqueia fundos na wallet do usuário"""
        wallet = self.wallet_repository.get_wallet(user_id)
        if wallet:
            wallet.unlock_funds(amount)
            self.wallet_repository.update_wallet(wallet)
        else:
            raise ValueError(f"Wallet for user {user_id} not found")
