from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
import json, os
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

ENV_PATH = os.path.expanduser("~/jurisai/.env")
load_dotenv(ENV_PATH)

SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "480"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()
app = FastAPI(title="JurisAI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

USERS_DB = {
    "admin": {
        "username": "admin",
        "hashed_password": pwd_context.hash("JurisAI2024!"),
        "role": "admin",
        "full_name": "Administrador"
    }
}

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

class LoginRequest(BaseModel):
    username: str
    password: str

class Lead(BaseModel):
    nome: str
    telefone: str
    email: Optional[str] = None
    assunto: str
    urgencia: str = "normal"
    origem: str = "whatsapp"

class Processo(BaseModel):
    numero: str
    cliente: str
    tipo: str
    status: str = "ativo"
    descricao: str
    valor_causa: Optional[float] = None

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("sub") is None:
            raise HTTPException(status_code=401, detail="Token invalido")
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token expirado ou invalido")

@app.post("/auth/login", response_model=Token)
async def login(request: LoginRequest):
    user = USERS_DB.get(request.username)
    if not user or not pwd_context.verify(request.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Credenciais invalidas")
    token = create_access_token({"sub": user["username"], "role": user["role"]})
    return {"access_token": token, "token_type": "bearer", "role": user["role"]}

@app.get("/health")
async def health():
    return {"status": "online", "sistema": "JurisAI", "versao": "1.0.0", "timestamp": datetime.now().isoformat()}

@app.post("/leads", dependencies=[Depends(verify_token)])
async def criar_lead(lead: Lead):
    f_path = os.path.expanduser("~/jurisai/crm/leads/leads.json")
    leads = json.load(open(f_path)) if os.path.exists(f_path) else []
    d = lead.dict()
    d["id"] = len(leads) + 1
    d["criado_em"] = datetime.now().isoformat()
    d["status"] = "novo"
    leads.append(d)
    with open(f_path, "w") as f: json.dump(leads, f, ensure_ascii=False, indent=2)
    return {"success": True, "lead_id": d["id"], "mensagem": "Lead registrado com sucesso"}

@app.get("/leads", dependencies=[Depends(verify_token)])
async def listar_leads(status: Optional[str] = None):
    f_path = os.path.expanduser("~/jurisai/crm/leads/leads.json")
    if not os.path.exists(f_path): return {"leads": [], "total": 0}
    leads = json.load(open(f_path))
    if status: leads = [l for l in leads if l.get("status") == status]
    return {"leads": leads, "total": len(leads)}

@app.post("/processos", dependencies=[Depends(verify_token)])
async def criar_processo(processo: Processo):
    f_path = os.path.expanduser("~/jurisai/crm/cases/processos.json")
    procs = json.load(open(f_path)) if os.path.exists(f_path) else []
    d = processo.dict()
    d["id"] = len(procs) + 1
    d["criado_em"] = datetime.now().isoformat()
    procs.append(d)
    with open(f_path, "w") as f: json.dump(procs, f, ensure_ascii=False, indent=2)
    return {"success": True, "processo_id": d["id"]}

@app.get("/processos", dependencies=[Depends(verify_token)])
async def listar_processos():
    f_path = os.path.expanduser("~/jurisai/crm/cases/processos.json")
    if not os.path.exists(f_path): return {"processos": [], "total": 0}
    procs = json.load(open(f_path))
    return {"processos": procs, "total": len(procs)}

@app.get("/dashboard", dependencies=[Depends(verify_token)])
async def dashboard():
    f_l = os.path.expanduser("~/jurisai/crm/leads/leads.json")
    f_p = os.path.expanduser("~/jurisai/crm/cases/processos.json")
    leads = json.load(open(f_l)) if os.path.exists(f_l) else []
    procs = json.load(open(f_p)) if os.path.exists(f_p) else []
    total_l = len(leads)
    novos_l = len([l for l in leads if l.get("status") == "novo"])
    total_p = len(procs)
    return {
        "metricas": {"total_leads": total_l, "leads_novos": novos_l, "total_processos": total_p, "conversao_pct": round((total_p / total_l * 100) if total_l > 0 else 0, 1)},
        "sistema": "online", "timestamp": datetime.now().isoformat()
    }
