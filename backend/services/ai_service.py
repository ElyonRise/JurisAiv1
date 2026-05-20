import os, httpx, json, re
from dotenv import load_dotenv
from datetime import datetime

load_dotenv(os.path.expanduser("~/jurisai/.env"))
DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY", "")
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com/v1")

SYSTEM_JURIDICO = "Voce e JurisAI, assistente juridico especializado em direito brasileiro. Responda sempre em portugues, de forma objetiva e profissional. Indique que a orientacao definitiva e do advogado responsavel."

async def chamar_ia(mensagem: str, contexto: str = "", max_tokens: int = 800) -> str:
    if not DEEPSEEK_KEY or DEEPSEEK_KEY.startswith("sk-sk-"):
        return simular_resposta(mensagem)
    messages = []
    if contexto:
        messages.extend([{"role": "user", "content": contexto}, {"role": "assistant", "content": "Entendido."}])
    messages.append({"role": "user", "content": mensagem})
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.post(f"{BASE_URL}/chat/completions", headers={"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"}, json={"model": "deepseek-chat", "messages": [{"role": "system", "content": SYSTEM_JURIDICO}] + messages, "max_tokens": max_tokens, "temperature": 0.3})
        return r.json()["choices"][0]["message"]["content"]

def simular_resposta(msg: str) -> str:
    m = msg.lower()
    if any(w in m for w in ["contrato", "minuta"]): return "Para elaborar, preciso de: nomes completos, CPF/CNPJ, objeto e condicoes."
    if any(w in m for w in ["prazo", "urgente", "processo"]): return "Assunto recebido com prioridade. Advogado entrara em contato em ate 2h. Urgencias: ligue (00) 0000-0000."
    if any(w in m for w in ["preco", "honorario"]): return "Honorarios variam conforme complexidade. Consulta inicial gratuita de 30 min. Deseja agendar?"
    return "Assistente juridico do escritorio. Um advogado analisara seu caso. Qual o assunto principal?"

async def resumir_documento(texto: str) -> dict:
    prompt = f"Resuma este documento juridico apontando: TIPO, PARTES, OBJETO, PONTOS CRITICOS e RECOMENDACAO. DOCUMENTO:\n{texto[:3000]}"
    return {"resumo": await chamar_ia(prompt, max_tokens=600), "processado_em": datetime.now().isoformat()}

async def gerar_contrato(tipo: str, dados: dict) -> str:
    return await chamar_ia(f"Gere minuta de {tipo} com: {json.dumps(dados)}. Inclua qualificacao, clausulas, prazo, valor, foro e marque [REVISAR] onde necessario.", max_tokens=1200)

async def triar_caso(descricao: str) -> dict:
    prompt = f"Triagem do caso: \"{descricao}\". Retorne JSON com: area_direito, urgencia, resumo_caso, proximo_passo, documentos_necessarios."
    try:
        resp = await chamar_ia(prompt, max_tokens=400)
        match = re.search(r'\{.*\}', resp, re.DOTALL)
        if match: return json.loads(match.group())
    except: pass
    return {"area_direito": "a classificar", "urgencia": "media", "resumo_caso": descricao[:100], "proximo_passo": "Consulta necessaria", "documentos_necessarios": ["Documentos pessoais", "Provas do caso"]}
