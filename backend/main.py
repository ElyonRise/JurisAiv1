import os, secrets
from datetime import datetime, timedelta
from typing import Optional, List
 
import resend
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy import (
    create_engine, Column, String, Boolean,
    Float, DateTime, Integer, Text, ForeignKey
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
 
load_dotenv()
 
# ── Configurações
DATABASE_URL     = os.getenv("DATABASE_URL", "sqlite:///./data/jurisai.db")
SECRET_KEY       = os.getenv("SECRET_KEY", "dev-secret-MUDE-EM-PRODUCAO")
ALGORITHM        = os.getenv("ALGORITHM", "HS256")
ACCESS_EXPIRE    = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
RESEND_API_KEY   = os.getenv("RESEND_API_KEY", "")
MAIL_FROM        = os.getenv("MAIL_FROM", "onboarding@resend.dev")
BASE_URL         = os.getenv("BASE_URL", "http://localhost:8000")
FRONTEND_URL     = os.getenv("FRONTEND_URL", "http://localhost:3000")
ADMIN_SECRET_KEY = os.getenv("ADMIN_SECRET_KEY", "admin-secret-MUDE")
 
resend.api_key = RESEND_API_KEY
 
# ── Banco de Dados
os.makedirs("data", exist_ok=True)
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
engine       = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base         = declarative_base()
 
 
class UserDB(Base):
    __tablename__ = "users"
    id               = Column(Integer, primary_key=True, autoincrement=True)
    email            = Column(String, unique=True, index=True, nullable=False)
    full_name        = Column(String, nullable=False)
    hashed_password  = Column(String, nullable=False)
    role             = Column(String, default="client")   # client | lawyer | admin
    specialty        = Column(String, nullable=True)
    oab              = Column(String, nullable=True)
    lat              = Column(Float, default=0.0)
    lng              = Column(Float, default=0.0)
    is_active        = Column(Boolean, default=False)
    is_blocked       = Column(Boolean, default=False)
    plan             = Column(String, default="free")     # free|basic|pro|unlimited
    activation_token = Column(String, nullable=True)
    reset_token      = Column(String, nullable=True)
    created_at       = Column(DateTime, default=datetime.utcnow)
    last_login       = Column(DateTime, nullable=True)
    cases            = relationship("CaseDB", back_populates="owner", cascade="all, delete-orphan")
 
 
class CaseDB(Base):
    __tablename__ = "cases"
    id          = Column(Integer, primary_key=True, autoincrement=True)
    owner_email = Column(String, ForeignKey("users.email"))
    title       = Column(String, nullable=False)
    description = Column(Text)
    status      = Column(String, default="open")
    urgency     = Column(String, default="medium")
    created_at  = Column(DateTime, default=datetime.utcnow)
    owner       = relationship("UserDB", back_populates="cases")
 
 
Base.metadata.create_all(bind=engine)
 
# ── Segurança
pwd_ctx       = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
 
def hash_password(pwd): return pwd_ctx.hash(pwd)
def verify_password(plain, hashed): return pwd_ctx.verify(plain, hashed)
 
def create_access_token(data, expires=None):
    p = data.copy()
    p["exp"] = datetime.utcnow() + (expires or timedelta(minutes=ACCESS_EXPIRE))
    return jwt.encode(p, SECRET_KEY, algorithm=ALGORITHM)
 
def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()
 
def get_current_user(token=Depends(oauth2_scheme), db=Depends(get_db)):
    exc = HTTPException(401, "Token inválido ou expirado.", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email: raise exc
    except JWTError: raise exc
    user = db.query(UserDB).filter(UserDB.email == email).first()
    if not user: raise exc
    if user.is_blocked: raise HTTPException(403, "Conta bloqueada. Entre em contato com o suporte.")
    return user
 
def require_admin(current_user=Depends(get_current_user)):
    if current_user.role != "admin": raise HTTPException(403, "Acesso restrito a administradores.")
    return current_user
 
# ── E-mails
def _html(title, body):
    return f"""<html><body style="margin:0;padding:0;background:#06080c;font-family:'Segoe UI',Arial,sans-serif;">
    <table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center" style="padding:40px 20px;">
    <table width="580" style="background:#0d1117;border-radius:16px;border:1px solid rgba(201,168,76,0.25);overflow:hidden;">
    <tr><td style="background:linear-gradient(135deg,#0b0f17,#0d1117);padding:32px 40px;text-align:center;border-bottom:1px solid rgba(201,168,76,0.15);">
    <span style="font-size:28px;font-weight:700;color:#c9a84c;letter-spacing:2px;">⚖️ JurisAI</span>
    <p style="color:#8b949e;margin:6px 0 0;font-size:13px;">Escritório de Advocacia Inteligente</p>
    </td></tr><tr><td style="padding:40px;">
    <h2 style="color:#e6edf3;margin:0 0 20px;font-size:22px;">{title}</h2>
    {body}
    <hr style="border:none;border-top:1px solid rgba(255,255,255,0.07);margin:32px 0;">
    <p style="color:#8b949e;font-size:11px;margin:0;">JurisAI &mdash; Sistema Jurídico Inteligente</p>
    </td></tr></table></td></tr></table></body></html>"""
 
def send_activation_email(to_email, full_name, token):
    url = f"{BASE_URL}/activate?token={token}"
    body = f"""<p style="color:#8b949e;line-height:1.8;margin:0 0 28px;">
    Olá, <strong style="color:#e6edf3;">{full_name}</strong>!<br>
    Sua conta no JurisAI foi criada. Clique abaixo para ativar:</p>
    <div style="text-align:center;margin-bottom:28px;">
    <a href="{url}" style="background:#c9a84c;color:#000;padding:15px 38px;border-radius:10px;font-weight:700;font-size:15px;text-decoration:none;display:inline-block;">✅ Ativar Minha Conta</a>
    </div><p style="color:#8b949e;font-size:12px;">Link válido por 24 horas. Se não foi você, ignore.</p>"""
    try:
        resend.Emails.send({"from": MAIL_FROM, "to": [to_email], "subject": "⚖️ JurisAI — Ative sua conta", "html": _html("Bem-vindo ao JurisAI!", body)})
    except Exception as e:
        print(f"[MAIL ERROR] {to_email}: {e}")
 
def send_reset_email(to_email, full_name, token):
    url = f"{FRONTEND_URL}/reset-password.html?token={token}"
    body = f"""<p style="color:#8b949e;line-height:1.8;margin:0 0 28px;">
    Olá, <strong style="color:#e6edf3;">{full_name}</strong>!<br>
    Recebemos um pedido de redefinição de senha.</p>
    <div style="text-align:center;margin-bottom:28px;">
    <a href="{url}" style="background:#ef4444;color:#fff;padding:15px 38px;border-radius:10px;font-weight:700;font-size:15px;text-decoration:none;display:inline-block;">🔑 Redefinir Senha</a>
    </div><p style="color:#8b949e;font-size:12px;">Link válido por 1 hora. Se não foi você, ignore.</p>"""
    try:
        resend.Emails.send({"from": MAIL_FROM, "to": [to_email], "subject": "⚖️ JurisAI — Redefinição de senha", "html": _html("Redefinição de Senha", body)})
    except Exception as e:
        print(f"[MAIL ERROR RESET] {to_email}: {e}")
 
# ── Schemas
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str
    specialty: Optional[str] = None
    oab: Optional[str] = None
    lat: Optional[float] = 0.0
    lng: Optional[float] = 0.0
 
class LoginRequest(BaseModel):
    username: str
    password: str
 
class ForgotPasswordRequest(BaseModel):
    email: EmailStr
 
class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
 
class UserOut(BaseModel):
    id: int; email: str; full_name: str; role: str
    is_active: bool; is_blocked: bool; plan: str
    created_at: datetime; last_login: Optional[datetime] = None
    class Config: from_attributes = True
 
class CaseOut(BaseModel):
    id: int; owner_email: str; title: str
    description: Optional[str]; status: str; urgency: str; created_at: datetime
    class Config: from_attributes = True
 
class CaseCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    urgency: Optional[str] = "medium"
 
# ── App
app = FastAPI(title="JurisAI API", description="Backend SaaS multi-usuário 100% gratuito", version="2.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
 
# ── Rotas Públicas
@app.get("/", tags=["status"])
def root(): return {"message": "JurisAI API v2.1 — Online ✅", "docs": "/docs"}
 
@app.get("/health", tags=["status"])
def health(): return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
 
@app.post("/register", status_code=201, tags=["auth"])
def register(data: RegisterRequest, bg: BackgroundTasks, db=Depends(get_db)):
    if data.role not in ("client", "lawyer"):
        raise HTTPException(400, "Role inválido. Use 'client' ou 'lawyer'.")
    if len(data.password) < 6:
        raise HTTPException(400, "A senha precisa ter pelo menos 6 caracteres.")
    if db.query(UserDB).filter(UserDB.email == data.email).first():
        raise HTTPException(400, "Este e-mail já está cadastrado.")
    token = secrets.token_urlsafe(32)
    user = UserDB(email=data.email, full_name=data.full_name,
                  hashed_password=hash_password(data.password), role=data.role,
                  specialty=data.specialty, oab=data.oab,
                  lat=data.lat or 0.0, lng=data.lng or 0.0, activation_token=token)
    db.add(user); db.commit(); db.refresh(user)
    bg.add_task(send_activation_email, data.email, data.full_name, token)
    return {"message": "Conta criada! Verifique seu e-mail para ativar o acesso.", "email": data.email}
 
@app.get("/activate", tags=["auth"])
def activate(token: str, db=Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.activation_token == token).first()
    if not user: raise HTTPException(400, "Token inválido ou já utilizado.")
    user.is_active = True; user.activation_token = None; db.commit()
    return RedirectResponse(url=f"{FRONTEND_URL}/index.html?activated=true")
 
@app.post("/login", tags=["auth"])
def login(data: LoginRequest, db=Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.email == data.username).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(401, "E-mail ou senha incorretos.")
    if not user.is_active:
        raise HTTPException(403, "Conta não ativada. Verifique seu e-mail.")
    if user.is_blocked:
        raise HTTPException(403, "Conta bloqueada. Entre em contato com o suporte.")
    user.last_login = datetime.utcnow(); db.commit()
    token = create_access_token({"sub": user.email, "role": user.role})
    return {"access_token": token, "token_type": "bearer", "role": user.role,
            "full_name": user.full_name, "email": user.email, "plan": user.plan}
 
@app.post("/forgot-password", tags=["auth"])
def forgot_password(data: ForgotPasswordRequest, bg: BackgroundTasks, db=Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.email == data.email).first()
    if user and user.is_active:
        t = secrets.token_urlsafe(32); user.reset_token = t; db.commit()
        bg.add_task(send_reset_email, user.email, user.full_name, t)
    return {"message": "Se o e-mail existir, você receberá as instruções em breve."}
 
@app.post("/reset-password", tags=["auth"])
def reset_password(data: ResetPasswordRequest, db=Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.reset_token == data.token).first()
    if not user: raise HTTPException(400, "Token inválido ou expirado.")
    if len(data.new_password) < 6: raise HTTPException(400, "Senha muito curta.")
    user.hashed_password = hash_password(data.new_password); user.reset_token = None; db.commit()
    return {"message": "Senha redefinida com sucesso!"}
 
# ── Rotas Autenticadas
@app.get("/me", response_model=UserOut, tags=["usuario"])
def get_me(cu=Depends(get_current_user)): return cu
 
@app.get("/cases", response_model=List[CaseOut], tags=["casos"])
def list_cases(cu=Depends(get_current_user), db=Depends(get_db)):
    if cu.role in ("lawyer", "admin"): return db.query(CaseDB).all()
    return db.query(CaseDB).filter(CaseDB.owner_email == cu.email).all()
 
@app.post("/cases", response_model=CaseOut, status_code=201, tags=["casos"])
def create_case(data: CaseCreate, cu=Depends(get_current_user), db=Depends(get_db)):
    case = CaseDB(owner_email=cu.email, title=data.title, description=data.description, urgency=data.urgency)
    db.add(case); db.commit(); db.refresh(case); return case
 
@app.put("/cases/{case_id}/status", tags=["casos"])
def update_status(case_id: int, new_status: str, cu=Depends(get_current_user), db=Depends(get_db)):
    valid = ("open", "in_progress", "closed")
    if new_status not in valid: raise HTTPException(400, f"Status inválido. Use: {valid}")
    case = db.query(CaseDB).filter(CaseDB.id == case_id).first()
    if not case: raise HTTPException(404, "Caso não encontrado.")
    if cu.role not in ("lawyer","admin") and case.owner_email != cu.email:
        raise HTTPException(403, "Sem permissão.")
    case.status = new_status; db.commit()
    return {"message": f"Status atualizado para '{new_status}'."}
 
# ── Rotas Admin
@app.post("/admin/create-admin", tags=["admin"])
def create_admin(data: RegisterRequest, secret: str, db=Depends(get_db)):
    if secret != ADMIN_SECRET_KEY: raise HTTPException(403, "Chave secreta inválida.")
    if db.query(UserDB).filter(UserDB.email == data.email).first():
        raise HTTPException(400, "E-mail já cadastrado.")
    user = UserDB(email=data.email, full_name=data.full_name,
                  hashed_password=hash_password(data.password),
                  role="admin", is_active=True, plan="unlimited")
    db.add(user); db.commit()
    return {"message": f"Admin '{data.email}' criado!"}
 
@app.get("/admin/stats", tags=["admin"])
def admin_stats(admin=Depends(require_admin), db=Depends(get_db)):
    return {
        "total_users":   db.query(UserDB).count(),
        "active_users":  db.query(UserDB).filter(UserDB.is_active==True).count(),
        "pending_users": db.query(UserDB).filter(UserDB.is_active==False).count(),
        "lawyers":       db.query(UserDB).filter(UserDB.role=="lawyer").count(),
        "clients":       db.query(UserDB).filter(UserDB.role=="client").count(),
        "blocked":       db.query(UserDB).filter(UserDB.is_blocked==True).count(),
        "total_cases":   db.query(CaseDB).count(),
        "open_cases":    db.query(CaseDB).filter(CaseDB.status=="open").count(),
        "closed_cases":  db.query(CaseDB).filter(CaseDB.status=="closed").count(),
    }
 
@app.get("/admin/users", response_model=List[UserOut], tags=["admin"])
def admin_list_users(admin=Depends(require_admin), db=Depends(get_db)):
    return db.query(UserDB).order_by(UserDB.created_at.desc()).all()
 
@app.post("/admin/block/{user_email}", tags=["admin"])
def admin_block(user_email: str, admin=Depends(require_admin), db=Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.email==user_email).first()
    if not user: raise HTTPException(404, "Usuário não encontrado.")
    user.is_blocked = True; db.commit()
    return {"message": f"{user_email} bloqueado."}
 
@app.post("/admin/unblock/{user_email}", tags=["admin"])
def admin_unblock(user_email: str, admin=Depends(require_admin), db=Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.email==user_email).first()
    if not user: raise HTTPException(404, "Usuário não encontrado.")
    user.is_blocked = False; db.commit()
    return {"message": f"{user_email} desbloqueado."}
 
@app.post("/admin/set-plan/{user_email}", tags=["admin"])
def admin_set_plan(user_email: str, plan: str, admin=Depends(require_admin), db=Depends(get_db)):
    if plan not in ("free","basic","pro","unlimited"):
        raise HTTPException(400, "Plano inválido.")
    user = db.query(UserDB).filter(UserDB.email==user_email).first()
    if not user: raise HTTPException(404, "Usuário não encontrado.")
    user.plan = plan; db.commit()
    return {"message": f"Plano de {user_email} → '{plan}'."}
 
@app.delete("/admin/delete/{user_email}", tags=["admin"])
def admin_delete(user_email: str, admin=Depends(require_admin), db=Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.email==user_email).first()
    if not user: raise HTTPException(404, "Usuário não encontrado.")
    db.delete(user); db.commit()
    return {"message": f"{user_email} removido."}
