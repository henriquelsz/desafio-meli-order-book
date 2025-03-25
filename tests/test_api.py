import requests
import time

BASE_URL = "http://localhost:8000"

# 1️⃣ Criar carteiras para comprador e vendedor
buyer_wallet = requests.post(f"{BASE_URL}/wallets", json={"wallet_id": "buyer_wallet"}).json()
seller_wallet = requests.post(f"{BASE_URL}/wallets", json={"wallet_id": "seller_wallet"}).json()

print("Carteiras criadas:", buyer_wallet, seller_wallet)

# 2️⃣ Criar ordens de compra e venda
buy_order = requests.post(f"{BASE_URL}/orders", json={
    "wallet_id": "buyer_wallet",
    "order_type": "BUY",
    "quantity": 10,
    "price": 100
}).json()

sell_order = requests.post(f"{BASE_URL}/orders", json={
    "wallet_id": "seller_wallet",
    "order_type": "SELL",
    "quantity": 10,
    "price": 100
}).json()

print("Ordens criadas:", buy_order, sell_order)

# 3️⃣ Executar o matching das ordens
match_response = requests.post(f"{BASE_URL}/match").json()
print("Matching realizado:", match_response)

# 🔄 Aguardar um tempo para o RabbitMQ processar os eventos
time.sleep(2)

# 4️⃣ Consultar saldo atualizado das carteiras
buyer_wallet_updated = requests.get(f"{BASE_URL}/wallets/buyer_wallet").json()
seller_wallet_updated = requests.get(f"{BASE_URL}/wallets/seller_wallet").json()

print("Saldo atualizado do comprador:", buyer_wallet_updated)
print("Saldo atualizado do vendedor:", seller_wallet_updated)
