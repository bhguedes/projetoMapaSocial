import requests
import time
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
from pathlib import Path
import os
from collections import Counter
import csvimport csv

# Configuração do logginggging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("api_collector.log"), logging.StreamHandler()],   handlers=[logging.FileHandler("api_collector.log"), logging.StreamHandler()],
))

# URL base
BASE_URL = "https://www.ipea.gov.br/atlasviolencia/api/v1"BASE_URL = "https://www.ipea.gov.br/atlasviolencia/api/v1"

# Configurar sessão
session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})e({"User-Agent": "Mozilla/5.0"})
session.verify = Truesession.verify = True

# Siglas esperadas para cada abrangência (para validação)ara cada abrangência (para validação)
SIGLAS_ESPERADAS = {S = {
    1: ["BRA"],
    2: ["N", "NE", "SE", "S", "CO"],
    3: ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"],, "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"],
    4: None  # Para municípios, seria o código IBGE (muito extenso para listar aqui)   4: None  # Para municípios, seria o código IBGE (muito extenso para listar aqui)
}}

# Função para validar formato de datata
def validar_formato_data(data_str):
    formatos_aceitos = ["%Y", "%Y-%m", "%Y-%m-%d"]", "%Y-%m-%d"]
    for formato in formatos_aceitos:ato in formatos_aceitos:
        try:
            time.strptime(data_str, formato)me(data_str, formato)
            return True
        except ValueError:Error:
            continueinue
    return False    return False

# Função para validar período
def validar_periodo(periodo_inicial, periodo_final):dar_periodo(periodo_inicial, periodo_final):
    try:
        formato = "%Y" if len(periodo_inicial) == 4 else "%Y-%m" if len(periodo_inicial) == 7 else "%Y-%m-%d" "%Y-%m" if len(periodo_inicial) == 7 else "%Y-%m-%d"
        inicio = time.strptime(periodo_inicial, formato)mato)
        fim = time.strptime(periodo_final, formato)ime(periodo_final, formato)
        if inicio > fim:
            logging.error("Período inicial deve ser menor ou igual ao período final")ríodo inicial deve ser menor ou igual ao período final")
            return None, Noneone
        return inicio, fim
    except ValueError as e:
        logging.error(f"Erro ao validar períodos: {e}")rro ao validar períodos: {e}")
        return None, None        return None, None

# Função para fazer requisições com tratamento de erro e rate limitingcom tratamento de erro e rate limiting
def get_dados(url, params=None):):
    for tentativa in range(3):ativa in range(3):
        try:
            response = session.get(url, params=params, timeout=10)ams=params, timeout=10)
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 5))
                logging.warning(f"Rate limit atingido. Aguardando {retry_after} segundos...")limit atingido. Aguardando {retry_after} segundos...")
                time.sleep(retry_after)ep(retry_after)
                continue
            elif response.status_code == 404:
                logging.error(f"Série ou recurso não encontrado: {url}")or(f"Série ou recurso não encontrado: {url}")
                return None
            response.raise_for_status()tus()
            data = response.json()nse.json()
            if not data:
                logging.warning(f"Resposta vazia para {url}").warning(f"Resposta vazia para {url}")
            return data
        except requests.exceptions.RequestException as e:
            logging.error(f"Erro ao acessar {url} (tentativa {tentativa+1}/3): {e}")(f"Erro ao acessar {url} (tentativa {tentativa+1}/3): {e}")
            time.sleep(2)e.sleep(2)
    return None    return None

