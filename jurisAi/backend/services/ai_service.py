"""Serviço de Inteligência Artificial - Integração com DeepSeek API."""

import os
import json
import requests
from typing import Optional


DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")

SYSTEM_PROMPT = """Você é um assistente jurídico brasileiro especializado em direito civil, trabalhista, consumerista e empresarial.
Suas respostas devem ser precisas, fundamentadas e em português do Brasil.
Sempre que possível, cite a legislação aplicável (Código Civil, CLT, CDC, etc.).
Não invente jurisprudências ou artigos de lei. Se não tiver certeza, indique isso claramente."""


def chamar_ia(
    mensagem: str,
    system_prompt: Optional[str] = None,
    model: str = "deepseek-chat",
    temperature: float = 0.3,
    max_tokens: int = 2048,
) -> str:
    """Chama a API DeepSeek com prompt jurídico e retorna a resposta.

    Se a chave DEEPSEEK_API_KEY não estiver configurada, retorna uma
    resposta simulada inteligente baseada no conteúdo da mensagem.
    """
    if not DEEPSEEK_API_KEY:
        return _resposta_simulada(mensagem)

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt or SYSTEM_PROMPT},
            {"role": "user", "content": mensagem},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except requests.exceptions.RequestException as exc:
        return f"[Erro na comunicação com a API DeepSeek] {exc}"
    except (KeyError, IndexError) as exc:
        return f"[Formato inesperado na resposta da API] {exc}"


def resumir_documento(texto: str, max_paragrafos: int = 3) -> str:
    """Resume um documento jurídico mantendo os pontos essenciais."""
    prompt = (
        f"Resuma o documento jurídico abaixo em no máximo {max_paragrafos} parágrafos, "
        f"destacando os pontos essenciais, partes envolvidas e conclusões:\n\n---\n{texto}\n---"
    )
    return chamar_ia(prompt)


def gerar_contrato(tipo: str, dados: dict) -> str:
    """Gera minuta de contrato com base no tipo e dados fornecidos."""
    dados_formatados = json.dumps(dados, indent=2, ensure_ascii=False)
    prompt = (
        f"Elabore uma minuta completa de {tipo} em português do Brasil, "
        f"utilizando os seguintes dados:\n\n{dados_formatados}\n\n"
        "Inclua cláusulas padrão aplicáveis, foro, e disposições gerais. "
        "Formate com numeração de cláusulas e parágrafos."
    )
    return chamar_ia(prompt, max_tokens=4096)


def triar_caso(descricao: str) -> str:
    """Analisa a descrição de um caso e retorna triagem com área do direito,
    complexidade estimada e próximos passos recomendados."""
    prompt = (
        "Analise o caso jurídico descrito abaixo e retorne uma triagem estruturada com:\n"
        "1. **Área do Direito** (ex: Civil, Trabalhista, Consumerista, Empresarial, etc.)\n"
        "2. **Complexidade** (Baixa, Média, Alta) com breve justificativa\n"
        "3. **Prazos importantes** a observar (prescrição, decadência, etc.)\n"
        "4. **Documentos recomendados** para instruir o caso\n"
        "5. **Próximos passos** sugeridos\n\n"
        f"Descrição do caso:\n\n{descricao}"
    )
    return chamar_ia(prompt)


# ---------------------------------------------------------------------------
# Fallback: respostas simuladas inteligentes quando a API não está configurada
# ---------------------------------------------------------------------------

def _resposta_simulada(mensagem: str) -> str:
    """Retorna uma resposta simulada contextual quando não há API key."""
    msg_lower = mensagem.lower()

    if "resum" in msg_lower:
        return (
            "[MODO SIMULAÇÃO — configure DEEPSEEK_API_KEY para respostas reais]\n\n"
            "Com base na análise do documento fornecido, identificam-se os seguintes pontos:\n"
            "1. Trata-se de matéria jurídica que requer atenção aos prazos processuais.\n"
            "2. As partes envolvidas devem ser claramente qualificadas.\n"
            "3. Recomenda-se a coleta de documentação probatória complementar.\n\n"
            "Configure a chave da API DeepSeek para obter uma análise detalhada e fundamentada."
        )

    if "contrato" in msg_lower or "minuta" in msg_lower:
        return (
            "[MODO SIMULAÇÃO — configure DEEPSEEK_API_KEY para respostas reais]\n\n"
            "CLÁUSULA PRIMEIRA — DO OBJETO\n"
            "1.1. O presente instrumento tem por objeto a prestação de serviços conforme especificado.\n\n"
            "CLÁUSULA SEGUNDA — DAS OBRIGAÇÕES\n"
            "2.1. Cada parte se obriga a cumprir as disposições aqui estabelecidas.\n\n"
            "CLÁUSULA TERCEIRA — DO FORO\n"
            "3.1. Fica eleito o foro da comarca do domicílio do contratante.\n\n"
            "Configure a chave da API DeepSeek para gerar uma minuta completa e personalizada."
        )

    if "triag" in msg_lower or "caso" in msg_lower or "anális" in msg_lower:
        return (
            "[MODO SIMULAÇÃO — configure DEEPSEEK_API_KEY para respostas reais]\n\n"
            "**Área do Direito:** A definir conforme análise detalhada\n"
            "**Complexidade:** Média — depende da documentação disponível\n"
            "**Prazos importantes:** Verificar prescrição quinquenal (art. 206, §5º, CC)\n"
            "**Documentos recomendados:** Documentos pessoais, comprovantes, contratos, correspondências\n"
            "**Próximos passos:** 1) Reunir toda documentação; 2) Elaborar relato cronológico; 3) Consultar advogado especialista\n\n"
            "Configure a chave da API DeepSeek para obter uma triagem precisa e fundamentada."
        )

    return (
        "[MODO SIMULAÇÃO — configure DEEPSEEK_API_KEY para respostas reais]\n\n"
        "Recebi sua consulta jurídica. Para fornecer uma resposta fundamentada, "
        "preciso de mais detalhes sobre o caso. Em geral, recomendo:\n"
        "1. Reunir toda documentação relevante;\n"
        "2. Organizar os fatos em ordem cronológica;\n"
        "3. Identificar os prazos aplicáveis;\n"
        "4. Buscar orientação de profissional habilitado.\n\n"
        "Configure a variável de ambiente DEEPSEEK_API_KEY para ativar a IA real."
    )
