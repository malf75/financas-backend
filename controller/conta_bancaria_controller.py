from sqlmodel import select, Session
from database.models import ContaBancaria, Usuario
from fastapi import HTTPException
from pydantic import BaseModel
from starlette import status

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

async def cria_conta_usuario(nome, saldo_conta, user, db: Session):
    try:
        cria_conta = ContaBancaria(
            usuario_id=user['id'],
            nome=nome,
            saldo_conta=saldo_conta
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
            usuario.saldo_usuario += saldo_conta
            db.commit()
            return {"201": "Conta Criada"}
    except Exception as e:
        return {"message":f"Erro ao criar conta bancária do usuário: {e}"}
    
async def deleta_conta_bancaria_usuario(id, user, db: Session):
    try:
        query = select(ContaBancaria).where(ContaBancaria.id == id, ContaBancaria.usuario_id == user["id"])
        conta = db.exec(query).first()
        db.delete(conta)
        db.commit()
        return {"200":"Conta deletada"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao deletar conta")

