from sqlmodel import select, Session
from sqlalchemy import or_
from database.models import Categoria
from fastapi import HTTPException
from starlette import status


async def retorna_categorias(user, db: Session):
    try:
        query = select(Categoria).where(or_(Categoria.usuario_id == user['id'], Categoria.usuario_id.is_(None)))
        categorias = db.exec(query).all()
        if not categorias:
            raise HTTPException(status_code=404, detail="Nenhuma categoria encontrada")
        return categorias
    except Exception as e:
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao retornar categorias")
    
async def cria_categoria(tipo, categoria, user, db: Session):
    try:
        categoria = new Categoria(
            usuario_id=user['id'],
            tipo_id=tipo,
            categoria=categoria
        )
        db.add(categoria)
        db.commit()
        return {"message":"Categoria criada com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao criar categoria")
    
async def edita_categoria(id, tipo, categoria, user, db: Session):
    try:
        query = select(Categoria).where(Categoria.id == id, Categoria.usuario_id == user['id'])
        categoria_db = db.exec(query).first()
        if not categoria_db:
            raise HTTPException(status_code=404, detail="Categoria não encontrada")
        if tipo:
            categoria_db.tipo_id = tipo
        if categoria:
            categoria_db.categoria = categoria
        db.add(categoria_db)
        db.commit()
        return {"message":"Categoria editada"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao editar categoria")
    
async def deleta_categorias(id,user,db:Session):
    try:
        query = select(Categoria).where(Categoria.id == id, Categoria.usuario_id == user['id'])
        categoria = db.exec(query).first()
        db.delete(categoria)
        db.commit()
        return {"message":"Categoria deletada"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao deletar categoria")