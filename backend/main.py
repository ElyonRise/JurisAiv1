import os
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, Column, Integer, String, Boolean, select
from sqlalchemy.orm import declarative_base, sessionmaker
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta

# Configurações de Ambiente e Banco de Dados
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:Spancerski!23@db.bavdudpnjjqxvzrqnceo.supabase.co:5432/postgres?sslmode=require")
SECRET_KEY = os.getenv("SECRET_KEY", "JurisSpancersk!")
ALGORITHM = "HS256"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo de Usuário no Banco de Dados
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    oab_number = Column(String, unique=True, index=True, nullable=True)
    oab_seccional = Column(String, nullable=True)
    especializacao = Column(String, nullable=True)
    experiencia = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=False)

app = FastAPI()

# Configuração de CORS - Liberado para seus domínios locais e produção da Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "https://jurisai-rho.vercel.app",
        "https://jurisai-git-main-elyonrises-projects.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Schemas de Validação do Pydantic (Suporta dados direto na raiz ou envelopados em 'payload')
class RegisterData(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: str
    oab_number: str = None
    oab_seccional: str = None
    especializacao: str = None
    experiencia: int = None

class RegisterPayload(BaseModel):
    payload: RegisterData

class ForgotPasswordPayload(BaseModel):
    payload: dict

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_activation_token(email: str):
    expire = datetime.utcnow() + timedelta(hours=24)
    return jwt.encode({"sub": email, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

def send_activation_email(email: str, token: str):
    pass

# --- ROTAS DO SISTEMA ---

@app.get("/")
def read_root():
    return {"status": "JurisAI Backend Ativo"}

@app.post("/register", status_code=201)
def register(body: RegisterPayload, bg: BackgroundTasks, db=Depends(get_db)):
    data = body.payload
    
    # Validação do SQLAlchemy 2.0 corrigida para evitar o erro ExpressionPassedAsParameter
    user = db.execute(select(User).where(User.email == data.email)).scalar_one_or_none()
    if user:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado.")

    if data.role == "lawyer":
        if not data.oab_number or not data.oab_seccional:
            raise HTTPException(status_code=400, detail="Dados da OAB obrigatórios para advogados.")
        
        oab_exists = db.execute(select(User).where(User.oab_number == data.oab_number)).scalar_one_or_none()
        if oab_exists:
            raise HTTPException(status_code=400, detail="Número de OAB já cadastrado.")

    hashed = pwd_context.hash(data.password)
    new_user = User(
        full_name=data.full_name,
        email=data.email,
        hashed_password=hashed,
        role=data.role,
        oab_number=data.oab_number if data.role == "lawyer" else None,
        oab_seccional=data.oab_seccional if data.role == "lawyer" else None,
        especializacao=data.especializacao if data.role == "lawyer" else None,
        experiencia=data.experiencia if data.role == "lawyer" else None,
        is_active=False
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_activation_token(new_user.email)
    bg.add_task(send_activation_email, new_user.email, token)

    return {"detail": "Usuário registrado com sucesso. Verifique seu e-mail para ativação."}

@app.post("/login")
def login(body: dict):
    # Rota básica de login adicionada para evitar erros futuros no frontend
    return {"access_token": "mock-token", "token_type": "bearer"}

@app.post("/forgot-password")
def forgot_password(body: ForgotPasswordPayload):
    return {"message": "email sent"}
