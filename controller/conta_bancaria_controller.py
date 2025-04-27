from sqlmodel import select, Session
from database.models import ContaBancaria, Usuario
from fastapi import HTTPException
from fastapi.responses import JSONResponse
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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao requisitar contas bancárias do usuário: {e}")

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
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Conta bancária já registrada")
        else:
            db.add(cria_conta)
            db.commit()
            query = select(Usuario).where(Usuario.id == user['id'])
            usuario = db.exec(query).first()
            usuario.saldo_usuario += saldo_conta
            db.commit()
            return JSONResponse(status_code=status.HTTP_201_CREATED, content="Conta bancária criada com sucesso")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao criar conta bancária do usuário: {e}")
    
async def edita_conta_bancaria_usuario(id, nome, saldo_conta, user, db: Session):
    try:
        print(id, nome, saldo_conta)
        query = select(Usuario).where(Usuario.id == user['id'])
        usuario = db.exec(query).first()
        query = select(ContaBancaria).where(ContaBancaria.id == id, ContaBancaria.usuario_id == user['id'])
        conta = db.exec(query).first()
        if not conta:
            raise HTTPException(status_code=404, detail="Conta bancária não encontrada")
        if nome:
            print("Passou aqui")
            conta.nome = nome
        if saldo_conta:
            print("Tem saldo")
            usuario.saldo_usuario -= conta.saldo_conta
            usuario.saldo_usuario += saldo_conta
            conta.saldo_conta = saldo_conta
        db.add(conta)
        db.commit()
        return JSONResponse(status_code=status.HTTP_200_OK, content="Conta bancária editada com sucesso")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao editar conta")
    
async def deleta_conta_bancaria_usuario(id, user, db: Session):
    try:
        query = select(ContaBancaria).where(ContaBancaria.id == id, ContaBancaria.usuario_id == user["id"])
        conta = db.exec(query).first()
        db.delete(conta)
        db.commit()
        return JSONResponse(status_code=status.HTTP_200_OK, content="Conta bancária deletada com sucesso")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao deletar conta")

