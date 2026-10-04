# Projeto Avaliativo — Análise de Dados de Viagens 2025

## Turma 05

## 1. Sobre o projeto

Este projeto desenvolve um pipeline de dados para extrair, transformar e analisar dados públicos de viagens de 2025.

A solução utiliza a arquitetura **Medallion**, organizada em três camadas:

- **RAW:** recebe os dados originais dos arquivos CSV e preserva os valores em formato textual.
- **SILVER:** realiza limpeza, conversão de tipos, cálculos e aplicação das regras de integridade.
- **GOLD:** reúne agregações e consultas utilizadas nas análises de negócio e nas visualizações.

O projeto utiliza Python, PostgreSQL, SQL e Jupyter Notebook para transformar os dados brutos em informações úteis para análise.

## 2. Problema que o projeto resolve

Os arquivos de viagens possuem informações distribuídas em diferentes bases, incluindo viagens, pagamentos, passagens e trechos. O projeto organiza essas informações em um fluxo único de tratamento e análise.

Com a estrutura criada, é possível analisar custos, duração das viagens, tipos de pagamento, meios de transporte, destinos e órgãos responsáveis pelos gastos.

## 3. Objetivos

- Organizar os dados de viagens de 2025 em camadas RAW, SILVER e GOLD.
- Transformar campos textuais em tipos adequados para análise.
- Garantir regras básicas de integridade dos dados.
- Responder às sete perguntas de negócio definidas no projeto.
- Criar gráficos para facilitar a interpretação dos resultados.

## 4. Tecnologias utilizadas

- Python
- Pandas
- PostgreSQL
- SQL
- SQLAlchemy
- Psycopg2
- Jupyter Notebook
- Matplotlib
- Seaborn
- Git e GitHub

## 5. Arquitetura de dados

### RAW

A camada RAW armazena os dados originais dos quatro arquivos CSV. As colunas são mantidas como `VARCHAR`, sem aplicação das regras de negócio da camada SILVER.

Tabelas:

- `raw_viagem`
- `raw_pagamento`
- `raw_passagem`
- `raw_trecho`

### SILVER

A camada SILVER transforma os dados da RAW para tipos adequados às análises.

Nessa etapa são realizadas, entre outras, as seguintes transformações:

- textos para números decimais;
- textos para datas;
- conversão de campos inteiros;
- tratamento de valores vazios;
- cálculo do custo total da viagem;
- cálculo da duração da viagem.

O custo total é calculado por:

```text
valor_diarias + valor_passagens + valor_outros_gastos - valor_devolucao
```

A duração é calculada por:

```text
(data_fim - data_inicio) + 1
```

Assim, o primeiro e o último dia da viagem são contabilizados.

Tabelas:

- `silver_viagem`
- `silver_pagamento`
- `silver_passagem`
- `silver_trecho`

A modelagem utiliza **4 chaves primárias, 3 chaves estrangeiras e 8 constraints extras**, conforme o enunciado.

### GOLD

A camada GOLD contém agregações preparadas para as análises.

Foram criadas:

- `gold_resumo_orgao`
- `vw_gold_resumo_orgao`
- `gold_resumo_trechos`
- `vw_gold_resumo_trechos`

A agregação de trechos utiliza `JOIN` entre `silver_viagem` e `silver_trecho`, agrupando os resultados por órgão com `GROUP BY`.

## 6. Dados utilizados

O projeto utiliza quatro arquivos CSV:

- `2025_Viagem.csv`
- `2025_Pagamento.csv`
- `2025_Passagem.csv`
- `2025_Trecho.csv`

Quantidade de registros carregados:

| Tabela | Registros |
|---|---:|
| viagem | 341.860 |
| pagamento | 606.916 |
| passagem | 167.260 |
| trecho | 763.349 |
| **Total** | **1.879.385** |

### Conferência RAW x SILVER

As conferências realizadas apresentaram os mesmos resultados da base de referência:

- 341.860 registros de viagens na RAW e na SILVER;
- 606.916 registros de pagamentos na RAW e na SILVER;
- 167.260 registros de passagens na RAW e na SILVER;
- 763.349 registros de trechos na RAW e na SILVER;
- 664 datas de emissão vazias na RAW foram tratadas como `NULL` na SILVER;
- a soma dos pagamentos permaneceu em **R$ 1.194.365.457,37** na RAW e na SILVER.

## 7. Estrutura do repositório

