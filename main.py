from fastapi.responses import RedirectResponse
from setup.settings import app
from auth.auth import router, get_current_user
from typing import Annotated
from database.db import get_db
from controller.conta_bancaria_controller import *
from controller.transacao_controller import *
from controller.categoria_controller import *
from sqlmodel import Session
from fastapi import Depends
import os
import uvicorn

app.include_router(router)
user_dependency = Annotated[dict, Depends(get_current_user)]
db = Annotated[Session, Depends(get_db)]

@app.get("/")
def redirect_index():
    return RedirectResponse("/docs")

@app.get("/dashboard")
async def rota_dashboard(user: user_dependency):
    pass

@app.get("/contabancaria")
async def rota_conta_bancaria(user: user_dependency, db: Session = Depends(get_db)):
    results = await retorna_contas_usuario(user, db)
    return results

@app.post("/contabancaria/criaconta")
async def rota_cria_conta(nome: str, saldo_conta: float, user: user_dependency, db: Session = Depends(get_db)):
    result = await cria_conta_usuario(nome, saldo_conta, user, db)
    return result

@app.post("/criatransacao")
async def rota_cria_transacao(valor: float, tipo: int, categoria: str, user: user_dependency, db: Session = Depends(get_db), conta: int | None = None):
    result = await cria_transacao(valor, tipo, categoria, user, db, conta)
    return result

@app.get("/categorias")
async def rota_categorias(user: user_dependency, db: Session = Depends(get_db)):
    result = await retorna_categorias(user, db)
    return result

@app.get("/transacoes/receitas")
async def rota_receitas(user: user_dependency, db: Session = Depends(get_db)):
    result = await retorna_receitas(user, db)
    return result

@app.get("/transacoes/despesas")
async def rota_despesas(user: user_dependency, db: Session = Depends(get_db)):
    result = await retorna_despesas(user, db)
    return result

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="127.0.0.1", port=port)