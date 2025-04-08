import requests
import time
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
from pathlib import Path
import os
from collections import Counter
import csv
import unittest

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("api_collector.log"), logging.StreamHandler()],
)

# URL base
BASE_URL = "https://www.ipea.gov.br/atlasviolencia/api/v1"

# Configurar sessão
session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})
session.verify = True

# Siglas esperadas para cada abrangência (para validação)
SIGLAS_ESPERADAS = {
    1: ["BRA"],
    2: ["N", "NE", "SE", "S", "CO"],
    3: ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"],
    4: None  # Para municípios, seria o código IBGE (muito extenso para listar aqui)
}

# Função para validar formato de data
def validar_formato_data(data_str):
    """
    Valida se a string de data está em um dos formatos aceitos: YYYY, YYYY-MM ou YYYY-MM-DD.

    Args:
        data_str (str): A data em formato de string.

    Returns:
        bool: True se o formato for válido, False caso contrário.
    """
    formatos_aceitos = ["%Y", "%Y-%m", "%Y-%m-%d"]
    for formato in formatos_aceitos:
        try:
            time.strptime(data_str, formato)
            return True
        except ValueError:
            continue
    return False

# Função para validar período
def validar_periodo(periodo_inicial, periodo_final):
    try:
        formato = "%Y" if len(periodo_inicial) == 4 else "%Y-%m" if len(periodo_inicial) == 7 else "%Y-%m-%d"
        inicio = time.strptime(periodo_inicial, formato)
        fim = time.strptime(periodo_final, formato)
        if inicio > fim:
            logging.error("Período inicial deve ser menor ou igual ao período final")
            return None, None
        return inicio, fim
    except ValueError as e:
        logging.error(f"Erro ao validar períodos: {e}")
        return None, None

# Função para fazer requisições com tratamento de erro e rate limiting
def get_dados(url, params=None):
    for tentativa in range(3):
        try:
            response = session.get(url, params=params, timeout=10)
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 5))
                logging.warning(f"Rate limit atingido. Aguardando {retry_after} segundos...")
                time.sleep(retry_after)
                continue
            elif response.status_code == 404:
                logging.error(f"Série ou recurso não encontrado: {url}")
                return None
            response.raise_for_status()
            data = response.json()
            if not data:
                logging.warning(f"Resposta vazia para {url}")
            return data
        except requests.exceptions.RequestException as e:
            logging.error(f"Erro ao acessar {url} (tentativa {tentativa+1}/3): {e}")
            time.sleep(2)
    return None

# Função para processar uma série
def processar_serie(serie, abrangencia, periodo_inicial, periodo_final):
    serie_id = serie.get("id")
    if not serie_id or not isinstance(serie_id, int):
        logging.warning(f"Série com ID inválido: {serie}")
        return None

    logging.info(f"Processando série: {serie.get('titulo', 'Sem título')} (ID: {serie_id})")

    valores = []
    for ano in range(int(periodo_inicial[:4]), int(periodo_final[:4]) + 1):
        params = {"inicial": f"{ano}-01-01", "final": f"{ano}-12-31"}
        valores_ano = get_dados(f"{BASE_URL}/valores-series/{serie_id}/{abrangencia}", params=params)
        if valores_ano:
            logging.info(f"Dados retornados para série {serie_id}, abrangência {abrangencia}: {valores_ano}")
            for valor in valores_ano:
                periodo = valor.get("periodo")
                if periodo and len(periodo) >= 4:
                    valor["ano"] = periodo[:4]  # Extrai os primeiros 4 caracteres como o ano
                else:
                    valor["ano"] = None
                    logging.warning(f"Campo 'periodo' ausente ou inválido para o valor: {valor}")
                logging.info(f"Processando valor: {valor}")
            valores.extend(valores_ano)
        else:
            logging.warning(f"Nenhum dado retornado para série {serie_id}, abrangência {abrangencia}")

    if valores:
        return {
            "serie_id": serie_id,
            "titulo": serie.get("titulo", "Sem título"),
            "valores": valores
        }
    else:
        logging.error(f"Nenhum valor processado para série {serie_id}")
        return None

# Função para achatar dados
def achatar_dados(dados_consolidados):
    linhas = []
    for dado in dados_consolidados:
        serie_id = dado.get("serie_id")
        titulo = dado.get("titulo")
        valores = dado.get("valores", [])
        
        for valor in valores:
            linha = {
                "serie_id": serie_id,
                "titulo": titulo,
                "sigla": valor.get("sigla"),
                "ano": valor.get("ano"),
                "valor": valor.get("valor"),
            }
            linhas.append(linha)
    return linhas

