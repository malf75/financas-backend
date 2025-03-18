from sqlmodel import select, Session
from sqlalchemy import or_
from database.models import Categoria
from fastapi import HTTPException


async def retorna_categorias(user, db: Session):
    try:
        query = select(Categoria).where(or_(Categoria.usuario_id == user['id'], Categoria.usuario_id.is_(None)))
        categorias = db.exec(query).all()
        if not categorias:
            raise HTTPException(status_code=404, detail="Nenhuma categoria encontrada")
        return categorias
    except Exception as e:
        return {"message":f"Erro ao retornar categorias: {e}"}