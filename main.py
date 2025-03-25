from fastapi import FastAPI
from api.routes import router

app = FastAPI(title="Order Book", description= "API para negociação de Vibranium")

#Incluindo as rotas da api
app.include_router(router)

#endpoint raiz
@app.get("/")
def root():
    return {"message": "Order Book API inicializado"}

