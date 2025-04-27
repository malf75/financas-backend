from sqlmodel import select, Session
from database.models import ContaBancaria, Usuario, Transacao, Categoria
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from services.huggingAPI import hugging_api_request
from starlette import status

async def cria_transacao(descricao, valor, tipo, categoria, conta, user, db:Session):
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
            descricao=descricao,
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

        return JSONResponse(status_code=status.HTTP_201_CREATED, content="Transação criada com sucesso!")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao criar transação: {e}")
    
async def edita_transacao(id_transacao, descricao, valor, tipo, categoria, conta_edicao, user, db: Session):
    try:
        query = select(Usuario).where(Usuario.id == user['id'])
        usuario = db.exec(query).first()
        query = select(Transacao).where(Transacao.id == id_transacao)

        transacao = db.exec(query).first()
        if descricao:
            transacao.descricao = descricao

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
                    nova_categoria = Categoria(
                        usuario_id=user['id'],
                        tipo_id=tipo,
                        categoria=categoria
                    )
                    db.add(nova_categoria)
                    db.commit()
                    db.refresh(nova_categoria)
                    categoria_final = nova_categoria.id
            transacao.categoria_id = categoria_final

        if valor:
            valor_antigo = transacao.valor
            tipo_antigo = transacao.tipo_id

            if not tipo:
                tipo = tipo_antigo

            if tipo_antigo == 1:
                usuario.saldo_usuario -= valor_antigo
            else:
                usuario.saldo_usuario += valor_antigo

            if tipo == 1:
                usuario.saldo_usuario += valor
            else:
                usuario.saldo_usuario -= valor

            if conta_edicao:
                query = select(ContaBancaria).where(ContaBancaria.id == transacao.conta_bancaria_id)
                conta_antiga = db.exec(query).first()
                query = select(ContaBancaria).where(ContaBancaria.id == conta_edicao)
                conta = db.exec(query).first()

                if tipo_antigo == 1:
                    conta_antiga.saldo_conta -= valor_antigo
                else:
                    conta_antiga.saldo_conta += valor_antigo

                if tipo == 1:
                    conta.saldo_conta += valor
                else:
                    conta.saldo_conta -= valor

            transacao.valor = valor
            transacao.tipo_id = tipo

        db.commit()
        return JSONResponse(status_code=status.HTTP_200_OK, content="Transação editada com sucesso!")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao editar transação: {e}")
    
async def deleta_transacao(id_transacao, user, db:Session):
    try:
        query = select(Transacao).where(Transacao.id == id_transacao, Transacao.usuario_id == user['id'])
        transacao = db.exec(query).first()
        db.delete(transacao)
        db.commit()
        return JSONResponse(status_code=status.HTTP_200_OK, content="Transação deletada com sucesso!")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao deletar transação: {e}")

async def retorna_transacoes(receitas, despesas, inicio, fim, user, db:Session):
    try:
        query = select(Transacao).where(Transacao.usuario_id == user["id"])
        if receitas:
            query = query.where(Transacao.tipo_id == 1)
        if despesas:
            query = query.where(Transacao.tipo_id == 2)
        if inicio:
            query = query.where(inicio <= Transacao.data)
        if fim:
            query = query.where(fim >= Transacao.data)
        transacoes = db.exec(query).all()
        return {"Transacoes": transacoes}
    except Exception as e:
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao retornar transações: {e}")


