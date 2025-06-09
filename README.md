<<<<<<< HEAD
# Mapa Social – Projeto de BI  
Análise da relação entre Segurança Pública e Educação no Brasil

## Visão Geral  
O **Mapa Social** é um projeto de Business Intelligence que visa correlacionar **índices de criminalidade**, **indicadores educacionais** e **investimentos públicos** no Brasil. Utiliza dados abertos e integra diversas fontes para gerar insights com potencial de impacto em **políticas públicas**.

## Objetivo  
Demonstrar, com base em dados concretos, como os investimentos em **Educação** e **Segurança Pública** impactam os índices de **violência** no Brasil. A solução foi desenvolvida no **Power BI**, com foco na visualização clara e analítica dos dados.

---

## Estrutura do Projeto

### Passo 1: Dados de Segurança (Atlas da Violência)  
Fonte: [API do Atlas da Violência – IPEA](https://www.ipea.gov.br/atlasviolencia/api)  
Coleta de indicadores históricos sobre violência por estado.

### Passo 2: Investimentos em Segurança Pública  
Fonte: [Portal da Transparência](https://portaldatransparencia.gov.br/despesas/funcao?de=01%2F01%2F2019&ate=01%2F12%2F2019&funcaoSubfuncao=FN06&ordenarPor=funcao&direcao=asc)  
Consulta a dados de execução orçamentária para a função "Segurança Pública".

### Passo 3: Indicadores de Educação  
Fonte: INEP – Censo Escolar 2022  
Coleta de dados sobre matrícula escolar, regime de ensino (integral/parcial) e cobertura educacional por UF.

### Passo 4: Modelagem de Dados  
Os dados foram tratados, padronizados e integrados no Power BI. A modelagem considera relações temporais, geográficas (por UF) e categorização temática (educação, orçamento, criminalidade).

## Tabelas no Modelo de Dados

### `dCALENDARIO`  
Tabela de datas para relacionamentos temporais.  
Campos principais: `Date`, `Ano`, `Mês`, `Trimestre`, `Dia da Semana`.

### `ATLAS_ATÉ_2022`  
Indicadores de violência por estado e ano.  
Campos: `ano`, `serie_id`, `sigla`, `titulo`, `valor`.

### `CENSO_ESCOLAR_2022`  
Dados de matrículas por UF, por nível de ensino e regime.  
Campos: `UF`, `Fundamental`, `Médio`, `Pré-escola`, `Integral`, `Parcial`.

### `CRIMES_2022`  
Ocorrências criminais por categoria e perfil das vítimas.  
Campos: `data_referencia`, `evento`, `faixa_etaria`, `sexo`, `total_vitima`, `uf`, `agente`, `arma`.

### `ORÇAMENTO_2022`  
Execução orçamentária por função, ação e órgão.  
Campos: `ORÇAMENTO ATUALIZADO`, `REALIZADO`, `% REALIZADO`, `EXERCICIO`, `função`, `programa`.

---

## Dashboard (Power BI)  
Apresentado em 3 telas principais:

### Tela 1 – Comparativo de Gastos Públicos (2022)  
- **Conteúdo:** Orçamentos realizados em Segurança Pública e Educação.  
- **Valor:** Evidencia desequilíbrios de investimento, apoiando decisões de realocação de recursos.

### Tela 2 – Distribuição de Homicídios (2022)  
- **Conteúdo:** Análise de 161.252 homicídios por UF, faixa etária e gênero.  
- **Valor:** Aponta regiões críticas e o perfil das vítimas, guiando ações policiais e sociais.

### Tela 3 – Educação vs. Homicídios de Jovens  
- **Conteúdo:** Correlação entre taxas de matrícula escolar e índices de homicídios entre jovens.  
- **Valor:** Sugere impacto da educação na prevenção da violência estrutural.

---

## Glossário

- **Valor (Atlas):** Indicador de violência por estado/ano.  
- **Orçamento Realizado:** Gasto efetivamente executado.  
- **Faixa Etária (Crimes):** Categoria de idade das vítimas.

---

## Conclusão  
O **Mapa Social** entrega uma análise integrada entre dados de educação, segurança e gastos públicas. Com isso, busco orientar **estratégias governamentais** e **ações sociais** mais eficazes.

**Versão:** Maio/2025
"""
=======
# projetoMapaSocial
Projeto de BI que analisa dados de Segurança e educação no Brasil

Este projeto tem como objetivo analisar a relação entre **Segurança e Educação** no Brasil utilizando **BI**.

## Passo 1: Extração de Dados sobre Segurança do Atlas da Violência
Os dados foram obtidos através da API disponível: **IPEA - Atlas da Violência** https://www.ipea.gov.br/atlasviolencia/api.

## Passo 2: Extração de Dados sobre investimento em Segurança
Os dados fora obtidos através de consulta do **Portal da Transparência** https://portaldatransparencia.gov.br/despesas/funcao?de=01%2F01%2F2019&ate=01%2F12%2F2019&funcaoSubfuncao=FN06&ordenarPor=funcao&direcao=asc

## Passo 3: Extração de Dados sobre Educação
Os dados fora obtidos através de consulta dO **INEP** 


## Passo 4: Modelagem de Dados
# Projeto BI - Mapa Social

## Visão Geral
O projeto **Mapa Social** visa correlacionar índices de criminalidade com investimentos públicos e indicadores educacionais. A análise é feita por meio de dados integrados no Power BI, utilizando dados do Atlas da Violência, Censo Escolar, orçamento público e ocorrências de crimes.

---

## Tabelas do Modelo de Dados

### dCALENDARIO
**Finalidade:** Tabela de datas que centraliza o relacionamento temporal do modelo.  
**Campos principais:**
- `Date`: data completa
- `Ano`: ano da data
- `Mês`: número do mês
- `Mês texto`: nome do mês
- `Dia da Semana`, `Fim de Semana`, `Trimestre`

### ATLAS ATÉ 2022
**Finalidade:** Traz séries históricas de indicadores de violência por estado.  
**Campos principais:**
- `ano`: ano da medição
- `serie_id`: identificador do indicador
- `sigla`: UF
- `titulo`: nome do indicador
- `valor`: valor numérico

### CENSO-ESCOLAR-2022
**Finalidade:** Indicadores educacionais por UF.  
**Campos principais (parciais e integrais):**
- `Fundamental`, `Médio`, `Pré-escola`, por tipo de regime (integral/parcial)
- `UF - Estadual e Municipal`: chave de localização

### CRIMES-2022
**Finalidade:** Ocorrências de crimes categorizadas.  
**Campos principais:**
- `data_referencia`: data da ocorrência
- `evento`: tipo de crime
- `faixa_etaria`, `feminino`, `masculino`, `nao_informado`
- `total`, `total_peso`, `total_vitima`
- `uf`, `abrangencia`, `agente`, `arma`

### ORÇAMENTO-2022
**Finalidade:** Dados orçamentários públicos por função/órgão.  
**Campos principais:**
- `ORÇAMENTO ATUALIZADO`, `EMPENHADO`, `REALIZADO`, `INICIAL`
- `% REALIZADO DO ORÇAMENTO`
- Códigos e nomes de: função, ação, despesa, órgão, programa
- `EXERCICIO`: ano do orçamento

---

## Relacionamentos do Modelo

### Estrutura das Relações

- `dCALENDARIO.Date` → `CRIMES-2022.data_referencia` (1:N)
- `dCALENDARIO.Ano` → `ATLAS ATÉ 2022.ano` (1:N)
- `dCALENDARIO.Ano` → `ORÇAMENTO-2022.EXERCICIO` (1:N)

### Observações
- Os dados do CENSO ESCOLAR não possuem relacionamento direto no modelo atual. Podem ser relacionados futuramente via UF + Ano.

---

## Glossário de Indicadores e Termos

- **Valor (ATLAS):** valor do indicador para o estado no ano.
- **Orçamento Realizado:** quanto foi efetivamente gasto.
- **Orçamento Empenhado:** quanto foi reservado para gastar.
- **Faixa Etária (CRIMES):** categorização da idade das vítimas.

---

## Observações Finais

Este modelo será usado para correlacionar investimento público com índices de criminalidade, visando análises de impacto social para políticas públicas.

**Versão:** Abril/2025
>>>>>>> 8e484bdbc058ce05ba9bb8c57260182753ecf98f
