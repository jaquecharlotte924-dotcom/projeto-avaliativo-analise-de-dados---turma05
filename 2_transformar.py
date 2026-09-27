
import pandas as pd
from datetime import datetime, time
from sqlalchemy import text
from banco import engine


def converter_valor(valor):
    if pd.isna(valor):
        return None

    valor = str(valor).strip()

    if valor == "" or valor.lower() in ["nan", "none"]:
        return None

    if "," in valor:
        valor = valor.replace(".", "").replace(",", ".")

    return valor


def converter_horario(valor):
    if pd.isna(valor):
        return None

    if isinstance(valor, time):
        return valor

    valor = str(valor).strip()

    if not valor or valor.lower() in ["nan", "none"]:
        return None

    for formato in ("%H:%M:%S.%f", "%H:%M:%S", "%H:%M"):
        try:
            return datetime.strptime(valor, formato).time()
        except ValueError:
            continue

    return None


def transformar_tabela(tabela):
    print(f"\nTransformando {tabela}...", flush=True)

    # Lê os dados da camada RAW
    df = pd.read_sql(f'SELECT * FROM raw."{tabela}"', engine)

    # Consulta a estrutura da tabela SILVER
    consulta = text("""
        SELECT column_name, data_type, is_identity, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'silver'
          AND table_name = :tabela
        ORDER BY ordinal_position
    """)

    with engine.connect() as conn:
        colunas_silver = pd.read_sql(
            consulta, conn, params={"tabela": tabela}
        )

    # Exclui as colunas geradas automaticamente
    colunas_identidade = colunas_silver.loc[
        colunas_silver["is_identity"] == "YES",
        "column_name"
    ].tolist()

    df = df.drop(columns=colunas_identidade, errors="ignore")

    # Converte os dados conforme os tipos do PostgreSQL
    for _, coluna in colunas_silver.iterrows():
        nome = coluna["column_name"]
        tipo = coluna["data_type"]

        if nome not in df.columns:
            continue

        if tipo in ["bigint", "integer", "smallint"]:
            df[nome] = pd.to_numeric(
                df[nome], errors="coerce"
            ).astype("Int64")

        elif tipo in ["numeric", "decimal", "real", "double precision"]:
            df[nome] = df[nome].apply(converter_valor)
            df[nome] = pd.to_numeric(
                df[nome], errors="coerce"
            )

        elif tipo.startswith("time"):
            df[nome] = df[nome].apply(converter_horario)

        elif tipo == "date" or "timestamp" in tipo:
            df[nome] = pd.to_datetime(
                df[nome], dayfirst=True, errors="coerce"
            )

    # Remove linhas sem os campos obrigatórios
    obrigatorias = colunas_silver.loc[
        (colunas_silver["is_nullable"] == "NO")
        & (colunas_silver["is_identity"] != "YES"),
        "column_name"
    ].tolist()

    obrigatorias = [c for c in obrigatorias if c in df.columns]

    if obrigatorias:
        df = df.dropna(subset=obrigatorias)

    # Mantém apenas viagens que existem na SILVER
    if tabela in ["pagamento", "passagem", "trecho"]:
        campo = "identificador_processo_viagem"

        if campo in df.columns:
            ids_viagem = pd.read_sql(
                f'SELECT "{campo}" FROM silver.viagem',
                engine
            )

            df = df[df[campo].isin(ids_viagem[campo])]

    # Mantém apenas as colunas existentes no destino
    colunas_validas = [
        c for c in colunas_silver["column_name"]
        if c in df.columns
    ]

    df = df[colunas_validas]

    # Cria tabela temporária para preparar a inserção
    staging = f"stg_{tabela}"

    df.to_sql(
        staging,
        engine,
        schema="silver",
        if_exists="replace",
        index=False,
        chunksize=2000,
        method="multi"
    )

    # Prepara conversões explícitas para o PostgreSQL
    expressoes = []

    for nome in colunas_validas:
        tipo = colunas_silver.loc[
            colunas_silver["column_name"] == nome,
            "data_type"
        ].iloc[0]

        coluna_sql = f'"{nome}"'

        if tipo.startswith("time"):
            expressao = f"NULLIF({coluna_sql}::text, '')::time"

        elif tipo == "date":
            expressao = f"NULLIF({coluna_sql}::text, '')::date"

        elif "timestamp" in tipo:
            if "with time zone" in tipo:
                expressao = (
                    f"NULLIF({coluna_sql}::text, '')"
                    "::timestamp with time zone"
                )
            else:
                expressao = (
                    f"NULLIF({coluna_sql}::text, '')"
                    "::timestamp without time zone"
                )

        elif tipo in ["bigint", "integer", "smallint"]:
            expressao = f"NULLIF({coluna_sql}::text, '')::{tipo}"

        elif tipo in ["numeric", "decimal", "real", "double precision"]:
            expressao = f"NULLIF({coluna_sql}::text, '')::{tipo}"

        else:
            expressao = coluna_sql

        expressoes.append(expressao)

    # Insere os dados sem apagar as tabelas ou suas restrições
    if colunas_validas:
        colunas_sql = ", ".join(
            f'"{c}"' for c in colunas_validas
        )
        valores_sql = ", ".join(expressoes)

        sql_insert = text(f"""
            INSERT INTO silver."{tabela}" ({colunas_sql})
            SELECT {valores_sql}
            FROM silver."{staging}"
            ON CONFLICT DO NOTHING
        """)

        with engine.begin() as conn:
            conn.execute(sql_insert)
            conn.execute(
                text(f'DROP TABLE IF EXISTS silver."{staging}"')
            )
    else:
        with engine.begin() as conn:
            conn.execute(
                text(f'DROP TABLE IF EXISTS silver."{staging}"')
            )

    # Consulta o total inserido
    with engine.connect() as conn:
        total = conn.execute(
            text(f'SELECT COUNT(*) FROM silver."{tabela}"')
        ).scalar()

    print(
        f"{tabela}: {total} registros na SILVER.",
        flush=True
    )


# Limpa a SILVER antes de recarregar os dados da RAW
with engine.begin() as conn:
    conn.execute(text("""
        TRUNCATE TABLE
            silver.pagamento,
            silver.passagem,
            silver.trecho,
            silver.viagem
        RESTART IDENTITY CASCADE
    """))

# A viagem deve ser carregada antes das tabelas dependentes
for tabela in ["viagem", "pagamento", "passagem", "trecho"]:
    transformar_tabela(tabela)

print("\nTransformação da camada SILVER concluída!", flush=True)