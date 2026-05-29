import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, Column, Integer, String, Boolean, select
from sqlalchemy.orm import declarative_base, sessionmaker
import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY   = os.getenv("SECRET_KEY")
MAIL_FROM    = os.getenv("MAIL_FROM")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
ALGORITHM    = "HS256"

BACKEND_URL  = "https://jurisaiv1.up.railway.app"
FRONTEND_URL = "https://jurisai-rho.vercel.app"

if not DATABASE_URL:
    raise RuntimeError("Variável DATABASE_URL não definida no ambiente.")
if not SECRET_KEY:
    raise RuntimeError("Variável SECRET_KEY não definida no ambiente.")
if not MAIL_FROM:
    raise RuntimeError("Variável MAIL_FROM não definida no ambiente.")
if not MAIL_PASSWORD:
    raise RuntimeError("Variável MAIL_PASSWORD não definida no ambiente.")

engine       = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base         = declarative_base()

class User(Base):
    __tablename__ = "users"
    id              = Column(Integer, primary_key=True, index=True)
    full_name       = Column(String, nullable=False)
    email           = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role            = Column(String, nullable=False)
    oab_number      = Column(String, unique=True, index=True, nullable=True)
    oab_seccional   = Column(String, nullable=True)
    especializacao  = Column(String, nullable=True)
    experiencia     = Column(Integer, nullable=True)
    is_active       = Column(Boolean, default=False)

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://jurisai-rho.vercel.app",
        "https://jurisai-git-main-elyonrises-projects.vercel.app",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:3000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RegisterData(BaseModel):
    full_name:      str
    email:          EmailStr
    password:       str
    role:           str
    oab_number:     Optional[str] = None
    oab_seccional:  Optional[str] = None
    especializacao: Optional[str] = None
    experiencia:    Optional[int] = None

class RegisterPayload(BaseModel):
    payload:        Optional[RegisterData] = None
    full_name:      Optional[str]          = None
    email:          Optional[EmailStr]     = None
    password:       Optional[str]          = None
    role:           Optional[str]          = None
    oab_number:     Optional[str]          = None
    oab_seccional:  Optional[str]          = None
    especializacao: Optional[str]          = None
    experiencia:    Optional[int]          = None

    def resolve(self) -> RegisterData:
        if self.payload:
            return self.payload
        if self.email and self.full_name and self.password and self.role:
            return RegisterData(
                full_name=self.full_name,
                email=self.email,
                password=self.password,
                role=self.role,
                oab_number=self.oab_number,
                oab_seccional=self.oab_seccional,
                especializacao=self.especializacao,
                experiencia=self.experiencia,
            )
        raise HTTPException(status_code=422, detail="Payload inválido.")

class LoginData(BaseModel):
    email:    EmailStr
    password: str

class LoginPayload(BaseModel):
    payload:  Optional[LoginData] = None
    email:    Optional[EmailStr]  = None
    password: Optional[str]       = None

    def resolve(self) -> LoginData:
        if self.payload:
            return self.payload
        if self.email and self.password:
            return LoginData(email=self.email, password=self.password)
        raise HTTPException(status_code=422, detail="Payload de login inválido.")

