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