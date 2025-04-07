from sqlmodel import select, Session
from database.models import ContaBancaria, Usuario, Transacao, Categoria
from fastapi import HTTPException
from services.huggingAPI import hugging_api_request
from starlette import status

async def cria_transacao(valor, tipo, categoria, user, db:Session, conta):
    try:
        try:
            int(categoria)
            categoria_final = categoria
        except ValueError:
            query_igualdade = select(Categoria).where(Categoria.categoria == categoria, Categoria.usuario_id == user['id'])
            result_igualdade = db.exec(query_igualdade).first()
            if result_igualdade:
                categoria_final = result_igualdade.id
            else:
                cria_categoria = Categoria(
                    usuario_id=user['id'],
                    tipo_id=tipo,
                    categoria=categoria
                )
                db.add(cria_categoria)
                db.commit()
                query = select(Categoria).where(Categoria.categoria == categoria, Categoria.usuario_id == user['id'])
                result = db.exec(query).first()
                categoria_final = result.id

        cria_transacao = Transacao(
            usuario_id=user['id'], 
            conta_bancaria_id=conta, 
            tipo_id=tipo, 
            valor=valor, 
            categoria_id=categoria_final
            )
        
        db.add(cria_transacao)

        if tipo == 1:
            query = select(Usuario).where(Usuario.id == user['id'])
            usuario = db.exec(query).first()
            usuario.saldo_usuario += valor
            if conta:
                query = select(ContaBancaria).where(ContaBancaria.id == conta)
                conta = db.exec(query).first()
                conta.saldo_conta += valor
        if tipo == 2:
            query = select(Usuario).where(Usuario.id == user['id'])
            usuario = db.exec(query).first()
            usuario.saldo_usuario -= valor
            if conta:
                query = select(ContaBancaria).where(ContaBancaria.id == conta)
                conta = db.exec(query).first()
                conta.saldo_conta -= valor

        db.commit()

        return {"201": "Transação criada com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao criar transação: {e}")
    
async def edita_transacao(valor, tipo, categoria, user, db:Session, id_transacao):
    try:
        query = select(Usuario).where(Usuario.id == user['id'])
        usuario = db.exec(query).first()
        query = select(Transacao).where(Transacao.id == id_transacao, Transacao.usuario_id == user['id'])
        transacao = db.exec(query).first()
        if categoria:
            try:
                int(categoria)
                categoria_final = categoria
            except ValueError:
                query_igualdade = select(Categoria).where(Categoria.categoria == categoria, Categoria.usuario_id == user['id'])
                result_igualdade = db.exec(query_igualdade).first()
                if result_igualdade:
                    categoria_final = result_igualdade.id
                else:
                    cria_categoria = Categoria(
                        usuario_id=user['id'],
                        tipo_id=tipo,
                        categoria=categoria
                    )
                    db.add(cria_categoria)
                    db.commit()
                    query = select(Categoria).where(Categoria.categoria == categoria, Categoria.usuario_id == user['id'])
                    result = db.exec(query).first()
                    categoria_final = result.id
                    transacao.categoria_id = categoria_final
        if valor:
            if tipo != None and tipo != transacao.tipo_id:
                if tipo == 1:
                    usuario.saldo_usuario += transacao.valor + valor
                    if conta:
                        query = select(ContaBancaria).where(ContaBancaria.id == conta)
                        conta = db.exec(query).first()
                        conta.saldo_conta += transacao.valor + valor
                if tipo == 2:
                    usuario.saldo_usuario -= valor - transacao.valor
                    if conta:
                        query = select(ContaBancaria).where(ContaBancaria.id == conta)
                        conta = db.exec(query).first()
                        conta.saldo_conta -= valor - transacao.valor
            else:
                if tipo == 1:
                    usuario.saldo_usuario -= transacao.valor + valor
                    if conta:
                        query = select(ContaBancaria).where(ContaBancaria.id == conta)
                        conta = db.exec(query).first()
                        conta.saldo_conta -= transacao.valor + valor
                if tipo == 2:
                    usuario.saldo_usuario += transacao.valor - valor
                    if conta:
                        query = select(ContaBancaria).where(ContaBancaria.id == conta)
                        conta = db.exec(query).first()
                        conta.saldo_conta += transacao.valor - valor
        db.commit()
        return {"200":"Transação editada"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao editar transação: {e}")
    
async def deleta_transacao(id_transacao, user, db:Session):
    try:
        query = select(Transacao).where(Transacao.id == id_transacao, Transacao.usuario_id == user['id'])
        transacao = db.exec(query).first()
        db.delete(transacao)
        db.commit()
        return {"200":"Transação deletada"}
    except Exception as e:
        return {"message":f"Erro ao deletar transação: {e}"}

async def retorna_receitas(user, db:Session):
    try:
        query = select(Transacao).where(Transacao.usuario_id == user['id'], Transacao.tipo_id == 1)
        receitas = db.exec(query).all()
        if not receitas:
            raise HTTPException(status_code=404, detail="Nenhuma receita encontrada")
        response = hugging_api_request(receitas)
        return {"Receitas": receitas, "Dicas": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao retornar receitas do usuário: {e}")


async def retorna_despesas(user, db: Session):
    try:
        query = select(Transacao).where(Transacao.usuario_id == user['id'], Transacao.tipo_id == 2)
        despesas = db.exec(query).all()
        if not despesas:
            raise HTTPException(status_code=404, detail="Nenhuma despesa encontrada")
        response = hugging_api_request(despesas)
        return {"Despesas": despesas, "Dicas": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao retornar despesas do usuário: {e}")


