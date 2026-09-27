
# Projeto Avaliativo — Análise de Dados
## Turma 05

## 1. Objetivo

Desenvolver um pipeline de dados utilizando Python, PostgreSQL e SQL, aplicando a arquitetura Medallion para organizar e analisar os dados de viagens de 2025.

## 2. Tecnologias utilizadas

- Python
- PostgreSQL
- SQL
- Pandas
- SQLAlchemy
- Jupyter Notebook
- Matplotlib
- Seaborn
- Git e GitHub

## 3. Arquitetura de dados

O projeto utiliza três camadas da arquitetura Medallion.

### RAW
Armazena os dados originais dos arquivos CSV, preservando os valores na forma textual.

### SILVER
Realiza a transformação dos dados, incluindo conversão de tipos e aplicação de regras de integridade.

### GOLD
Utiliza consultas SQL para análises e visualizações dos dados no Jupyter Notebook.

## 4. Estrutura do projeto

- `0_criar_banco.sql`: criação do banco e das tabelas.
- `1_extrair.py`: extração e carregamento dos dados na RAW.
- `2_transformar.py`: transformação e carregamento na SILVER.
- `3_analise.ipynb`: análises e gráficos.
- `4_ajustes_silver.sql`: ajustes na estrutura das tabelas SILVER.
- `banco.py`: configuração da conexão com o PostgreSQL.
- `config.py`: leitura das configurações do banco.
- `.env.example`: exemplo das variáveis de ambiente.
- `requirements.txt`: dependências do projeto.
- `.gitignore`: arquivos que não devem ser versionados.

## 5. Configuração do ambiente

Instale as dependências:

```bash
py -m pip install -r requirements.txt
```

Configure as variáveis de ambiente no arquivo `.env`, utilizando o `.env.example` como referência.

Crie o banco de dados PostgreSQL e execute o script `0_criar_banco.sql`, seguindo as instruções do próprio arquivo.

## 6. Execução do pipeline

Execute os scripts na seguinte ordem:

1. Extração dos dados:

```bash
py 1_extrair.py
```

2. Transformação dos dados:

```bash
py 2_transformar.py
```

3. Abra o notebook `3_analise.ipynb` no Jupyter Notebook ou no VS Code e execute as células de análise.

**Atenção:** o script de transformação limpa as tabelas SILVER antes de recarregá-las. A camada RAW é preservada.

## 7. Análises realizadas

O notebook apresenta três visualizações:

- Os dez órgãos superiores com maior quantidade de viagens.
- O valor total dos pagamentos por tipo.
- A quantidade de viagens por mês de início.

As análises de viagens abrangem o período de janeiro a junho de 2025.

## 8. Controle de versão

O projeto utiliza Git e GitHub para registrar as etapas de desenvolvimento, incluindo a configuração do banco, a extração, a transformação e as análises.