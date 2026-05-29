import httpx, os, json
from dotenv import load_dotenv
load_dotenv(os.path.expanduser("~/jurisai/.env"))

API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com/v1")

SYSTEM_TRIAGE = "Voce e agente de triagem juridica. Extraia: area, urgencia, resumo, docs faltantes. Responda APENAS JSON: {area, urgencia, resumo, docs_faltantes, proximo_passo}."
SYSTEM_DOCS = "Analise documentos juridicos. Liste pontos criticos, validade, assinaturas e recomendacoes. Texto estruturado."
SYSTEM_FOLLOW = "Agente de acompanhamento. Mantenha cliente informado sobre andamento e prazos. Linguagem clara. Sem promessas."
SYSTEM_LAWYER = "Assistente senior para advogados. Auxilie redacao, jurisprudencia, estrategia e riscos. Sigilo absoluto."

async def call_deepseek(messages: list, max_tokens=800) -> str:
    if not API_KEY:
        return json.dumps({"erro": "Chave de IA nao configurada"}, indent=2)
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.post(f"{BASE_URL}/chat/completions", headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}, json={"model": "deepseek-chat", "messages": messages, "max_tokens": max_tokens, "temperature": 0.2})
        return r.json()["choices"][0]["message"]["content"]

async def process_agent(agent_type: str, history: list, user_input: str) -> str:
    sys_map = {"triagem": SYSTEM_TRIAGE, "documentos": SYSTEM_DOCS, "acompanhamento": SYSTEM_FOLLOW, "advogado": SYSTEM_LAWYER}
    sys_prompt = sys_map.get(agent_type, SYSTEM_FOLLOW)
    messages = [{"role": "system", "content": sys_prompt}] + history + [{"role": "user", "content": user_input}]
    return await call_deepseek(messages)
