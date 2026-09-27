-- =========================================================
-- PROJETO AVALIATIVO - ANÁLISE DE DADOS
-- PostgreSQL
-- Camadas: RAW e SILVER
-- =========================================================

-- Criar schemas
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS silver;


-- =========================================================
-- RAW
-- Todos os campos permanecem VARCHAR.
-- Os dados serão carregados posteriormente pelos CSVs.
-- =========================================================

DROP TABLE IF EXISTS raw.viagem CASCADE;
DROP TABLE IF EXISTS raw.pagamento CASCADE;
DROP TABLE IF EXISTS raw.passagem CASCADE;
DROP TABLE IF EXISTS raw.trecho CASCADE;


CREATE TABLE raw.viagem (
    identificador_processo_viagem VARCHAR,
    numero_proposta_pcdp VARCHAR,
    situacao VARCHAR,
    viagem_urgente VARCHAR,
    justificativa_urgencia_viagem VARCHAR,
    codigo_orgao_superior VARCHAR,
    nome_orgao_superior VARCHAR,
    codigo_orgao_solicitante VARCHAR,
    nome_orgao_solicitante VARCHAR,
    cpf_viajante VARCHAR,
    nome VARCHAR,
    cargo VARCHAR,
    funcao VARCHAR,
    descricao_funcao VARCHAR,
    data_inicio VARCHAR,
    data_fim VARCHAR,
    destinos VARCHAR,
    motivo VARCHAR,
    valor_diarias VARCHAR,
    valor_passagens VARCHAR,
    valor_devolucao VARCHAR,
    valor_outros_gastos VARCHAR
);


CREATE TABLE raw.pagamento (
    identificador_processo_viagem VARCHAR,
    numero_proposta_pcdp VARCHAR,
    codigo_orgao_superior VARCHAR,
    nome_orgao_superior VARCHAR,
    codigo_orgao_pagador VARCHAR,
    nome_orgao_pagador VARCHAR,
    codigo_unidade_gestora_pagadora VARCHAR,
    nome_unidade_gestora_pagadora VARCHAR,
    tipo_pagamento VARCHAR,
    valor VARCHAR
);


CREATE TABLE raw.passagem (
    identificador_processo_viagem VARCHAR,
    numero_proposta_pcdp VARCHAR,
    meio_transporte VARCHAR,
    pais_origem_ida VARCHAR,
    uf_origem_ida VARCHAR,
    cidade_origem_ida VARCHAR,
    pais_destino_ida VARCHAR,
    uf_destino_ida VARCHAR,
    cidade_destino_ida VARCHAR,
    pais_origem_volta VARCHAR,
    uf_origem_volta VARCHAR,
    cidade_origem_volta VARCHAR,
    pais_destino_volta VARCHAR,
    uf_destino_volta VARCHAR,
    cidade_destino_volta VARCHAR,
    valor_passagem VARCHAR,
    taxa_servico VARCHAR,
    data_emissao_compra VARCHAR,
    hora_emissao_compra VARCHAR
);


CREATE TABLE raw.trecho (
    identificador_processo_viagem VARCHAR,
    numero_proposta_pcdp VARCHAR,
    sequencia_trecho VARCHAR,
    origem_data VARCHAR,
    origem_pais VARCHAR,
    origem_uf VARCHAR,
    origem_cidade VARCHAR,
    destino_data VARCHAR,
    destino_pais VARCHAR,
    destino_uf VARCHAR,
    destino_cidade VARCHAR,
    meio_transporte VARCHAR,
    numero_diarias VARCHAR,
    missao VARCHAR
);


-- =========================================================
-- SILVER
-- Dados tratados.
-- =========================================================

DROP TABLE IF EXISTS silver.pagamento CASCADE;
DROP TABLE IF EXISTS silver.passagem CASCADE;
DROP TABLE IF EXISTS silver.trecho CASCADE;
DROP TABLE IF EXISTS silver.viagem CASCADE;


CREATE TABLE silver.viagem (
    identificador_processo_viagem BIGINT PRIMARY KEY,
    numero_proposta_pcdp VARCHAR(50) NOT NULL,
    situacao VARCHAR(30) NOT NULL,
    viagem_urgente VARCHAR(3) NOT NULL,
    justificativa_urgencia_viagem TEXT,
    codigo_orgao_superior BIGINT,
    nome_orgao_superior VARCHAR(255),
    codigo_orgao_solicitante BIGINT,
    nome_orgao_solicitante VARCHAR(255),
    cpf_viajante VARCHAR(20),
    nome VARCHAR(255) NOT NULL,
    cargo VARCHAR(255),
    funcao VARCHAR(255),
    descricao_funcao VARCHAR(255),
    data_inicio DATE,
    data_fim DATE,
    destinos TEXT,
    motivo TEXT,
    valor_diarias NUMERIC(14,2),
    valor_passagens NUMERIC(14,2),
    valor_devolucao NUMERIC(14,2),
    valor_outros_gastos NUMERIC(14,2),

    CONSTRAINT chk_viagem_situacao
        CHECK (situacao IN ('Realizada', 'Não realizada')),

    CONSTRAINT chk_viagem_urgente
        CHECK (viagem_urgente IN ('SIM', 'NÃO')),

    CONSTRAINT chk_viagem_datas
        CHECK (data_fim IS NULL OR data_inicio IS NULL OR data_fim >= data_inicio),

    CONSTRAINT uq_viagem_proposta
        UNIQUE (numero_proposta_pcdp)
);


