from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional, List


class Usuario(SQLModel, table=True):
    __tablename__ = 'usuarios'

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    nome: str = Field(max_length=100)
    email: str = Field(max_length=50)
    senha: str
    saldo_usuario: int = Field(default=0)
    criado_em: datetime = Field(default_factory=datetime.now)
    ativo: bool = Field(default=True)

    transacoes: List["Transacao"] = Relationship(
        back_populates="usuario",
        sa_relationship=relationship("Transacao", back_populates="usuario", cascade="all, delete-orphan")
    )

    conta_bancaria: List["ContaBancaria"] = Relationship(
        back_populates="usuario",
        sa_relationship=relationship("ContaBancaria", back_populates="usuario", cascade="all, delete-orphan")
    )

    categoria: List["Categoria"] = Relationship(
        back_populates="usuario",
        sa_relationship=relationship("Categoria", back_populates="usuario", cascade="all, delete-orphan")
    )

    recupera_senha: List["RecuperaSenha"] = Relationship(
        back_populates="usuario",
        sa_relationship=relationship("RecuperaSenha", back_populates="usuario", cascade="all, delete-orphan")
    )

    secret_key: Optional[str] = None
    qrcode: Optional[str] = None
    primeiro_login: bool = Field(default=True)
    refresh_token: Optional[str] = None


class RecuperaSenha(SQLModel, table=True):
    __tablename__ = 'recupera_senha'

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    usuario_id: int = Field(foreign_key="usuarios.id")
    usuario: Optional[Usuario] = Relationship(back_populates="recupera_senha")
    token: str
    criado_em: datetime = Field(default_factory=datetime.now)


class ContaBancaria(SQLModel, table=True):
    __tablename__ = 'conta_bancaria'

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    usuario_id: int = Field(foreign_key="usuarios.id")
    usuario: Optional[Usuario] = Relationship(back_populates="conta_bancaria")

    nome: str = Field(max_length=100)
    saldo_conta: int = Field(default=0)
    criado_em: datetime = Field(default_factory=datetime.now)

    transacoes: List["Transacao"] = Relationship(
        back_populates="conta_bancaria",
        sa_relationship=relationship("Transacao", back_populates="conta_bancaria", cascade="all, delete-orphan")
    )


class Transacao(SQLModel, table=True):
    __tablename__ = 'transacao'

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    usuario_id: int = Field(foreign_key="usuarios.id")
    descricao: str = Field(max_length=100, nullable=True)
    conta_bancaria_id: Optional[int] = Field(default=None, foreign_key="conta_bancaria.id")
    categoria_id: int = Field(foreign_key="categoria.id")
    tipo_id: int = Field(foreign_key="tipo.id")

    valor: int
    data: datetime = Field(default_factory=datetime.now)

    usuario: Optional[Usuario] = Relationship(back_populates="transacoes")
    conta_bancaria: Optional["ContaBancaria"] = Relationship(back_populates="transacoes")
    categoria: Optional["Categoria"] = Relationship(back_populates="transacoes")
    tipo: Optional["Tipo"] = Relationship(back_populates="transacoes")


class Tipo(SQLModel, table=True):
    __tablename__ = 'tipo'

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    tipo: str

    categoria: List["Categoria"] = Relationship(back_populates="tipo")
    transacoes: List["Transacao"] = Relationship(back_populates="tipo")


class Categoria(SQLModel, table=True):
    __tablename__ = 'categoria'

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    usuario_id: Optional[int] = Field(default=None, foreign_key="usuarios.id")
    tipo_id: int = Field(foreign_key="tipo.id")
    categoria: str

    usuario: Optional[Usuario] = Relationship(back_populates="categoria")
    tipo: Optional["Tipo"] = Relationship(back_populates="categoria")
    transacoes: List["Transacao"] = Relationship(back_populates="categoria")
