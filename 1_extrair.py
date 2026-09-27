import pandas as pd
from banco import engine


arquivos = {
    "viagem": "2025_Viagem.csv",
    "pagamento": "2025_Pagamento.csv",
    "passagem": "2025_Passagem.csv",
    "trecho": "2025_Trecho.csv"
}


colunas = {
    "viagem": [
        "identificador_processo_viagem",
        "numero_proposta_pcdp",
        "situacao",
        "viagem_urgente",
        "justificativa_urgencia_viagem",
        "codigo_orgao_superior",
        "nome_orgao_superior",
        "codigo_orgao_solicitante",
        "nome_orgao_solicitante",
        "cpf_viajante",
        "nome",
        "cargo",
        "funcao",
        "descricao_funcao",
        "data_inicio",
        "data_fim",
        "destinos",
        "motivo",
        "valor_diarias",
        "valor_passagens",
        "valor_devolucao",
        "valor_outros_gastos"
    ],

    "pagamento": [
        "identificador_processo_viagem",
        "numero_proposta_pcdp",
        "codigo_orgao_superior",
        "nome_orgao_superior",
        "codigo_orgao_pagador",
        "nome_orgao_pagador",
        "codigo_unidade_gestora_pagadora",
        "nome_unidade_gestora_pagadora",
        "tipo_pagamento",
        "valor"
    ],

    "passagem": [
        "identificador_processo_viagem",
        "numero_proposta_pcdp",
        "meio_transporte",
        "pais_origem_ida",
        "uf_origem_ida",
        "cidade_origem_ida",
        "pais_destino_ida",
        "uf_destino_ida",
        "cidade_destino_ida",
        "pais_origem_volta",
        "uf_origem_volta",
        "cidade_origem_volta",
        "pais_destino_volta",
        "uf_destino_volta",
        "cidade_destino_volta",
        "valor_passagem",
        "taxa_servico",
        "data_emissao_compra",
        "hora_emissao_compra"
    ],

    "trecho": [
        "identificador_processo_viagem",
        "numero_proposta_pcdp",
        "sequencia_trecho",
        "origem_data",
        "origem_pais",
        "origem_uf",
        "origem_cidade",
        "destino_data",
        "destino_pais",
        "destino_uf",
        "destino_cidade",
        "meio_transporte",
        "numero_diarias",
        "missao"
    ]
}


for tabela, arquivo in arquivos.items():

    print(f"\nCarregando {arquivo}...")

    df = pd.read_csv(
        arquivo,
        sep=";",
        encoding="latin-1",
        dtype=str
    )

    # Remove espaços extras dos nomes das colunas
    df.columns = [col.strip() for col in df.columns]

    # Substitui os nomes originais pelos nomes das tabelas RAW
    df.columns = colunas[tabela]

    # Envia os dados para a camada RAW sem alterar os valores
    df.to_sql(
        tabela,
        engine,
        schema="raw",
        if_exists="append",
        index=False,
        chunksize=2000
    )

    print(f"{arquivo} carregado com sucesso!")