CREATE TABLE silver.pagamento (
    id_pagamento BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    identificador_processo_viagem BIGINT NOT NULL,
    numero_proposta_pcdp VARCHAR(50) NOT NULL,
    codigo_orgao_superior BIGINT,
    nome_orgao_superior VARCHAR(255),
    codigo_orgao_pagador BIGINT,
    nome_orgao_pagador VARCHAR(255),
    codigo_unidade_gestora_pagadora BIGINT,
    nome_unidade_gestora_pagadora VARCHAR(255),
    tipo_pagamento VARCHAR(100) NOT NULL,
    valor NUMERIC(14,2),

    CONSTRAINT fk_pagamento_viagem
        FOREIGN KEY (identificador_processo_viagem)
        REFERENCES silver.viagem (identificador_processo_viagem),

    CONSTRAINT chk_pagamento_tipo
        CHECK (
            tipo_pagamento IN (
                'DIÁRIAS',
                'PASSAGEM',
                'RESTITUIÇÃO',
                'Serviço correlato: seguro'
            )
        ),

    CONSTRAINT chk_pagamento_valor
        CHECK (valor IS NULL OR valor >= 0)
);


CREATE TABLE silver.passagem (
    id_passagem BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    identificador_processo_viagem BIGINT NOT NULL,
    numero_proposta_pcdp VARCHAR(50) NOT NULL,
    meio_transporte VARCHAR(50) NOT NULL,
    pais_origem_ida VARCHAR(100),
    uf_origem_ida VARCHAR(10),
    cidade_origem_ida VARCHAR(150),
    pais_destino_ida VARCHAR(100),
    uf_destino_ida VARCHAR(10),
    cidade_destino_ida VARCHAR(150),
    pais_origem_volta VARCHAR(100),
    uf_origem_volta VARCHAR(10),
    cidade_origem_volta VARCHAR(150),
    pais_destino_volta VARCHAR(100),
    uf_destino_volta VARCHAR(10),
    cidade_destino_volta VARCHAR(150),
    valor_passagem NUMERIC(14,2),
    taxa_servico NUMERIC(14,2),
    data_emissao_compra DATE,
    hora_emissao_compra TIME,

    CONSTRAINT fk_passagem_viagem
        FOREIGN KEY (identificador_processo_viagem)
        REFERENCES silver.viagem (identificador_processo_viagem),

    CONSTRAINT chk_passagem_valor
        CHECK (valor_passagem IS NULL OR valor_passagem >= 0),

    CONSTRAINT chk_passagem_taxa
        CHECK (taxa_servico IS NULL OR taxa_servico >= 0)
);


CREATE TABLE silver.trecho (
    id_trecho BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    identificador_processo_viagem BIGINT NOT NULL,
    numero_proposta_pcdp VARCHAR(50) NOT NULL,
    sequencia_trecho INTEGER NOT NULL,
    origem_data DATE,
    origem_pais VARCHAR(100),
    origem_uf VARCHAR(10),
    origem_cidade VARCHAR(150),
    destino_data DATE,
    destino_pais VARCHAR(100),
    destino_uf VARCHAR(10),
    destino_cidade VARCHAR(150),
    meio_transporte VARCHAR(50),
    numero_diarias NUMERIC(10,2),
    missao VARCHAR(3),

    CONSTRAINT fk_trecho_viagem
        FOREIGN KEY (identificador_processo_viagem)
        REFERENCES silver.viagem (identificador_processo_viagem),

    CONSTRAINT uq_trecho_sequencia
        UNIQUE (identificador_processo_viagem, sequencia_trecho),

    CONSTRAINT chk_trecho_sequencia
        CHECK (sequencia_trecho > 0),

    CONSTRAINT chk_trecho_diarias
        CHECK (numero_diarias IS NULL OR numero_diarias >= 0),

    CONSTRAINT chk_trecho_missao
        CHECK (missao IN ('Sim', 'Não'))
);


-- Índices para facilitar os JOINs e análises
CREATE INDEX idx_pagamento_processo
    ON silver.pagamento (identificador_processo_viagem);

CREATE INDEX idx_passagem_processo
    ON silver.passagem (identificador_processo_viagem);

CREATE INDEX idx_trecho_processo
    ON silver.trecho (identificador_processo_viagem);