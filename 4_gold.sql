DROP TABLE IF EXISTS public.gold_resumo_orgao;

CREATE TABLE public.gold_resumo_orgao AS
SELECT
    v.nome_orgao_superior AS orgao,
    COUNT(*) AS quantidade_viagens,
    SUM(v.valor_total) AS custo_total
FROM public.silver_viagem v
WHERE v.situacao = 'Realizada'
GROUP BY v.nome_orgao_superior;

CREATE OR REPLACE VIEW public.vw_gold_resumo_orgao AS
SELECT
    v.nome_orgao_superior AS orgao,
    COUNT(*) AS quantidade_viagens,
    SUM(v.valor_total) AS custo_total
FROM public.silver_viagem v
WHERE v.situacao = 'Realizada'
GROUP BY v.nome_orgao_superior;
CREATE TABLE public.gold_resumo_trechos AS
SELECT
    v.nome_orgao_superior AS orgao,
    COUNT(DISTINCT v.id_viagem) AS quantidade_viagens,
    COUNT(t.id_trecho) AS quantidade_trechos
FROM public.silver_viagem v
JOIN public.silver_trecho t
    ON v.id_viagem = t.id_viagem
WHERE v.situacao = 'Realizada'
GROUP BY v.nome_orgao_superior;


CREATE OR REPLACE VIEW public.vw_gold_resumo_trechos AS
SELECT
    v.nome_orgao_superior AS orgao,
    COUNT(DISTINCT v.id_viagem) AS quantidade_viagens,
    COUNT(t.id_trecho) AS quantidade_trechos
FROM public.silver_viagem v
JOIN public.silver_trecho t
    ON v.id_viagem = t.id_viagem
WHERE v.situacao = 'Realizada'
GROUP BY v.nome_orgao_superior;