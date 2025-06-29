from sqlmodel import select, Session
from database.models import ContaBancaria, Usuario, Transacao
from fastapi import HTTPException
from starlette import status

async def retorna_dashboard(user, db:Session):
    try:
        statement = select(Usuario).where(Usuario.id == user["id"])
        query_user = db.exec(statement).first()
        saldo_total = query_user.saldo_usuario

        statement = select(ContaBancaria).where(ContaBancaria.usuario_id == user["id"])
        query_contas = db.exec(statement).all()

        statement = select(Transacao).where(Transacao.usuario_id == user["id"], Transacao.tipo_id == 1)
        query_receitas = db.exec(statement).all()

        statement = select(Transacao).where(Transacao.usuario_id == user["id"], Transacao.tipo_id == 2)
        query_despesas = db.exec(statement).all()

        return {"dados":[
            {"saldo_conta": saldo_total},
            {"contas": query_contas},
            {"receitas": query_receitas},
            {"despesas": query_despesas}
        ]}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao retornar dados: {e}")