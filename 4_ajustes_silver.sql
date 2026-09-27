-- Ajustes nas colunas da tabela passagem
ALTER TABLE silver.passagem
    ALTER COLUMN uf_destino_ida TYPE VARCHAR(100),
    ALTER COLUMN uf_destino_volta TYPE VARCHAR(100),
    ALTER COLUMN uf_origem_ida TYPE VARCHAR(100),
    ALTER COLUMN uf_origem_volta TYPE VARCHAR(100);

-- Ajustes nas colunas da tabela trecho
ALTER TABLE silver.trecho
    ALTER COLUMN origem_uf TYPE VARCHAR(100),
    ALTER COLUMN destino_uf TYPE VARCHAR(100);

-- Remove a regra que impedia propostas repetidas
ALTER TABLE silver.viagem
    DROP CONSTRAINT IF EXISTS uq_viagem_proposta;