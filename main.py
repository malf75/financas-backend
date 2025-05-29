from fastapi.responses import RedirectResponse
from typing import Optional
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
from pydantic import BaseModel
from datetime import datetime
import os
import uvicorn

class ContaBancariaRequest(BaseModel):
    nome: str
    saldo: int

class EditaContaBancariaRequest(BaseModel):
    id: int
    nome: str | None = None
    saldo: int | None = None

class TransacaoRequest(BaseModel):
    descricao: str
    valor: int
    tipo: int
    categoria: str
    conta: int | None = None

class EditaTransacaoRequest(BaseModel):
    id: int
    descricao: str | None = None
    valor: int | None = None
    tipo: int | None = None
    categoria: str | None = None
    conta: int | None = None

class EditaCategoriaRequest(BaseModel):
    id: int
    tipo: int | None = None
    categoria: str | None = None

class CriaCategoriaRequest(BaseModel):
    tipo: int
    categoria: str
    
app.include_router(router)
user_dependency = Annotated[dict, Depends(get_current_user)]
db = Annotated[Session, Depends(get_db)]

@app.get("/")
def redirect_index():
    return RedirectResponse("/docs")

@app.get("/dashboard")
async def rota_dashboard(user: user_dependency, db: Session = Depends(get_db)):
    try:
        results = await retorna_dashboard(user, db)
        return results
    except Exception as e:
        return e

@app.get("/contabancaria")
async def rota_conta_bancaria(user: user_dependency, db: Session = Depends(get_db)):
    try:
        results = await retorna_contas_usuario(user, db)
        return results
    except Exception as e:
        return e

@app.post("/contabancaria/criaconta")
async def rota_cria_conta(create_conta: ContaBancariaRequest, user: user_dependency, db: Session = Depends(get_db)):
    try:
        result = await cria_conta_usuario(create_conta.nome, create_conta.saldo, user, db)
        return result
    except Exception as e:
        return e
    
@app.patch("/contabancaria/editaconta")
async def rota_edita_conta(edit_conta: EditaContaBancariaRequest, user: user_dependency, db: Session = Depends(get_db)):
    try:
        result = await edita_conta_bancaria_usuario(edit_conta.id, edit_conta.nome, edit_conta.saldo, user, db)
        return result
    except Exception as e:
        return e
    
@app.delete("/contabancaria")
async def rota_deleta_conta_bancaria(id: int, user: user_dependency, db: Session = Depends(get_db)):
    try:
        result = await deleta_conta_bancaria_usuario(id,user,db)
        return result
    except Exception as e:
        return e

@app.get("/transacoes")
async def rota_retorna_transacoes(user: user_dependency, receitas: Optional[bool] = None, despesas: Optional[bool] = None, inicio: Optional[datetime] = None, fim: Optional[datetime] = None, db: Session = Depends(get_db)):
    try:
        result = await retorna_transacoes(receitas,despesas, inicio, fim,user, db)
        return result
    except Exception as e:
        return e

@app.post("/criatransacao")
async def rota_cria_transacao(transacao: TransacaoRequest, user: user_dependency, db: Session = Depends(get_db)):
    try:
        result = await cria_transacao(transacao.descricao, transacao.valor, transacao.tipo, transacao.categoria, transacao.conta, user, db)
        return result
    except Exception as e:
        return e
    
@app.patch("/editatransacao")
async def rota_edita_transacao(transacao: EditaTransacaoRequest, user: user_dependency, db: Session = Depends(get_db)):
    try:
        result = await edita_transacao(transacao.id, transacao.descricao ,transacao.valor, transacao.tipo, transacao.categoria, transacao.conta, user, db)
        return result
    except Exception as e:
        return e
    
@app.delete("/apagatransacao")
async def rota_deleta_transacao(id: int, user: user_dependency, db: Session = Depends(get_db)):
    try:
        result = await deleta_transacao(id, user, db)
        return result
    except Exception as e:
        return e

@app.get("/categorias")
async def rota_categorias(user: user_dependency, db: Session = Depends(get_db)):
    try:
        result = await retorna_categorias(user, db)
        return result
    except Exception as e:
        return e
    
@app.post("/categorias")
async def rota_cria_categorias(categoria: CriaCategoriaRequest, user: user_dependency, db: Session = Depends(get_db)):
    try:
        result = await cria_categoria(categoria.tipo, categoria.categoria, user, db)
        return result
    except Exception as e:
        return e
    
@app.patch("/categorias")
async def rota_edita_categoria(categoria: EditaCategoriaRequest, user: user_dependency, db: Session = Depends(get_db)):
    try:
        result = await edita_categoria(categoria.id, categoria.tipo, categoria.categoria, user, db)
        return result
    except Exception as e:
        return e
    
@app.delete("/categorias")
async def rota_deleta_categoria(id: int, user: user_dependency, db: Session = Depends(get_db)):
    try:
        result = await deleta_categorias(id, user, db)
        return result
    except Exception as e:
        return e



if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="127.0.0.1", port=port)