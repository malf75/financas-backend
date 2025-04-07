from fastapi.responses import RedirectResponse
from setup.settings import app
from auth.auth import router, get_current_user
from typing import Annotated
from database.db import get_db, engine
from controller.conta_bancaria_controller import *
from controller.transacao_controller import *
from controller.categoria_controller import *
from controller.dashboard_controller import *
from sqlmodel import Session, SQLModel
from fastapi import Depends
import os
import uvicorn

class ContaBancariaRequest(BaseModel):
    nome: str
    saldo: int

class TransacaoRequest(BaseModel):
    valor: int
    tipo: int
    categoria: str
    conta: int | None = None

app.include_router(router)
user_dependency = Annotated[dict, Depends(get_current_user)]
db = Annotated[Session, Depends(get_db)]

SQLModel.metadata.create_all(engine)

@app.get("/")
def redirect_index():
    return RedirectResponse("/docs")

@app.get("/dashboard")
async def rota_dashboard(user: user_dependency, db: Session = Depends(get_db)):
    try:
        results = await retorna_dashboard(user, db)
        return results
    except Exception as e:
        return {e}

@app.get("/contabancaria")
async def rota_conta_bancaria(user: user_dependency, db: Session = Depends(get_db)):
    try:
        results = await retorna_contas_usuario(user, db)
        return results
    except Exception as e:
        return {e}

@app.post("/contabancaria/criaconta")
async def rota_cria_conta(create_conta: ContaBancariaRequest, user: user_dependency, db: Session = Depends(get_db)):
    try:
        result = await cria_conta_usuario(create_conta.nome, create_conta.saldo, user, db)
        return result
    except Exception as e:
        return {"erro": str(e)}
    
@app.delete("/contabancaria")
async def deleta_conta_bancaria(id: int, user: user_dependency, db: Session = Depends(get_db)):
    try:
        result = await deleta_conta_bancaria_usuario(id,user,db)
        return result
    except Exception as e:
        return {"erro": str(e)}

@app.post("/criatransacao")
async def rota_cria_transacao(transacao: TransacaoRequest, user: user_dependency, db: Session = Depends(get_db)):
    try:
        result = await cria_transacao(transacao.valor, transacao.tipo, transacao.categoria, user, db, transacao.conta)
        return result
    except Exception as e:
        return {"erro": str(e)}

@app.get("/categorias")
async def rota_categorias(user: user_dependency, db: Session = Depends(get_db)):
    try:
        result = await retorna_categorias(user, db)
        return result
    except Exception as e:
        return {"erro": str(e)}
    
@app.delete("/categorias")
async def deleta_categoria(id: int, user: user_dependency, db: Session = Depends(get_db)):
    try:
        result = await deleta_categorias(id, user, db)
        return result
    except Exception as e:
        return {"erro": str(e)}

@app.get("/transacoes/receitas")
async def rota_receitas(user: user_dependency, db: Session = Depends(get_db)):
    try:
        result = await retorna_receitas(user, db)
        return result
    except Exception as e:
        return {"erro": str(e)}

@app.get("/transacoes/despesas")
async def rota_despesas(user: user_dependency, db: Session = Depends(get_db)):
    try:
        result = await retorna_despesas(user, db)
        return result
    except Exception as e:
        return {"erro": str(e)}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="127.0.0.1", port=port)