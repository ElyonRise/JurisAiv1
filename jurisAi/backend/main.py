from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import secrets, jwt, os, json, shutil, math
from datetime import datetime, timedelta
from passlib.context import CryptContext
from backend.db import get_db, init_db
from services.email_service import send_activation_email
from services.ai_agents import process_agent

init_db()
SECRET_KEY = os.getenv("SECRET_KEY", "fallback")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
APP_PORT = int(os.getenv("APP_PORT", "8000"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()
app = FastAPI(title="JurisAI v2.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
UPLOAD_DIR = os.path.expanduser("~/jurisai/backend/uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

class RegisterReq(BaseModel): email: str; password: str; role: str; full_name: str; specialty: Optional[str]=None; lat: Optional[float]=None; lng: Optional[float]=None
class LoginReq(BaseModel): email: str; password: str
class ActivateReq(BaseModel): token: str
class ChatReq(BaseModel): agent_type: str; message: str; history: Optional[List[dict]]=[]

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("sub") is None: raise HTTPException(401, "Invalido")
        return payload
    except: raise HTTPException(401, "Token invalido")

@app.post("/register")
async def register(req: RegisterReq):
    db = get_db()
    if req.role not in ["cliente", "advogado"]: raise HTTPException(400, "Role invalido")
    if db.execute("SELECT id FROM users WHERE email=?", (req.email,)).fetchone(): raise HTTPException(400, "Email ja cadastrado")
    token = secrets.token_urlsafe(32)
    db.execute("INSERT INTO users (email, password_hash, role, full_name, specialty, lat, lng) VALUES (?,?,?,?,?,?,?)",
               (req.email, pwd_context.hash(req.password), req.role, req.full_name, req.specialty, req.lat, req.lng))
    db.execute("INSERT INTO activation_tokens (token, email) VALUES (?,?)", (token, req.email))
    db.commit()
    await send_activation_email(req.email, token)
    return {"success": True, "message": "Conta criada. Verifique email."}

@app.post("/activate")
async def activate(req: ActivateReq):
    db = get_db()
    row = db.execute("SELECT email FROM activation_tokens WHERE token=?", (req.token,)).fetchone()
    if not row: raise HTTPException(400, "Token invalido")
    db.execute("UPDATE users SET is_active=1 WHERE email=?", (row["email"],))
    db.execute("DELETE FROM activation_tokens WHERE token=?", (req.token,))
    db.commit()
    return {"success": True, "message": "Conta ativada."}

@app.post("/login")
async def login(req: LoginReq):
    db = get_db()
    user = db.execute("SELECT id, email, password_hash, role, is_active FROM users WHERE email=?", (req.email,)).fetchone()
    if not user or not pwd_context.verify(req.password, user["password_hash"]): raise HTTPException(401, "Credenciais invalidas")
    if not user["is_active"]: raise HTTPException(403, "Conta nao ativada.")
    token = jwt.encode({"sub": str(user["id"]), "email": user["email"], "role": user["role"], "exp": datetime.utcnow() + timedelta(hours=8)}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "role": user["role"]}

@app.post("/chat/{agent_type}")
async def chat_agent(agent_type: str, req: ChatReq, user=Depends(get_current_user)):
    if agent_type == "advogado" and user.get("role") != "advogado": raise HTTPException(403, "Apenas advogados")
    return {"response": await process_agent(agent_type, req.history or [], req.message), "agent": agent_type}

@app.get("/lawyers/nearby")
async def find_lawyers(lat: float = Query(...), lng: float = Query(...), specialty: str = Query(None), user=Depends(get_current_user)):
    def dist(a_lat, a_lng, b_lat, b_lng):
        R = 6371; dlat, dlon = math.radians(b_lat-a_lat), math.radians(b_lng-a_lng)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(a_lat)) * math.cos(math.radians(b_lat)) * math.sin(dlon/2)**2
        return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1-a)))
    db = get_db()
    rows = db.execute("SELECT id, full_name, specialty, lat, lng FROM users WHERE role='advogado' AND is_active=1").fetchall()
    result = []
    for r in rows:
        if specialty and r["specialty"] != specialty: continue
        d = dist(lat, lng, r["lat"], r["lng"])
        if d <= 50: result.append({"id": r["id"], "name": r["full_name"], "specialty": r["specialty"], "dist_km": round(d,1)})
    return {"lawyers": sorted(result, key=lambda x: x["dist_km"])}

@app.post("/cases/{case_id}/files")
async def upload_file(case_id: int, file: UploadFile = File(...), user=Depends(get_current_user)):
    filepath = os.path.join(UPLOAD_DIR, f"{case_id}_{file.filename}")
    with open(filepath, "wb") as f: shutil.copyfileobj(file.file, f)
    db = get_db()
    db.execute("INSERT INTO files (case_id, filename, filepath, uploaded_by) VALUES (?,?,?,?)", (case_id, file.filename, filepath, user["email"]))
    db.commit()
    return {"success": True, "path": filepath}

@app.post("/cases")
async def create_case(client_id: Optional[int]=None, status: str="triagem", user=Depends(get_current_user)):
    db = get_db()
    c_id = client_id if user["role"] == "advogado" else user["sub"]
    cur = db.execute("INSERT INTO cases (client_id, status) VALUES (?,?)", (c_id, status))
    db.commit()
    return {"case_id": cur.lastrowid, "status": "criado"}
