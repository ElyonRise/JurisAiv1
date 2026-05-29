from typing import List, Optional
from datetime import datetime
from backend.models.schemas import LeadCreate, LeadResponse


def create_lead(lead: LeadCreate) -> LeadResponse:
    """Create a new lead and return it with generated ID and timestamp."""
    from backend.services.database_service import db_service
    
    lead_data = {
        "nome": lead.nome,
        "email": lead.email,
        "telefone": lead.telefone,
        "area_interesse": lead.area_interesse,
        "descricao": lead.descricao
    }
    
    new_lead = db_service.create_lead(lead_data)
    return LeadResponse(**new_lead)


def get_leads(status: Optional[str] = None) -> List[LeadResponse]:
    """Get all leads, optionally filtered by status."""
    from backend.services.database_service import db_service
    
    leads = db_service.get_leads(status=status)
    return [LeadResponse(**lead) for lead in leads]


def get_lead_by_id(lead_id: int) -> Optional[LeadResponse]:
    """Get a single lead by ID."""
    from backend.services.database_service import db_service
    
    lead = db_service.get_lead_by_id(lead_id)
    if lead:
        return LeadResponse(**lead)
    return None


def update_lead_status(lead_id: int, status: str) -> Optional[LeadResponse]:
    """Update the status of an existing lead."""
    from backend.services.database_service import db_service
    
    updated = db_service.update_lead(lead_id, {"status": status})
    if updated:
        return LeadResponse(**updated)
    return None
