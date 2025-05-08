from pydantic import BaseModel

class ContaBancariaRequest(BaseModel):
    nome: str
    saldo: int

class EditaContaBancariaRequest(BaseModel):
    id: int
    nome: str | None = None
    saldo: int | None = None

class TransacaoRequest(BaseModel):
    descricao: str
    valor: int
    tipo: int
    categoria: str
    conta: int | None = None

class EditaTransacaoRequest(BaseModel):
    id: int
    descricao: str | None = None
    valor: int | None = None
    tipo: int | None = None
    categoria: str | None = None
    conta: int | None = None

class EditaCategoriaRequest(BaseModel):
    id: int
    tipo: int | None = None
    categoria: str | None = None

class CriaCategoriaRequest(BaseModel):
    tipo: int
    categoria: str