import os
from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi_mail import ConnectionConfig

load_dotenv(override=True)
app = FastAPI()

KEY = os.getenv('KEY')
APP_URL = os.getenv('APP_URL')
SECRET_KEY = str(os.getenv('SECRET_KEY'))
DATABASE_URL = str(os.getenv('DATABASE_URL'))
ALGORITHM = str(os.getenv('ALGORITHM'))
ACCESS_TOKEN_EXPIRE_TIME = float(str(os.getenv('ACCESS_TOKEN_EXPIRE_TIME')))
REFRESH_TOKEN_EXPIRE_TIME = int(os.getenv('REFRESH_TOKEN_EXPIRE_TIME'))

email_conf = ConnectionConfig(
    MAIL_USERNAME=str(os.getenv('MAIL_USERNAME')),
    MAIL_PASSWORD=str(os.getenv('MAIL_PASSWORD')),
    MAIL_FROM=str(os.getenv('MAIL_FROM')),
    MAIL_PORT=int(os.getenv('MAIL_PORT')),
    MAIL_SERVER=str(os.getenv('MAIL_SERVER')),
    MAIL_FROM_NAME=str(os.getenv('MAIL_FROM_NAME')),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER=os.path.abspath('./templates')
)

origins = [
    str(os.getenv('APP_URL')),
    str(os.getenv('DEV_URL')),
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)