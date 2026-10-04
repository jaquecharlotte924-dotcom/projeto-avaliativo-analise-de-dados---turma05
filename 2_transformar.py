import pandas as pd
from sqlalchemy import text
from banco import engine

LOTE = 5000


def limpar(s, limite=None):
    s = s.astype("string").str.strip()
    s = s.mask(s.str.lower().isin(["", "nan", "none", "null"]))
    if limite:
        s = s.str.slice(0, limite)
    return s.astype(object).where(s.notna(), None)


def numero(s):
    s = limpar(s).astype("string")
    s = s.str.replace("R$", "", regex=False).str.replace(" ", "", regex=False)
    virgula = s.str.contains(",", na=False)
    s.loc[virgula] = (
        s.loc[virgula].str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )
    n = pd.to_numeric(s, errors="coerce")
    return n.astype(object).where(n.notna(), None)


def data(s):
    d = pd.to_datetime(s, dayfirst=True, errors="coerce")
    return pd.Series(d.dt.date, index=s.index, dtype=object).where(d.notna(), None)


def inserir(tabela, df, conn):
    if not df.empty:
        df.to_sql(
            tabela, conn, schema="public",
            if_exists="append", index=False, chunksize=1000
        )


def viagens(conn):
    ids = set()
    total = 0

    for r in pd.read_sql_query(
        "SELECT * FROM public.raw_viagem", conn, chunksize=LOTE
    ):
        inicio = pd.to_datetime(r["data_inicio"], dayfirst=True, errors="coerce")
        fim = pd.to_datetime(r["data_fim"], dayfirst=True, errors="coerce")
        dias = (fim - inicio).dt.days + 1

        df = pd.DataFrame({
            "id_viagem": limpar(r["identificador_processo_viagem"], 20),
            "num_proposta": limpar(r["numero_proposta_pcdp"], 20),
            "situacao": limpar(r["situacao"], 50),
            "viagem_urgente": limpar(r["viagem_urgente"], 5),
            "cod_orgao_super": limpar(r["codigo_orgao_superior"], 20),
            "nome_orgao_superior": limpar(r["nome_orgao_superior"], 255),
            "nome_viajante": limpar(r["nome"], 255),
            "cargo": limpar(r["cargo"], 255),
            "data_inicio": data(r["data_inicio"]),
            "data_fim": data(r["data_fim"]),
            "destinos": limpar(r["destinos"], 4000),
            "motivo": limpar(r["motivo"], 4000),
            "valor_diarias": numero(r["valor_diarias"]),
            "valor_passagens": numero(r["valor_passagens"]),
            "valor_devolucao": numero(r["valor_devolucao"]),
            "valor_outros_gastos": numero(r["valor_outros_gastos"]),
            "duracao_dias": [
                int(v) if pd.notna(v) and v > 0 else None
                for v in dias
            ]
        })

        df["nome_orgao_superior"] = df["nome_orgao_superior"].fillna(
            "Sem informação"
        )
        df = df.dropna(subset=["id_viagem"])
        df = df.drop_duplicates(subset=["id_viagem"])
        df = df[~df["id_viagem"].isin(ids)].copy()

        diarias = pd.to_numeric(df["valor_diarias"], errors="coerce")
        df = df[diarias.isna() | (diarias >= 0)].copy()

        df["valor_total"] = (
            pd.to_numeric(df["valor_diarias"], errors="coerce").fillna(0)
            + pd.to_numeric(df["valor_passagens"], errors="coerce").fillna(0)
            + pd.to_numeric(df["valor_outros_gastos"], errors="coerce").fillna(0)
            - pd.to_numeric(df["valor_devolucao"], errors="coerce").fillna(0)
        ).round(2)

        ids.update(df["id_viagem"])
        inserir("silver_viagem", df, conn)
        total += len(df)

    print(f"Viagens: {total}")
    return ids


