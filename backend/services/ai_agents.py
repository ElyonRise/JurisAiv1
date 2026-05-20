import httpx, os, json
from dotenv import load_dotenv
load_dotenv(os.path.expanduser("~/jurisai/.env"))

API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com/v1")

SYSTEM_TRIAGE = "Voce e um agente de triagem juridica. Extraia: area do direito, urgencia, resumo curto, documentos faltantes. Responda APENAS em JSON: {area, urgencia, resumo, docs_faltantes, proximo_passo}."
SYSTEM_DOCS = "Voce analisa documentos juridicos enviados por clientes. Liste pontos criticos, validade, assinaturas e recomendacoes para o advogado. Responda em texto estruturado."
SYSTEM_FOLLOW = "Voce e um agente de acompanhamento. Mantenha o cliente informado sobre o andamento, prazos e proximas etapas. Use linguagem clara e acessivel. Sem prometer resultados."
SYSTEM_LAWYER = "Voce e um assistente senior para advogados. Auxilie com: redacao de pecas, pesquisa jurisprudencial, estrategia processual e analise de riscos. Mantenha sigilo absoluto e cite fontes quando possivel."

async def call_deepseek(messages: list, max_tokens=800) -> str:
    if not API_KEY:
        return json.dumps({"erro": "Chave de IA nao configurada"}, indent=2)
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.post(f"{BASE_URL}/chat/completions", headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}, json={"model": "deepseek-chat", "messages": messages, "max_tokens": max_tokens, "temperature": 0.2})
        d = r.json()
        return d["choices"][0]["message"]["content"]

async def process_agent(agent_type: str, history: list, user_input: str) -> str:
    sys_map = {"triagem": SYSTEM_TRIAGE, "documentos": SYSTEM_DOCS, "acompanhamento": SYSTEM_FOLLOW, "advogado": SYSTEM_LAWYER}
    sys_prompt = sys_map.get(agent_type, SYSTEM_FOLLOW)
    messages = [{"role": "system", "content": sys_prompt}] + history + [{"role": "user", "content": user_input}]
    resp = await call_deepseek(messages)
    if agent_type == "triagem" and resp.strip().startswith("{"):
        try: return json.loads(resp.strip())
        except: pass
    return resp
