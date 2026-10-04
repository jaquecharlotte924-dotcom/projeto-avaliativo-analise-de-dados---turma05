
import pandas as pd
from sqlalchemy import text
from banco import engine


arquivos = {
    "raw_viagem": {
        "arquivo": "2025_Viagem.csv",
        "colunas": [
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
        ]
    },

    "raw_pagamento": {
        "arquivo": "2025_Pagamento.csv",
        "colunas": [
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
        ]
    },

    "raw_passagem": {
        "arquivo": "2025_Passagem.csv",
        "colunas": [
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
        ]
    },

    "raw_trecho": {
        "arquivo": "2025_Trecho.csv",
        "colunas": [
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
}


def carregar_arquivo(tabela, arquivo, colunas):
    print(f"\nCarregando {arquivo}...", flush=True)

    try:
        # Lê o CSV em blocos, preservando os valores
        blocos = pd.read_csv(
            arquivo,
            sep=";",
            encoding="latin-1",
            dtype=str,
            chunksize=20000,
            keep_default_na=False,
            na_filter=False
        )

        total = 0

        # Substitui os dados anteriores em uma transação.
        # Se ocorrer um erro, a transação é desfeita.
        with engine.begin() as conn:
            conn.execute(
                text(f'TRUNCATE TABLE "{tabela}"')
            )

            for df in blocos:
                # Confere a quantidade de colunas do CSV
                if len(df.columns) != len(colunas):
                    raise ValueError(
                        f"O arquivo {arquivo} possui "
                        f"{len(df.columns)} colunas, mas "
                        f"eram esperadas {len(colunas)}."
                    )

                # Padroniza os nomes, sem alterar os valores
                df.columns = [
                    coluna.strip() for coluna in df.columns
                ]
                df.columns = colunas

                # Carrega cada bloco na RAW
                df.to_sql(
                    tabela,
                    conn,
                    if_exists="append",
                    index=False,
                    chunksize=2000
                )

                total += len(df)

        print(
            f"{tabela}: {total} registros carregados.",
            flush=True
        )

    except FileNotFoundError:
        print(f"Arquivo não encontrado: {arquivo}")
        raise

    except Exception as erro:
        print(f"Erro ao carregar {arquivo}: {erro}")
        raise


# Carrega os quatro arquivos
for tabela, dados in arquivos.items():
    carregar_arquivo(
        tabela,
        dados["arquivo"],
        dados["colunas"]
    )

print("\nExtração da camada RAW concluída!", flush=True)