Os principais arquivos do projeto são:

- `0_criar_banco.sql`: criação das tabelas RAW e SILVER, chaves e constraints.
- `0_ajustes_silver.sql`: ajustes realizados na estrutura da camada SILVER.
- `1_extrair.py`: leitura e carga dos arquivos CSV na camada RAW.
- `2_transformar.py`: transformação dos dados da RAW para a SILVER.
- `3_analise.ipynb`: consultas, resultados, gráficos e conclusões das perguntas de negócio.
- `4_gold.sql`: criação das tabelas e views da camada GOLD.
- `banco.py`: conexão com o PostgreSQL.
- `config.py`: leitura das configurações do banco.
- `.env.example`: modelo das variáveis de ambiente.
- `requirements.txt`: bibliotecas utilizadas no projeto.
- `.gitignore`: arquivos e dados que não devem ser versionados.

## 8. Configuração do ambiente

### 8.1 Pré-requisitos

É necessário ter instalado:

- Python 3.x
- PostgreSQL
- Git

### 8.2 Instalação das dependências

No terminal, dentro da pasta do projeto:

```bash
py -m pip install -r requirements.txt
```

### 8.3 Configuração das credenciais

Crie o arquivo `.env` a partir do `.env.example` e informe os dados de conexão do PostgreSQL.

O arquivo `.env` contém informações privadas e **não deve ser enviado ao GitHub**.

### 8.4 Banco de dados

Conecte-se ao banco PostgreSQL do projeto e execute o script:

```text
0_criar_banco.sql
```

Esse arquivo cria as tabelas RAW e SILVER utilizadas pelo pipeline.

## 9. Como executar — jeito mais fácil pelo VS Code e notebook

1. Abra a pasta do projeto no VS Code.
2. Confirme que o PostgreSQL está instalado e que o banco do projeto está disponível.
3. Garanta que os quatro arquivos CSV estejam na pasta esperada pelo `1_extrair.py`.
4. Execute no terminal:

```bash
py 1_extrair.py
```

5. Depois execute:

```bash
py 2_transformar.py
```

6. Execute o `4_gold.sql` no PostgreSQL para criar a camada GOLD.
7. Abra o arquivo `3_analise.ipynb` no VS Code.
8. Selecione o kernel Python do projeto.
9. Execute as células do notebook de cima para baixo ou use **Run All**.

O notebook realiza as consultas SQL, apresenta os resultados e gera os gráficos.

## 10. Como executar — pelo terminal, arquivo por arquivo

### Ambiente

```bash
py -m pip install -r requirements.txt
```

### Credenciais

Crie o `.env` utilizando o `.env.example` como referência.

### Banco e tabelas

Execute `0_criar_banco.sql` no PostgreSQL.

### Pipeline

```bash
py 1_extrair.py
py 2_transformar.py
```

Depois, execute `4_gold.sql` no PostgreSQL.

Por fim, abra `3_analise.ipynb` e execute as células de análise.

### Reexecução

O processo pode ser executado novamente. A carga da RAW é refeita e a SILVER é limpa antes da transformação, evitando o acúmulo dos registros anteriores.

## 11. Regras utilizadas nas análises

As sete perguntas de negócio consideram somente viagens com:

```text
situacao = 'Realizada'
```

### Custo total da viagem

```text
diárias + passagens + outros gastos - devolução
```

### Duração

```text
(data_fim - data_inicio) + 1
```

### Destinos

O campo `destinos` é tratado como texto livre. Textos exatamente iguais são considerados o mesmo destino. Para a análise de custo médio, são considerados somente destinos com pelo menos 100 viagens.

### Valor médio por tipo de pagamento

O valor médio é calculado por:

```text
SUM(valor) / COUNT(*)
```

Os valores `Sigiloso` e `Inválido`, quando presentes nos dados, são mantidos e não são removidos artificialmente da base.

## 12. Perguntas de negócio e resultados

### 1. Quais 5 órgãos têm maior custo total?

1. Ministério da Justiça e Segurança Pública — **R$ 485.748.241,43**
2. Ministério da Defesa — **R$ 154.595.910,29**
3. Ministério da Educação — **R$ 109.759.836,03**
4. Ministério do Meio Ambiente e Mudança do Clima — **R$ 49.300.595,26**
5. Ministério da Previdência Social — **R$ 40.236.180,79**

### 2. Quais 3 destinos têm maior custo médio por viagem?

