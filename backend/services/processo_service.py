from typing import List, Optional
from datetime import datetime
from backend.models.schemas import ProcessoCreate, ProcessoResponse

# In-memory storage (will be replaced with database later)
processos_db: List[dict] = []


def create_processo(processo: ProcessoCreate) -> ProcessoResponse:
    processo_id = len(processos_db) + 1
    new_processo = {
        "id": processo_id,
        "numero_processo": processo.numero_processo,
        "cliente_nome": processo.cliente_nome,
        "area_juridica": processo.area_juridica,
        "descricao": processo.descricao,
        "status": "em_andamento",
        "data_criacao": datetime.utcnow().isoformat(),
        "ultima_atualizacao": datetime.utcnow().isoformat()
    }
    processos_db.append(new_processo)
    return ProcessoResponse(**new_processo)


def get_processos() -> List[ProcessoResponse]:
    return [ProcessoResponse(**p) for p in processos_db]


def get_processo_by_id(processo_id: int) -> Optional[ProcessoResponse]:
    for processo in processos_db:
        if processo["id"] == processo_id:
            return ProcessoResponse(**processo)
    return None


def update_processo_status(processo_id: int, status: str) -> Optional[ProcessoResponse]:
    for processo in processos_db:
        if processo["id"] == processo_id:
            processo["status"] = status
            processo["ultima_atualizacao"] = datetime.utcnow().isoformat()
            return ProcessoResponse(**processo)
    return None
