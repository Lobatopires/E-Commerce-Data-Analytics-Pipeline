"""Módulo para conversão, carregamento e análise de ficheiros Excel e CSV."""

import glob
import os
import pandas as pd


def converter_excel_para_csv(pasta_alvo):
    """Procura ficheiros Excel (.xlsx, .xls) na pasta alvo e converte-os em CSV.

    Args:
        pasta_alvo (str): O caminho da pasta onde estão os ficheiros Excel.
    """
    caminho_pesquisa = os.path.join(pasta_alvo, "*.xls*")
    ficheiros_excel = glob.glob(caminho_pesquisa)

    for ficheiro in ficheiros_excel:
        # Extrai apenas o nome sem a extensão (ex: 'Vendas.xlsx' -> 'Vendas')
        nome_sem_extensao = os.path.splitext(os.path.basename(ficheiro))[0]
        caminho_csv = os.path.join(pasta_alvo, f"{nome_sem_extensao}.csv")

        # Lê a primeira folha do Excel e exporta como CSV
        df = pd.read_excel(ficheiro)
        df.to_csv(caminho_csv, index=False, encoding="utf-8")
        print(
            f"Convertido: {os.path.basename(ficheiro)} -> {nome_sem_extensao}.csv"
        )


def carregar_todos_csv(pasta_alvo):
    """Carrega todos os ficheiros .csv de uma pasta para um dicionário de DataFrames.

    Args:
        pasta_alvo (str): O diretório onde se encontram os ficheiros CSV.

    Returns:
        dict: Dicionário contendo o nome do ficheiro como chave e o DataFrame
            como valor.
    """
    caminho_pesquisa = os.path.join(pasta_alvo, "*.csv")
    ficheiros_encontrados = glob.glob(caminho_pesquisa)

    tabelas = {}
    for ficheiro in ficheiros_encontrados:
        nome_arquivo = os.path.basename(ficheiro)
        df_temp = pd.read_csv(ficheiro)

        # Limpeza automática: Remove colunas fantasmas (ex: 'Unnamed: 13')
        df_temp = df_temp.loc[:, ~df_temp.columns.str.contains("^Unnamed")]

        tabelas[nome_arquivo] = df_temp

    return tabelas


def analisar_tabela(nome, df, chave_primaria):
    """Imprime uma análise descritiva do DataFrame (linhas, colunas, chaves e nulos).

    Args:
        nome (str): Nome de identificação da tabela.
        df (pandas.DataFrame): O DataFrame a ser analisado.
        chave_primaria (str): O nome da coluna usada como chave primária.
    """
    print(f"\n=== ANÁLISE DA TABELA: {nome.upper()} ===")
    print(f"Total de registos (linhas): {df.shape[0]}")
    print(f"Total de colunas: {df.shape[1]}")

    # Verificação da integridade das chaves primárias
    if chave_primaria == "Desconhecida":
        print(
            "Nenhuma coluna de ID detetada. Análise de chaves duplicadas"
            " ignorada."
        )
    elif chave_primaria in df.columns:
        duplicados_chave = df[chave_primaria].duplicated().sum()
        print(f"IDs duplicados na chave '{chave_primaria}': {duplicados_chave}")
    else:
        print(f"A coluna '{chave_primaria}' não existe nesta tabela.")

    # Verificação e cálculo percentual de valores nulos
    nulos = df.isnull().sum()
    nulos_com_dados = nulos[nulos > 0]

    if not nulos_com_dados.empty:
        print("Valores nulos encontrados:")
        for col, qtd in nulos_com_dados.items():
            pct = (qtd / len(df)) * 100
            print(f"  - Coluna '{col}': {qtd} nulos ({pct:.2f}%)")
    else:
        print("Nenhum valor nulo detetado!")


def analise_file(dados):
    """Percorre um dicionário de DataFrames e executa a análise em cada um.

    A função tenta identificar automaticamente a primeira coluna que contém 'ID'
    para usá-la como chave primária.

    Args:
        dados (dict): Dicionário com nomes de ficheiros e seus respetivos
            DataFrames.
    """
    for nome_arquivo, df in dados.items():
        # Limpar o nome para o título (Ex: 'customers.csv' -> 'Customers')
        nome_limpo = nome_arquivo.split(".")[0].capitalize()

        # Procura a primeira coluna cujo nome contenha 'ID' (case-insensitive)
        colunas_id = [col for col in df.columns if "id" in col.lower()]

        # Define a chave adivinhada caso encontre alguma coluna correspondente
        chave_adivinhada = colunas_id[0] if colunas_id else "Desconhecida"

        # Executa a análise para o DataFrame atual
        analisar_tabela(nome_limpo, df, chave_adivinhada)


# --- EXECUÇÃO DO SCRIPT ---

if __name__ == "__main__":
    # 1. Converter ficheiros Excel para CSV na pasta './ECOMERCE/'
    converter_excel_para_csv("data/ECOMERCE")

    # 2. Carregar todos os ficheiros CSV da pasta './ECOMERCE/'
    dados_pasta = carregar_todos_csv("data/ECOMERCE")

    # 3. Executar análise dinâmica sobre os dados carregados
    analise_file(dados_pasta)