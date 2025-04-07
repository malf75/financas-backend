from sqlmodel import select, Session
from database.models import ContaBancaria, Usuario, Transacao
from fastapi import HTTPException
from services.huggingAPI import hugging_api_request

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

        response = hugging_api_request(
            f"Saldo_total: {saldo_total}, Contas_bancarias: {query_contas}, Receitas: {query_receitas}, Despesas: {query_despesas}"
        )

        return {"dados":[
            {"saldo_conta": saldo_total},
            {"contas": query_contas},
            {"receitas": query_receitas},
            {"despesas": query_despesas},
            response
        ]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao retornar dados: {e}")