# Função para salvar dados achatados em CSV
def salvar_csv(dados_achatados, caminho):
    with open(caminho, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["serie_id", "titulo", "sigla", "ano", "valor"])
        writer.writeheader()
        writer.writerows(dados_achatados)
    logging.info(f"Dados achatados salvos em {caminho}")

# Função principal
def main(args):
    # Log para confirmar a abrangência usada
    logging.info(f"Abrangência selecionada: {args.abrangencia} (1=País, 2=Região, 3=UF, 4=Município)")

    # Validar parâmetros
    if not (1 <= args.abrangencia <= 4):
        logging.error("Abrangência inválida. Use: 1 (País), 2 (Região), 3 (UF), 4 (Município)")
        import sys
        sys.exit()
    if not validar_formato_data(args.periodo_inicial) or not validar_formato_data(args.periodo_final):
        logging.error("Períodos devem estar no formato YYYY, YYYY-MM ou YYYY-MM-DD")
        import sys
        sys.exit()
    periodo_inicial, periodo_final = validar_periodo(args.periodo_inicial, args.periodo_final)
    if not periodo_inicial or not periodo_final:
        import sys
        sys.exit()

    # Aviso para abrangência 4 (municípios)
    if args.abrangencia == 4:
        logging.warning("Abrangência 4 (Municípios) pode retornar um grande volume de dados. A API não suporta paginação, o que pode causar problemas de desempenho.")

    # Criar diretório de saída
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    # 1 Obter Temas Disponíveis
    temas = get_dados(f"{BASE_URL}/temas")
    if not temas:
        logging.error("Falha ao obter temas. Verifique a conexão ou disponibilidade da API.")
        import sys
        sys.exit()

    dados_consolidados = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = []
        for tema in temas:
            tema_id = tema.get("id")
            if not tema_id or not isinstance(tema_id, int):
                logging.warning(f"Tema com ID inválido: {tema}")
                continue

            logging.info(f"Processando tema: {tema.get('titulo', 'Sem título')}")

            # 2 Obter Séries do Tema
            series = get_dados(f"{BASE_URL}/series/{tema_id}")
            if series:
                for serie in series:
                    futures.append(
                        executor.submit(
                            processar_serie, serie, args.abrangencia, args.periodo_inicial, args.periodo_final
                        )
                    )

        # Aguardar e coletar resultados
        for future in as_completed(futures):
            try:
                resultado = future.result()
                if resultado:
                    dados_consolidados.append(resultado)
            except Exception as e:
                logging.error(f"Erro ao processar série: {e}")

    # Após consolidar os dados
    if not dados_consolidados:
        logging.error("Nenhum dado consolidado foi coletado.")
        return

    # Achatar os dados
    dados_achatados = achatar_dados(dados_consolidados)

    # Salvar em JSON (opcional)
    json_path = os.path.join(args.output_dir, "dados_consolidados.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(dados_consolidados, f, ensure_ascii=False, indent=4)
    logging.info(f"Dados salvos em {json_path}")

    # Salvar em CSV
    csv_path = os.path.join(args.output_dir, "dados_consolidados.csv")
    salvar_csv(dados_achatados, csv_path)

# Configuração de argumentos de linha de comando
def parse_args():
    parser = argparse.ArgumentParser(description="Coletor de dados da API do Atlas da Violência (IPEA)")
    parser.add_argument("--abrangencia", type=int, default=1, choices=[1, 2, 3, 4],
                        help="Abrangência: 1=País, 2=Região, 3=UF, 4=Município (padrão: 1)")
    parser.add_argument("--periodo-inicial", type=str, default="2010",
                        help="Período inicial (formato: YYYY, YYYY-MM ou YYYY-MM-DD, padrão: 2010)")
    parser.add_argument("--periodo-final", type=str, default="2023",
                        help="Período final (formato: YYYY, YYYY-MM ou YYYY-MM-DD, padrão: 2023)")
    parser.add_argument("--workers", type=int, default=5,
                        help="Número de workers para processamento paralelo (padrão: 5)")
    parser.add_argument("--output-dir", type=str, default="output",
                        help="Diretório de saída para os arquivos (padrão: output)")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    periodo_inicial, periodo_final = validar_periodo(args.periodo_inicial, args.periodo_final)
    if not periodo_inicial or not periodo_final:
        import sys
        sys.exit()  # Encerra o programa corretamente
    main(args)

class TestValidacoes(unittest.TestCase):
    def test_validar_formato_data(self):
        self.assertTrue(validar_formato_data("2023"))
        self.assertTrue(validar_formato_data("2023-01"))
        self.assertTrue(validar_formato_data("2023-01-01"))
        self.assertFalse(validar_formato_data("01-2023"))