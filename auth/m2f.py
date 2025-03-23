import pyotp
import segno
import base64
import io
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from setup.settings import KEY, email_conf, APP_URL
from fastapi_mail import FastMail, MessageSchema
from database.models import Usuario
from sqlmodel import select, Session
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(email_conf.TEMPLATE_FOLDER)

key = base64.b64decode(KEY)

def gera_m2f(email):
    try:
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)

        issuer_name = "Jao Financas"
        user_email = email
        uri = totp.provisioning_uri(user_email, issuer_name=issuer_name)
        qr = segno.make(uri)

        byte_io = io.BytesIO()
        qr.save(byte_io, kind="png", scale=10)
        qr_data = byte_io.getvalue()

        qr_base64 = base64.b64encode(qr_data).decode("utf-8")

        cipher = AES.new(key, AES.MODE_CBC)
        iv = cipher.iv
        encrypted = cipher.encrypt(pad(secret.encode(), AES.block_size))
        secret_encoded = base64.b64encode(iv + encrypted).decode()
        return secret_encoded, qr_base64
    except Exception as e:
        return {"message":f"Erro ao gerar o totp: {e}"}
    
def verifica_m2f(secret, otp):
    try:
        data = base64.b64decode(secret)
        iv, encrypted = data[:16], data[16:]

        cipher = AES.new(key, AES.MODE_CBC, iv)
        secret_decoded = unpad(cipher.decrypt(encrypted), AES.block_size).decode()
        
        totp = pyotp.TOTP(secret_decoded)
        valido = totp.verify(otp)
        return valido
    except Exception as e:
        return {"message":f"Erro ao verificar OTP: {e}"}
    
async def recupera_m2f(email_to: str, db:Session):
    try:
        query = select(Usuario).where(Usuario.email == email_to)
        result = db.exec(query).first()
        data = base64.b64decode(result.secret_key)
        iv, encrypted = data[:16], data[16:]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        secret_decoded = unpad(cipher.decrypt(encrypted), AES.block_size).decode()

        totp = pyotp.TOTP(secret_decoded)
        issuer_name = "Jao Financas"
        user_email = email_to
        uri = totp.provisioning_uri(user_email, issuer_name=issuer_name)
        qr = segno.make(uri)

        byte_io = io.BytesIO()
        qr.save(byte_io, kind="png")
        qr_data = byte_io.getvalue()

        qr_base64 = base64.b64encode(qr_data).decode("utf-8")

        result.qrcode = qr_base64

        body = templates.get_template('email.html').render(url=f"{APP_URL}/login", title="Recuperação do Autenticador", message="Seu qrcode foi gerado, refaça o login para recuperar o autenticador:")

        message = MessageSchema(
            subject="Recuperação do Autenticador",
            recipients=[email_to],
            body=body,
            subtype='html',
            headers={"Content-Type": "text/html; charset=UTF-8"}
        )

        fm = FastMail(email_conf)
        await fm.send_message(message)
        return {"message":"Email de Recuperação Enviado"}
    except Exception as e:
        return {"message":f"Erro ao enviar email: {e}"}