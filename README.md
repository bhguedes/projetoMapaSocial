# projetoMapaSocial
Projeto de BI que analisa dados de Segurança e educação no Brasil

Este projeto tem como objetivo analisar a relação entre **Segurança e Educação** no Brasil utilizando **BI**.

## Passo 1: Extração de Dados sobre Segurança do Atlas da Violência
Os dados foram obtidos através da API disponível: **IPEA - Atlas da Violência** https://www.ipea.gov.br/atlasviolencia/api.

## Passo 2: Extração de Dados sobre investimento em Segurança
Os dados fora obtidos através de consulta do **Portal da Transparência** https://portaldatransparencia.gov.br/despesas/funcao?de=01%2F01%2F2019&ate=01%2F12%2F2019&funcaoSubfuncao=FN06&ordenarPor=funcao&direcao=asc

## Passo 3: Extração de Dados sobre Educação
Os dados fora obtidos através de consulta dO **INEP** 

## Passo 4: Modelagem dos dados

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