# Função para processar uma série
def processar_serie(serie, abrangencia, periodo_inicial, periodo_final):angencia, periodo_inicial, periodo_final):
    serie_id = serie.get("id")
    if not serie_id or not isinstance(serie_id, int):
        logging.warning(f"Série com ID inválido: {serie}")ning(f"Série com ID inválido: {serie}")
        return None        return None

    logging.info(f"Processando série: {serie.get('titulo', 'Sem título')} (ID: {serie_id})")    logging.info(f"Processando série: {serie.get('titulo', 'Sem título')} (ID: {serie_id})")

    valores = get_dados(
        f"{BASE_URL}/valores-series/{serie_id}/{abrangencia}",
        params={"inicial": periodo_inicial, "final": periodo_final},   params={"inicial": periodo_inicial, "final": periodo_final},
    )    )

    if valores:
        # Validar siglas retornadas
        siglas_retornadas = set(valor.get("sigla") for valor in valores if valor.get("sigla")) in valores if valor.get("sigla"))
        siglas_esperadas = SIGLAS_ESPERADAS.get(abrangencia)rangencia)
        if siglas_esperadas and siglas_retornadas:
            siglas_inesperadas = siglas_retornadas - set(siglas_esperadas)iglas_retornadas - set(siglas_esperadas)
            if siglas_inesperadas:
                logging.warning(f"Siglas inesperadas encontradas para série {serie_id}: {siglas_inesperadas}")                logging.warning(f"Siglas inesperadas encontradas para série {serie_id}: {siglas_inesperadas}")

        # Contar registros por sigla
        contagem_por_sigla = Counter(valor.get("sigla") for valor in valores if valor.get("sigla"))r valor in valores if valor.get("sigla"))
        for sigla, contagem in contagem_por_sigla.items():
            logging.info(f"Série {serie_id} - {sigla}: {contagem} registros")            logging.info(f"Série {serie_id} - {sigla}: {contagem} registros")

        # Aviso sobre qualidade dos dados
        logging.info("Nota: Os dados podem conter inconsistências, como aumento de mortes por causa indeterminada (fonte: Atlas da Violência 2021).")        logging.info("Nota: Os dados podem conter inconsistências, como aumento de mortes por causa indeterminada (fonte: Atlas da Violência 2021).")

        return {
            "serie_id": serie_id,
            "titulo": serie.get("titulo", "Sem título"),t("titulo", "Sem título"),
            "valores": valores   "valores": valores
        }
    else:
        logging.error(f"Erro ao obter valores da série {serie_id} com params: {periodo_inicial}-{periodo_final}")or(f"Erro ao obter valores da série {serie_id} com params: {periodo_inicial}-{periodo_final}")
        return None        return None

# Função para achatar dados
def achatar_dados(dados_consolidados):os(dados_consolidados):
    linhas = []
    for dado in dados_consolidados:
        serie_id = dado.get("serie_id")id")
        titulo = dado.get("titulo")
        valores = dado.get("valores", [])valores = dado.get("valores", [])
        
        for valor in valores:valores:
            linha = {
                "serie_id": serie_id,_id,
                "titulo": titulo,
                "sigla": valor.get("sigla"),a"),
                "ano": valor.get("ano"),
                "valor": valor.get("valor"),   "valor": valor.get("valor"),
            }
            linhas.append(linha)s.append(linha)
    return linhas    return linhas

# Função para salvar dados achatados em CSVos achatados em CSV
def salvar_csv(dados_achatados, caminho)::
    with open(caminho, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["serie_id", "titulo", "sigla", "ano", "valor"])        writer = csv.DictWriter(f, fieldnames=dados_achatados[0].keys())
        writer.writeheader()er()
        writer.writerows(dados_achatados))
    logging.info(f"Dados achatados salvos em {caminho}")

