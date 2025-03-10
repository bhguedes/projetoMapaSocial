import requests
import time
import json
import logging
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("api_collector.log"), logging.StreamHandler()],
)

# URL base da API
BASE_URL = "https://www.ipea.gov.br/atlasviolencia/api/v1"

# Configurar uma sessão para melhor performance e reaproveitamento da conexão
session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})

# Função para fazer requisições com tratamento de erro
def get_dados(url, params=None):
    for tentativa in range(3):  # Tenta até 3 vezes antes de desistir
        try:
            response = session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            if not data:
                logging.warning(f"Resposta vazia para {url}")
            return data
        except requests.exceptions.RequestException as e:
            logging.error(f"Erro ao acessar {url} (tentativa {tentativa+1}/3): {e}")
            time.sleep(2)  # Espera antes de tentar novamente
    return None  # Retorna None se falhar todas as tentativas

# Função para processar uma série e retornar os dados
def processar_serie(serie, abrangencia, periodo_inicial, periodo_final):
    serie_id = serie.get("id")
    if serie_id is None:
        logging.warning(f"Série sem ID válido: {serie}")
        return None

    logging.info(f"Processando série: {serie.get('titulo', 'Sem título')} (ID: {serie_id})")

    # Obter Valores Estatísticos da Série
    valores = get_dados(
        f"{BASE_URL}/valores-series/{serie_id}/{abrangencia}",
        params={"inicial": periodo_inicial, "final": periodo_final},
    )

    if valores:
        logging.info(f"Dados coletados para a série {serie_id}: {valores}")
        return {
            "serie_id": serie_id,
            "titulo": serie.get("titulo", "Sem título"),
            "valores": valores
        }
    else:
        logging.error(f"Erro ao obter valores da série {serie_id}")
        return None

# Função principal
def main():
    # Definir parâmetros opcionais
    abrangencia = 1  # 1 = País, 2 = Região, 3 = UF, 4 = Município
    periodo_inicial = "2010"  # Exemplo de período
    periodo_final = "2023"  # Exemplo de período

    # 1️⃣ Obter Temas Disponíveis
    temas = get_dados(f"{BASE_URL}/temas")

    if not temas:
        logging.error("Falha ao obter temas. Verifique a conexão ou disponibilidade da API.")
        return

    # Lista para armazenar todos os dados consolidados
    dados_consolidados = []

    # Processar temas em paralelo
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for tema in temas:
            tema_id = tema.get("id")
            if tema_id is None:
                logging.warning(f"Tema sem ID válido: {tema}")
                continue

            logging.info(f"Processando tema: {tema.get('titulo', 'Sem título')}")

            # 2️⃣ Obter Séries do Tema
            series = get_dados(f"{BASE_URL}/series/{tema_id}")

            if series:
                # Processar séries em paralelo
                for serie in series:
                    futures.append(
                        executor.submit(
                            processar_serie, serie, abrangencia, periodo_inicial, periodo_final
                        )
                    )

        # Aguardar a conclusão de todas as tarefas
        for future in as_completed(futures):
            try:
                resultado = future.result()
                if resultado:
                    dados_consolidados.append(resultado)
            except Exception as e:
                logging.error(f"Erro ao processar série: {e}")

    # Salvar os dados consolidados em um arquivo JSON
    with open("dados_consolidados.json", "w", encoding="utf-8") as f:
        json.dump(dados_consolidados, f, ensure_ascii=False, indent=4)

    # Verificar se há dados consolidados
    if not dados_consolidados:
        logging.error("Nenhum dado consolidado foi coletado.")
        return

    # Converter os dados consolidados em um DataFrame e salvar como CSV
    dados_para_csv = []
    for item in dados_consolidados:
        serie_id = item["serie_id"]
        titulo = item["titulo"]
        valores = item["valores"]

        # Verificar a estrutura dos valores
        if isinstance(valores, list):  # Se for uma lista
            for valor in valores:
                if isinstance(valor, dict):  # Se for um dicionário
                    # Verificar se as chaves esperadas existem
                    if "ano" in valor and "valor" in valor:
                        dados_para_csv.append({
                            "serie_id": serie_id,
                            "titulo": titulo,
                            "ano": valor["ano"],
                            "valor": valor["valor"]
                        })
                    else:
                        logging.warning(f"Estrutura inesperada nos valores da série {serie_id}: {valor}")
                else:
                    logging.warning(f"Valor inesperado na série {serie_id}: {valor}")
        else:
            logging.warning(f"Valores da série {serie_id} não são uma lista: {valores}")

    # Verificar se há dados para o CSV
    if not dados_para_csv:
        logging.error("Nenhum dado válido foi encontrado para gerar o CSV.")
        return

    # Criar DataFrame e salvar como CSV
    df = pd.DataFrame(dados_para_csv)
    df.to_csv("dados_consolidados.csv", index=False, encoding="utf-8")
    logging.info("Dados consolidados salvos em 'dados_consolidados.json' e 'dados_consolidados.csv'.")

if __name__ == "__main__":
    main()