def dependente(conn, tabela_raw, tabela_silver, transformar, ids):
    total = 0
    chaves_trecho = set()

    for r in pd.read_sql_query(
        f"SELECT * FROM public.{tabela_raw}", conn, chunksize=LOTE
    ):
        df = transformar(r)
        df = df[df["id_viagem"].isin(ids)].copy()

        if tabela_silver == "silver_trecho":
            manter = []
            for idv, seq in zip(df["id_viagem"], df["sequencia_trecho"]):
                chave = (idv, seq)
                ok = pd.isna(seq) or chave not in chaves_trecho
                manter.append(ok)
                if pd.notna(seq):
                    chaves_trecho.add(chave)
            df = df.loc[manter].copy()

        inserir(tabela_silver, df, conn)
        total += len(df)

    print(f"{tabela_silver}: {total}")


def pagamentos(r):
    df = pd.DataFrame({
        "id_viagem": limpar(r["identificador_processo_viagem"], 20),
        "num_proposta": limpar(r["numero_proposta_pcdp"], 20),
        "nome_orgao_pagador": limpar(r["nome_orgao_pagador"], 255),
        "nome_ug_pagadora": limpar(r["nome_unidade_gestora_pagadora"], 255),
        "tipo_pagamento": limpar(r["tipo_pagamento"], 50),
        "valor": numero(r["valor"])
    })
    df = df[df["tipo_pagamento"].notna()].copy()
    v = pd.to_numeric(df["valor"], errors="coerce")
    return df[v.isna() | (v >= 0)].copy()


def passagens(r):
    df = pd.DataFrame({
        "id_viagem": limpar(r["identificador_processo_viagem"], 20),
        "meio_transporte": limpar(r["meio_transporte"], 50),
        "pais_origem_ida": limpar(r["pais_origem_ida"], 60),
        "uf_origem_ida": limpar(r["uf_origem_ida"], 40),
        "cidade_origem_ida": limpar(r["cidade_origem_ida"], 80),
        "pais_destino_ida": limpar(r["pais_destino_ida"], 60),
        "uf_destino_ida": limpar(r["uf_destino_ida"], 40),
        "cidade_destino_ida": limpar(r["cidade_destino_ida"], 80),
        "valor_passagem": numero(r["valor_passagem"]),
        "taxa_servico": numero(r["taxa_servico"]),
        "data_emissao": data(r["data_emissao_compra"])
    })
    v = pd.to_numeric(df["valor_passagem"], errors="coerce")
    t = pd.to_numeric(df["taxa_servico"], errors="coerce")
    return df[(v.isna() | (v >= 0)) & (t.isna() | (t >= 0))].copy()


def trechos(r):
    df = pd.DataFrame({
        "id_viagem": limpar(r["identificador_processo_viagem"], 20),
        "sequencia_trecho": pd.to_numeric(
            r["sequencia_trecho"], errors="coerce"
        ),
        "origem_data": data(r["origem_data"]),
        "origem_uf": limpar(r["origem_uf"], 40),
        "origem_cidade": limpar(r["origem_cidade"], 80),
        "destino_data": data(r["destino_data"]),
        "destino_uf": limpar(r["destino_uf"], 40),
        "destino_cidade": limpar(r["destino_cidade"], 80),
        "meio_transporte": limpar(r["meio_transporte"], 50),
        "numero_diarias": numero(r["numero_diarias"])
    })
    df["sequencia_trecho"] = df["sequencia_trecho"].map(
        lambda v: int(v) if pd.notna(v) and v % 1 == 0 else None
    )
    v = pd.to_numeric(df["numero_diarias"], errors="coerce")
    return df[v.isna() | (v >= 0)].copy()


with engine.begin() as conn:
    conn.execute(text("""
        TRUNCATE TABLE
            public.silver_trecho,
            public.silver_passagem,
            public.silver_pagamento,
            public.silver_viagem
        RESTART IDENTITY
    """))

    print("Transformando viagens...", flush=True)
    ids = viagens(conn)

    print("Transformando pagamentos...", flush=True)
    dependente(conn, "raw_pagamento", "silver_pagamento", pagamentos, ids)

    print("Transformando passagens...", flush=True)
    dependente(conn, "raw_passagem", "silver_passagem", passagens, ids)

    print("Transformando trechos...", flush=True)
    dependente(conn, "raw_trecho", "silver_trecho", trechos, ids)

print("Transformação SILVER concluída!")