Considerando somente destinos com pelo menos 100 viagens:

1. Brasília/DF, Brasília/DF — **R$ 27.401,80** — 283 viagens
2. Genebra/Suíça — **R$ 25.469,22** — 242 viagens
3. Nova York/Estados Unidos — **R$ 21.214,19** — 149 viagens

### 3. Qual viagem tem maior duração e qual foi seu custo total?

A viagem `000000000020699856` apresentou:

- destino: **Mogi Mirim/SP**;
- duração: **384 dias**;
- custo total registrado: **R$ 0,00**.

### 4. Qual tipo de pagamento tem maior valor médio?

**Diárias — R$ 2.078,79**.

### 5. Qual meio de transporte é mais utilizado nos trechos?

**Veículo Oficial — 385.734 trechos**.

### 6. Qual UF de destino aparece mais nos trechos?

**São Paulo — 81.727 trechos**.

### 7. Qual órgão pagou mais no total?

**Fundo Nacional de Segurança Pública — R$ 278.288.685,42**.

O órgão pagador `Sigiloso` aparece em seguida, com **R$ 199.308.482,09**.

## 13. Visualizações

O notebook `3_analise.ipynb` apresenta **7 gráficos**, um para cada pergunta de negócio:

1. 5 órgãos com maior custo total.
2. 3 destinos com maior custo médio por viagem.
3. Viagem com maior duração.
4. Valor médio por tipo de pagamento.
5. 5 meios de transporte mais utilizados.
6. 5 UFs de destino mais frequentes.
7. 5 órgãos pagadores com maior valor total.

Os gráficos possuem título, eixos nomeados e legenda quando aplicável.

## 14. Conclusões e insights

A análise mostrou que os custos das viagens estão concentrados principalmente em alguns órgãos públicos. O Ministério da Justiça e Segurança Pública apresentou o maior custo total entre os cinco primeiros órgãos.

Entre os destinos com pelo menos 100 viagens, Brasília/DF, Brasília/DF apresentou o maior custo médio por viagem. Genebra/Suíça e Nova York/Estados Unidos aparecem na sequência.

A viagem de maior duração apresentou 384 dias, com custo total registrado de R$ 0,00.

As diárias apresentaram o maior valor médio entre os tipos de pagamento analisados.

Nos trechos, o Veículo Oficial foi o meio de transporte mais utilizado, enquanto São Paulo foi a UF de destino mais frequente.

No total pago por órgão, o Fundo Nacional de Segurança Pública apresentou o maior valor.

## 15. Limitações

- Os dados analisados correspondem ao período de **janeiro a junho de 2025**.
- O campo `destinos` é texto livre e diferentes formas de escrita podem representar o mesmo local.
- O órgão pagador `Sigiloso` é mantido na base, portanto existe uma limitação de identificação para parte dos pagamentos.
- O meio de transporte `Inválido` é mantido na base conforme os dados de origem.

## 16. Possíveis melhorias

- Separar `destinos` em cidade, UF e país para melhorar as análises.
- Criar um dashboard interativo.
- Ampliar a análise para outros períodos e anos.
- Criar novas agregações na GOLD para futuras perguntas de negócio.
- Automatizar a atualização dos dados e das visualizações.

## 17. Controle de versão

O projeto utiliza Git e GitHub para registrar as etapas de desenvolvimento.

Os principais momentos do desenvolvimento foram organizados em commits, acompanhando a criação do banco, extração, transformação, análises e documentação.

## 18. Segurança e boas práticas

- Não versionar o arquivo `.env`.
- Não versionar senhas ou outras credenciais.
- Não enviar dados brutos para o GitHub quando protegidos pelo `.gitignore`.
- Utilizar `.env.example` como modelo para configuração do ambiente.

## 19. Fluxo do projeto

```text
Arquivos CSV
     ↓
   RAW
     ↓
Transformação com Python
     ↓
  SILVER
     ↓
Agregações SQL
(JOIN + GROUP BY)
     ↓
   GOLD
     ↓
7 perguntas de negócio
     ↓
7 gráficos + conclusões
```

## 20. Resultado final

O projeto apresenta um pipeline completo de dados, desde a carga dos arquivos CSV até a transformação, agregação e análise das informações em PostgreSQL, Python e Jupyter Notebook.

A solução permite reproduzir as etapas do processo e responder às perguntas de negócio com resultados documentados e visualizações.
