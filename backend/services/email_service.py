import httpx, os
from dotenv import load_dotenv
load_dotenv(os.path.expanduser("~/jurisai/.env"))

BREVO_KEY = os.getenv("BREVO_API_KEY", "")
SENDER_EMAIL = os.getenv("BREVO_SENDER_EMAIL", "noreply@jurisai.com")
SENDER_NAME = os.getenv("BREVO_SENDER_NAME", "JurisAI")

async def send_activation_email(email: str, token: str):
    if not BREVO_KEY:
        print(f"[DEV] Email de ativacao simulado para {email}: {token}")
        return True
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {"accept": "application/json", "api-key": BREVO_KEY, "content-type": "application/json"}
    link = f"http://localhost:{os.getenv('FRONTEND_PORT', '8080')}/ativar?token={token}"
    payload = {
        "sender": {"name": SENDER_NAME, "email": SENDER_EMAIL},
        "to": [{"email": email}],
        "subject": "Ative sua conta JurisAI",
        "htmlContent": f"<p>Olá,</p><p>Clique para ativar: <a href='{link}'>Ativar Conta</a></p><p>Válido por 24h.</p>"
    }
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(url, headers=headers, json=payload)
        return resp.status_code in [200, 201, 202]
