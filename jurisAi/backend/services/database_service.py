import os
from typing import List, Dict, Any, Optional


class DatabaseService:
    """In-memory database service (will be replaced with real database later)."""

    def __init__(self):
        self.leads_db: List[Dict[str, Any]] = []
        self.processos_db: List[Dict[str, Any]] = []
        self.users_db: List[Dict[str, Any]] = []
        self.contracts_db: List[Dict[str, Any]] = []

        self._init_admin()

    def _init_admin(self):
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
        self.users_db.append({
            "id": 1,
            "username": os.getenv("ADMIN_USERNAME", "admin"),
            "email": os.getenv("ADMIN_EMAIL", "admin@jurisai.com"),
            "hashed_password": pwd_context.hash(admin_password),
            "role": "admin",
            "active": True
        })

    # Lead operations
    def create_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        lead_id = len(self.leads_db) + 1
        new_lead = {
            "id": lead_id,
            **lead_data,
            "status": "novo",
            "criado_em": self._get_timestamp()
        }
        self.leads_db.append(new_lead)
        return new_lead

    def get_leads(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        if status:
            return [lead for lead in self.leads_db if lead.get("status") == status]
        return self.leads_db

    def get_lead_by_id(self, lead_id: int) -> Optional[Dict[str, Any]]:
        for lead in self.leads_db:
            if lead["id"] == lead_id:
                return lead
        return None

    def update_lead(self, lead_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        for lead in self.leads_db:
            if lead["id"] == lead_id:
                lead.update(updates)
                lead["updated_at"] = self._get_timestamp()
                return lead
        return None

    # Processo operations
    def create_processo(self, processo_data: Dict[str, Any]) -> Dict[str, Any]:
        processo_id = len(self.processos_db) + 1
        new_processo = {
            "id": processo_id,
            **processo_data,
            "status": "em_andamento",
            "criado_em": self._get_timestamp()
        }
        self.processos_db.append(new_processo)
        return new_processo

    def get_processos(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        if status:
            return [p for p in self.processos_db if p.get("status") == status]
        return self.processos_db

    def get_processo_by_id(self, processo_id: int) -> Optional[Dict[str, Any]]:
        for processo in self.processos_db:
            if processo["id"] == processo_id:
                return processo
        return None

    def update_processo(self, processo_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        for processo in self.processos_db:
            if processo["id"] == processo_id:
                processo.update(updates)
                processo["updated_at"] = self._get_timestamp()
                return processo
        return None

    # User operations
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        for user in self.users_db:
            if user["username"] == username:
                return user
        return None

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        for user in self.users_db:
            if user["email"] == email:
                return user
        return None

    # Contract operations
    def create_contrato(self, contract_data: Dict[str, Any]) -> Dict[str, Any]:
        contract_id = len(self.contracts_db) + 1
        new_contract = {
            "id": contract_id,
            **contract_data,
            "status": "gerado",
            "criado_em": self._get_timestamp()
        }
        self.contracts_db.append(new_contract)
        return new_contract

    def get_contratos(self, cliente_id: Optional[int] = None) -> List[Dict[str, Any]]:
        if cliente_id is not None:
            return [c for c in self.contracts_db if c.get("cliente_id") == cliente_id]
        return self.contracts_db

    def get_contrato_by_id(self, contract_id: int) -> Optional[Dict[str, Any]]:
        for contract in self.contracts_db:
            if contract["id"] == contract_id:
                return contract
        return None

    def update_contrato(self, contract_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        for contract in self.contracts_db:
            if contract["id"] == contract_id:
                contract.update(updates)
                contract["updated_at"] = self._get_timestamp()
                return contract
        return None

    @staticmethod
    def _get_timestamp() -> str:
        from datetime import datetime
        return datetime.utcnow().isoformat()


# Singleton instance
db_service = DatabaseService()
