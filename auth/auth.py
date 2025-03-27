import base64
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from starlette import status
from database.db import get_db
from database.models import Usuario, RecuperaSenha
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from setup.settings import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_TIME, REFRESH_TOKEN_EXPIRE_TIME, APP_URL, email_conf
from pydantic import BaseModel, EmailStr
from auth.m2f import *

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/login')

class CreateUserRequest(BaseModel):
    nome: str
    email: EmailStr
    password: str

db_dependency = Annotated[Session, Depends(get_db)]

@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency,
                      create_user_request: CreateUserRequest):
    if create_user_request.nome == '':
        raise HTTPException(status_code=400, detail="O campo de nome deve ser preenchido")
    if create_user_request.password == '':
        raise HTTPException(status_code=400, detail="O campo de senha deve ser preenchido")
    else:
        try:
            secret_encoded, qrcode = gera_m2f(create_user_request.email)
            create_user_model = Usuario(
                nome=create_user_request.nome,
                email=create_user_request.email,
                senha=bcrypt_context.hash(create_user_request.password),
                secret_key=secret_encoded,
                qrcode=qrcode
            )
            query = select(Usuario).where(Usuario.email == create_user_model.email)
            consulta = db.exec(query).first()
            if consulta:
                raise HTTPException(status_code=409, detail="Email já existente")
            else:
                db.add(create_user_model)
                db.commit()
                return {"201": "Usuário Criado"}
        except Exception as e:
            raise HTTPException(status_code=e.status_code, detail=f"Erro ao criar usuário: {e}")

@router.post("/login")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):
    try:
        user = authenticate_user(form_data.username, form_data.password, db)
        if user == False:
            raise HTTPException(status_code=400, detail=f"Erro ao realizar login")
        else:
            if user.primeiro_login == True:
                return {"id":user.id}
            return {"id":user.id,"primeiro_login":user.primeiro_login}
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Erro ao realizar login: {e}")

@router.get("/qr/{id}")
async def qrcode(id: int, db: db_dependency):
    try:
        statement = select(Usuario).where(Usuario.id == id)
        query = db.exec(statement).first()
        return {"qrcode": query.qrcode, "id":f"{id}"}
    except Exception as e:
        return {"message":f"Erro ao requisitar qrcode: {e}"}

@router.post("/m2f/{id}")
async def m2f_verification(id: int, otp: str, db: db_dependency):
    try:
        statement = select(Usuario).where(Usuario.id == id)
        query = db.exec(statement).first()
        verify = verifica_m2f(query.secret_key, otp)
        if verify == True:
            query.primeiro_login = False
            query.qrcode = ''
            tokens = create_access_token(query.email, query.id, db)
            query.refresh_token = tokens[1]["refresh_token"]
            db.commit()
            return {"tokens": tokens}
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="OTP inválido")
    except Exception as e:
        return {"message":f"Erro ao verificar OTP: {e}"}
    
@router.get("/m2f/recovery/{id}")
async def m2f_recovery(id: int, db: db_dependency):
    try:
       statement = select(Usuario).where(Usuario.id == id)
       query = db.exec(statement).first()
       return await recupera_m2f(query.email, db)
    except Exception as e:
        return {"message":f"Erro ao recuperar m2f: {e}"}

def authenticate_user(email: str, password: str, db):
    try:
        user = select(Usuario).where(Usuario.email == email)
        query = db.exec(user).first()
        if not query or not bcrypt_context.verify(password, query.senha):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Credenciais Incorretas")
        return query
    except Exception as e:
        return False

def create_access_token(email: str, user_id: int, db: db_dependency):
    try:
        access_encode = {"sub": email, "id": user_id}
        access_expires = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_TIME)
        access_encode.update({"exp": access_expires})
        refresh_encode = {"sub": email, "id": user_id}
        refresh_expires = datetime.now(timezone.utc) + timedelta(hours=REFRESH_TOKEN_EXPIRE_TIME)
        refresh_encode.update({"exp": refresh_expires})
        access_jwt = jwt.encode(access_encode, SECRET_KEY, algorithm=ALGORITHM)
        refresh_jwt = jwt.encode(refresh_encode, SECRET_KEY, algorithm=ALGORITHM)
        user = select(Usuario).where(Usuario.id == user_id)
        query = db.exec(user).first()
        query.refresh_token = refresh_jwt
        db.commit()
        return [{"access_token": access_jwt, "token_type": "Bearer", "expires_in": f"{ACCESS_TOKEN_EXPIRE_TIME} Hours"},{"refresh_token": refresh_jwt, "token_type": "Bearer", "expires_in": f"{REFRESH_TOKEN_EXPIRE_TIME} Hours"}]
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Erro ao gerar token o usuário:{e}")
    
@router.get("/user")
async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        user_id: int = payload.get("id")
        print(f"email: {email}, id:{user_id}, exp: {payload.get("exp")}")
        if email is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Não pode verificar o usuário.")
        return {"email": email, "id": user_id}
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"Erro ao verificar o usuário:{e}")

@router.post("/token/refresh")
async def refresh_token(refresh_token: Annotated[str, Depends(oauth2_bearer)], db: db_dependency):
    refresh = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
    id = refresh.get("id")
    user = select(Usuario).where(Usuario.id == id)
    query = db.exec(user).first()
    exp_timestamp = refresh.get("exp")
    if exp_timestamp:
        try:
            exp_datetime = datetime.fromtimestamp(exp_timestamp, timezone.utc)
            if datetime.now(timezone.utc)>exp_datetime:
            if datetime.now(timezone.utc)>exp_datetime:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                    detail="Refresh token expirou, refaça o login.")
            else:
                print(query.refresh_token)
                if query.refresh_token == refresh_token:
                    token = create_access_token(query.email, query.id, db)
                    query.refresh_token = token[1]["refresh_token"]
                    db.commit()
                    return token
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                detail=f"Ocorreu um erro ao verificar o token: {e} token: {refresh_token}")

@router.post("/recoverpassword")
async def token_recupera_senha(email: EmailStr, db: db_dependency):
    try:
        user = select(Usuario).where(Usuario.email == email)
        query = db.exec(user).first()
        token = base64.b64encode(email).decode("utf-8")
        cria_token = RecuperaSenha(
            usuario_id = query.id,
            token = token
        )
        db.add(cria_token)
        db.commit()

        body = templates.get_template('email.html').render(url=str(f"{APP_URL}/recoverpassword?token={token}"), title="Recuperação de senha", message="Seu link de recuperação de senha foi gerado:")

        message = MessageSchema(
            subject="Recuperação de Senha",
            recipients=[email],
            body=body,
            subtype='html',
            headers={"Content-Type": "text/html; charset=UTF-8"}
        )

        fm = FastMail(email_conf)
        await fm.send_message(message)
        return {"message":"Email de Recuperação Enviado"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Erro ao gerar email de recuperação: {e}")
    
@router.post("/recoverpassword/{token}")
async def recupera_senha(token: str, nova_senha: str, db: db_dependency):
    try:
        query = select(RecuperaSenha).where(RecuperaSenha.token == token)
        result = db.exec(query).first()
        if not result:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token Inválido")
        else:
            user = select(Usuario).where(Usuario.id == result.usuario_id)
            query = db.exec(user).first()
            query.senha = bcrypt_context.hash(nova_senha)
            db.delete(result)
            db.commit()
            return {"message":"Senha Alterada"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Erro ao recuperar senha: {e}")
