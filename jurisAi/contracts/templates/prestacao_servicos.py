from datetime import datetime

def gerar_contrato_prestacao_servicos(dados: dict) -> str:
    hoje = datetime.now().strftime("%d de %B de %Y")
    return f"""CONTRATO DE PRESTACAO DE SERVICOS ADVOCATICIOS
Numero: {dados.get('numero', '[REVISAR]')}
Data: {hoje}

CONTRATANTE: {dados.get('cliente_nome', '[NOME]')}, CPF: {dados.get('cliente_cpf', '[CPF]')}, endereco: {dados.get('cliente_endereco', '[ENDERECO]')}.
CONTRATADO: {dados.get('advogado_nome', '[NOME]')}, OAB/{dados.get('oab_estado', 'XX')} n {dados.get('oab_numero', '[OAB]')}, escritorio: {dados.get('escritorio_endereco', '[ENDERECO]')}.

1. OBJETO: {dados.get('objeto', '[DESCRICAO]')}
2. HONORARIOS: R$ {dados.get('valor_honorarios', '[VALOR]')} ({dados.get('valor_por_extenso', '[EXTENSO]')}), forma: {dados.get('forma_pagamento', '[FORMA]')}.
3. PRAZO: Vigora ate encerramento do caso, incluindo recursos {dados.get('inclui_recursos', 'ordinarios')}.
4. OBRIGACOES CONTRATADO: Diligencia, atualizacoes, sigilo profissional.
5. OBRIGACOES CONTRATANTE: Documentacao, pagamentos, comunicacao de alteracoes.
6. FORO: Comarca de {dados.get('cidade_foro', '[CIDADE]')}.

{dados.get('cidade_foro', '[CIDADE]')}, {hoje}.
Assinaturas: Contratante e Contratado.
[REVISAR: Ajustar conforme especificidades do caso]
"""
