from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List

class Usuario(SQLModel, table=True):
    __tablename__ = 'usuarios'

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    nome: str = Field(max_length=100)
    email: str = Field(max_length=50)
    senha: str = Field()
    saldo_usuario: float = Field(default=0.0)
    criado_em: datetime = Field(default_factory=datetime.now)
    ativo: bool = Field(default=True)
    transacoes: List['Transacao'] = Relationship(back_populates="usuario", cascade_delete=True)
    conta_bancaria: List['ContaBancaria'] = Relationship(back_populates="usuario", cascade_delete=True)
    categoria: List['Categoria'] = Relationship(back_populates="usuario", cascade_delete=True)
    recupera_senha: List['RecuperaSenha'] = Relationship(back_populates="usuario", cascade_delete=True)
    secret_key: str = Field(nullable=False)
    qrcode: str = Field(nullable=True)
    primeiro_login: bool = Field(default=True)
    refresh_token: str = Field(nullable=True)

class RecuperaSenha(SQLModel, table=True):
    __tablename__ = 'recupera_senha'

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    usuario_id: int = Field(foreign_key="usuarios.id")
    usuario: Usuario = Relationship(back_populates="recupera_senha")
    token: str = Field()
    criado_em: datetime = Field(default_factory=datetime.now)
    

class ContaBancaria(SQLModel, table=True):
    __tablename__ = 'conta_bancaria'

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    usuario_id: int = Field(foreign_key="usuarios.id")
    usuario: Usuario = Relationship(back_populates="conta_bancaria")
    nome: str = Field(max_length=100)
    saldo_conta: float = Field(default=0.0)
    transacoes: List['Transacao'] = Relationship(back_populates="conta_bancaria", cascade_delete=True)
    criado_em: datetime = Field(default_factory=datetime.now)

class Transacao(SQLModel, table=True):
    __tablename__ = 'transacao'

    id: int | None = Field(default=None, primary_key=True, index=True)
    usuario_id: int = Field(foreign_key="usuarios.id")
    conta_bancaria_id: Optional[int] = Field(default=None, foreign_key="conta_bancaria.id")
    conta_bancaria: Optional[ContaBancaria] = Relationship(back_populates="transacoes")
    usuario: Usuario = Relationship(back_populates="transacoes")
    valor: float = Field()
    data: datetime = Field(default_factory=datetime.now)
    categoria_id: int = Field(foreign_key="categoria.id")
    tipo_id: int = Field(foreign_key="tipo.id")

class Tipo(SQLModel, table=True):
    __tablename__ = 'tipo'

    id: int | None = Field(default=None, primary_key=True, index=True)
    tipo: str = Field(nullable=False)
    categoria: List['Categoria'] = Relationship(back_populates="tipo")

class Categoria(SQLModel, table=True):
    __tablename__ = 'categoria'

    id: int | None = Field(default=None, primary_key=True, index=True)
    usuario_id: int | None = Field(foreign_key="usuarios.id")
    usuario: Usuario | None = Relationship(back_populates="categoria")
    tipo_id: int = Field(foreign_key="tipo.id")
    tipo: Tipo = Relationship(back_populates="categoria")
    categoria: str = Field(nullable=False)