class ForgotPasswordPayload(BaseModel):
    payload: Optional[dict]     = None
    email:   Optional[EmailStr] = None

    def resolve_email(self) -> str:
        if self.payload and "email" in self.payload:
            return self.payload["email"]
        if self.email:
            return self.email
        raise HTTPException(status_code=422, detail="E-mail obrigatório.")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_access_token(email: str, role: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=8)
    return jwt.encode({"sub": email, "role": role, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

def create_activation_token(email: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=24)
    return jwt.encode({"sub": email, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

def create_reset_token(email: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=1)
    return jwt.encode({"sub": email, "type": "reset", "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

def send_email(to: str, subject: str, html: str):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = MAIL_FROM
        msg["To"]      = to
        msg.attach(MIMEText(html, "html"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(MAIL_FROM, MAIL_PASSWORD)
            server.sendmail(MAIL_FROM, to, msg.as_string())
        print(f"[EMAIL OK] Enviado para {to}")
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")

def send_activation_email(email: str, token: str):
    link = f"{BACKEND_URL}/activate?token={token}"
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:500px;margin:auto">
      <h2 style="color:#1a56db">Bem-vindo ao JurisAI!</h2>
      <p>Clique no botão abaixo para ativar sua conta:</p>
      <a href="{link}" style="background:#1a56db;color:#fff;padding:12px 24px;border-radius:6px;text-decoration:none;display:inline-block;margin:16px 0">
        Ativar minha conta
      </a>
      <p style="color:#666;font-size:13px">Este link expira em 24 horas. Se você não criou uma conta, ignore este e-mail.</p>
    </div>
    """
    send_email(email, "Ative sua conta JurisAI", html)

def send_reset_email(email: str, token: str):
    link = f"{FRONTEND_URL}/reset-password?token={token}"
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:500px;margin:auto">
      <h2 style="color:#1a56db">Redefinição de senha — JurisAI</h2>
      <p>Clique no botão abaixo para redefinir sua senha:</p>
      <a href="{link}" style="background:#1a56db;color:#fff;padding:12px 24px;border-radius:6px;text-decoration:none;display:inline-block;margin:16px 0">
        Redefinir senha
      </a>
      <p style="color:#666;font-size:13px">Este link expira em 1 hora. Se você não solicitou, ignore este e-mail.</p>
    </div>
    """
    send_email(email, "Redefinição de senha JurisAI", html)

@app.get("/")
def read_root():
    return {"status": "JurisAI Backend Ativo"}

@app.post("/register", status_code=201)
def register(body: RegisterPayload, bg: BackgroundTasks, db=Depends(get_db)):
    data = body.resolve()
    if db.execute(select(User).where(User.email == data.email)).scalar_one_or_none():
        raise HTTPException(status_code=400, detail="E-mail já cadastrado.")
    if data.role == "lawyer":
        if not data.oab_number or not data.oab_seccional:
            raise HTTPException(status_code=400, detail="Dados da OAB obrigatórios para advogados.")
        if db.execute(select(User).where(User.oab_number == data.oab_number)).scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Número de OAB já cadastrado.")
    new_user = User(
        full_name=data.full_name,
        email=data.email,
        hashed_password=bcrypt.hashpw(data.password.encode(), bcrypt.gensalt()).decode(),
        role=data.role,
        oab_number=data.oab_number      if data.role == "lawyer" else None,
        oab_seccional=data.oab_seccional if data.role == "lawyer" else None,
        especializacao=data.especializacao if data.role == "lawyer" else None,
        experiencia=data.experiencia    if data.role == "lawyer" else None,
        is_active=False,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    token = create_activation_token(new_user.email)
    bg.add_task(send_activation_email, new_user.email, token)
    return {"detail": "Usuário registrado com sucesso. Verifique seu e-mail para ativar a conta."}

@app.get("/activate")
def activate_account(token: str, db=Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email   = payload.get("sub")
    except Exception:
        raise HTTPException(status_code=400, detail="Token inválido ou expirado.")
    user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    user.is_active = True
    db.commit()
    return {"detail": "Conta ativada com sucesso. Você já pode fazer login."}

@app.post("/login")
def login(body: LoginPayload, db=Depends(get_db)):
    data = body.resolve()
    user = db.execute(select(User).where(User.email == data.email)).scalar_one_or_none()
    if not user or not bcrypt.checkpw(data.password.encode(), user.hashed_password.encode()):
        raise HTTPException(status_code=401, detail="Credenciais inválidas.")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Conta não ativada. Verifique seu e-mail.")
    token = create_access_token(user.email, user.role)
    return {
        "access_token": token,
        "token_type":   "bearer",
        "role":         user.role,
        "full_name":    user.full_name,
    }

@app.post("/forgot-password")
def forgot_password(body: ForgotPasswordPayload, bg: BackgroundTasks, db=Depends(get_db)):
    email = body.resolve_email()
    user  = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if user and user.is_active:
        token = create_reset_token(email)
        bg.add_task(send_reset_email, email, token)
    return {"message": "Se o e-mail existir, você receberá as instruções em breve."}