# Função principal
def main(args):
    # Log para confirmar a abrangência usada confirmar a abrangência usada
    logging.info(f"Abrangência selecionada: {args.abrangencia} (1=País, 2=Região, 3=UF, 4=Município)")cípio)")

    # Validar parâmetrosparâmetros
    if not (1 <= args.abrangencia <= 4):    if not (1 <= args.abrangencia <= 4):
        logging.error("Abrangência inválida. Use: 1 (País), 2 (Região), 3 (UF), 4 (Município)"). Use: 1 (País), 2 (Região), 3 (UF), 4 (Município)")
        return
    if not validar_formato_data(args.periodo_inicial) or not validar_formato_data(args.periodo_final):
        logging.error("Períodos devem estar no formato YYYY, YYYY-MM ou YYYY-MM-DD")        logging.error("Períodos devem estar no formato YYYY, YYYY-MM ou YYYY-MM-DD")
        return
    periodo_inicial, periodo_final = validar_periodo(args.periodo_inicial, args.periodo_final)riodo_inicial, args.periodo_final)
    if not periodo_inicial or not periodo_final:    if not periodo_inicial or not periodo_final:
        return

    # Aviso para abrangência 4 (municípios)abrangência 4 (municípios)
    if args.abrangencia == 4:
        logging.warning("Abrangência 4 (Municípios) pode retornar um grande volume de dados. A API não suporta paginação, o que pode causar problemas de desempenho.")g.warning("Abrangência 4 (Municípios) pode retornar um grande volume de dados. A API não suporta paginação, o que pode causar problemas de desempenho.")

    # Criar diretório de saídaída
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    # 1️⃣ Obter Temas Disponíveisoníveis
    temas = get_dados(f"{BASE_URL}/temas")emas")
    if not temas:
        logging.error("Falha ao obter temas. Verifique a conexão ou disponibilidade da API.") ou disponibilidade da API.")
        return

    dados_consolidados = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = []
        for tema in temas:
            tema_id = tema.get("id")tema.get("id")
            if not tema_id or not isinstance(tema_id, int):instance(tema_id, int):
                logging.warning(f"Tema com ID inválido: {tema}")ema com ID inválido: {tema}")
                continue

            logging.info(f"Processando tema: {tema.get('titulo', 'Sem título')}")f"Processando tema: {tema.get('titulo', 'Sem título')}")

            # 2️⃣ Obter Séries do Tema            # 2️⃣ Obter Séries do Tema
            series = get_dados(f"{BASE_URL}/series/{tema_id}")URL}/series/{tema_id}")
            if series:
                for serie in series:for serie in series:
                    futures.append(
                        executor.submit(tor.submit(
                            processar_serie, serie, args.abrangencia, args.periodo_inicial, args.periodo_final.abrangencia, args.periodo_inicial, args.periodo_final
                        )
                    )

        # Aguardar e coletar resultadosesultados
        for future in as_completed(futures):
            try:y:
                resultado = future.result()                resultado = future.result()
                if resultado:f resultado:
                    dados_consolidados.append(resultado)
            except Exception as e:
                logging.error(f"Erro ao processar série: {e}")

    # Após consolidar os dados    if not dados_consolidados:
    if not dados_consolidados:oi coletado.")
        logging.error("Nenhum dado consolidado foi coletado.")
        return

    # Achatar os dados
    dados_achatados = achatar_dados(dados_consolidados)

    # Salvar em JSON (opcional)
    json_path = os.path.join(args.output_dir, "dados_consolidados.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(dados_consolidados, f, ensure_ascii=False, indent=4)
    logging.info(f"Dados salvos em {json_path}")v")

    # Salvar em CSV
    csv_path = os.path.join(args.output_dir, "dados_consolidados.csv")# Configuração de argumentos de linha de comando
    salvar_csv(dados_achatados, csv_path)
rgumentParser(description="Coletor de dados da API do Atlas da Violência (IPEA)")
# Configuração de argumentos de linha de comando
def parse_args():s, 2=Região, 3=UF, 4=Município (padrão: 1)")
    parser = argparse.ArgumentParser(description="Coletor de dados da API do Atlas da Violência (IPEA)")_argument("--periodo-inicial", type=str, default="2010",
    parser.add_argument("--abrangencia", type=int, default=1, choices=[1, 2, 3, 4],          help="Período inicial (formato: YYYY, YYYY-MM ou YYYY-MM-DD, padrão: 2010)")

















    main(args)        return    if not periodo_inicial or not periodo_final:    periodo_inicial, periodo_final = validar_periodo(args.periodo_inicial, args.periodo_final)    args = parse_args()if __name__ == "__main__":    return parser.parse_args()                        help="Diretório de saída para os arquivos (padrão: output)")    parser.add_argument("--output-dir", type=str, default="output",                        help="Número de workers para processamento paralelo (padrão: 5)")    parser.add_argument("--workers", type=int, default=5,                        help="Período final (formato: YYYY, YYYY-MM ou YYYY-MM-DD, padrão: 2023)")    parser.add_argument("--periodo-final", type=str, default="2023",                        help="Período inicial (formato: YYYY, YYYY-MM ou YYYY-MM-DD, padrão: 2010)")    parser.add_argument("--periodo-inicial", type=str, default="2010",                        help="Abrangência: 1=País, 2=Região, 3=UF, 4=Município (padrão: 1)")    parser.add_argument("--periodo-final", type=str, default="2023",
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
        return
    main(args)