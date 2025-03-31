from sqlmodel import select, Session
from database.models import ContaBancaria, Usuario
from fastapi import HTTPException
from pydantic import BaseModel

class ContaBancariaRequest(BaseModel):
    nome: str
    saldo: float


async def retorna_contas_usuario(user, db: Session):
    try:
        query = select(ContaBancaria).where(ContaBancaria.usuario_id == user['id'])
        print(query)
        results = db.exec(query).all()
        if not results:
            raise HTTPException(status_code=404, detail="Usuário não possui contas bancárias")
        return results
    except Exception as e:
        return {"message":f"Erro ao requisitar contas bancárias do usuário: {e}"}

async def cria_conta_usuario(create_conta: ContaBancariaRequest, user, db: Session):
    try:
        cria_conta = ContaBancaria(
            usuario_id=user['id'],
            nome=create_conta.nome,
            saldo_conta=create_conta.saldo
        )
        query = select(ContaBancaria).where(ContaBancaria.nome == cria_conta.nome, ContaBancaria.usuario_id == user['id'])
        consulta = db.exec(query).first()
        if consulta:
            raise HTTPException(status_code=400, detail="Conta Bancária Já Registrada")
        else:
            db.add(cria_conta)
            db.commit()
            query = select(Usuario).where(Usuario.id == user['id'])
            usuario = db.exec(query).first()
            usuario.saldo_usuario += create_conta.saldo
            db.commit()
            return {"201": "Conta Criada"}
    except Exception as e:
        return {"message":f"Erro ao criar conta bancária do usuário: {e}"}