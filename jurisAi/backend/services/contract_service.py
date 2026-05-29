from typing import List, Optional
from backend.models.schemas import ContratoResponse


def create_contrato(titulo: str, conteudo: str, cliente_id: Optional[int] = None) -> ContratoResponse:
    """Create a new contract and return it with generated ID and timestamp."""
    from backend.services.database_service import db_service
    
    contrato_data = {
        "titulo": titulo,
        "conteudo": conteudo,
        "cliente_id": cliente_id,
        "status": "gerado"
    }
    
    new_contrato = db_service.create_contrato(contrato_data)
    return ContratoResponse(**new_contrato)


def get_contratos(cliente_id: Optional[int] = None) -> List[ContratoResponse]:
    """Get all contracts, optionally filtered by client ID."""
    from backend.services.database_service import db_service
    
    contratos = db_service.get_contratos(cliente_id=cliente_id)
    return [ContratoResponse(**contrato) for contrato in contratos]


def get_contrato_by_id(contrato_id: int) -> Optional[ContratoResponse]:
    """Get a single contract by ID."""
    from backend.services.database_service import db_service
    
    contrato = db_service.get_contrato_by_id(contrato_id)
    if contrato:
        return ContratoResponse(**contrato)
    return None


def update_contrato_status(contrato_id: int, status: str) -> Optional[ContratoResponse]:
    """Update the status of an existing contract."""
    from backend.services.database_service import db_service
    
    updated = db_service.update_contrato(contrato_id, {"status": status})
    if updated:
        return ContratoResponse(**updated)
    return None
