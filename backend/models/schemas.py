from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class Token(BaseModel):
    access_token: str
    token_type: str


class LeadCreate(BaseModel):
    nome: str
    email: EmailStr
    telefone: str
    area_interesse: str
    descricao: Optional[str] = None


class LeadResponse(BaseModel):
    id: int
    nome: str
    email: str
    telefone: str
    area_interesse: str
    descricao: Optional[str] = None
    status: str
    criado_em: str


class ProcessoCreate(BaseModel):
    numero_processo: str
    cliente_nome: str
    area_juridica: str
    descricao: str


class ProcessoResponse(BaseModel):
    id: int
    numero_processo: str
    cliente_nome: str
    area_juridica: str
    descricao: str
    status: str
    data_criacao: str
    ultima_atualizacao: str


class ContratoCreate(BaseModel):
    titulo: str
    conteudo: str
    cliente_id: Optional[int] = None


class ContratoResponse(BaseModel):
    id: int
    titulo: str
    conteudo: str
    cliente_id: Optional[int] = None
    status: str
    criado_em: str


class DashboardStats(BaseModel):
    total_leads: int
    total_processos: int
    processos_ativos: int
    processos_concluidos: int
    leads_recentes_7d: int


class MessageResponse(BaseModel):
    message: str
