
''' Este script é responsável por resetar e criar as tabelas no banco de dados.'''

from sqlmodel import SQLModel, engine
from sqlalchemy.orm import Session

def create_db_and_tables():
    print("Criando tabelas no banco de dados...")
    SQLModel.metadata.drop_all(engine)
    print(SQLModel.metadata.tables.keys())
    SQLModel.metadata.create_all(engine) 
    print("Tabelas criadas com sucesso!")

    with Session(engine) as session:
        session.commit()

create_db_and_tables() 