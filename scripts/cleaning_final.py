"""Pipeline ETL baseada em regras de negócio para limpeza e transformação.

Realiza o tratamento de nulos, padronização de texto, conversão de datas,
filtragem de limites e resolução de integridade referencial com clientes
órfãos.
"""

import os
import pandas as pd
import x_ray_tabelas_pasta as xray


# ==========================================
# 1. MAPA DE REGRAS DE NEGÓCIO
# ==========================================
REGRAS_NEGOCIO = {
    "customers.csv": {
        "eliminar_nulos": [],
        "preencher_mediana": ["Age"],
        "preencher_valor": {"City": "Não Informado"},
        "padronizar_texto": ["City"],
        "filtrar_limites": {"Age": {"min": 14, "max": 100}},
    },
    "orders.csv": {
        "eliminar_nulos": ["OrderDate"],
        "preencher_mediana": [],
        "preencher_valor": {
            "Quantity": 1,
            "Discount": 0,
            "PaymentMethod": "Desconhecido",
        },
        "padronizar_texto": ["PaymentMethod", "Status"],
        "converter_data": ["OrderDate"],
        "filtrar_limites": {"Quantity": {"min": 1, "max": None}},
    },
    "payments.csv": {
        "eliminar_nulos": ["PaymentDate"],
        "converter_data": ["PaymentDate"],
    },
}


def aplicar_regras_transformacao(df_original, regras):
    """Aplica o conjunto de regras de limpeza e padronização a um DataFrame.

    Args:
        df_original (pandas.DataFrame): O DataFrame original a ser transformado.
        regras (dict): Dicionário contendo as regras a serem aplicadas.

    Returns:
        pandas.DataFrame: O DataFrame limpo e transformado.
    """
    df = df_original.copy()

    if regras.get("converter_data"):
        for col in regras["converter_data"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")

    if regras.get("eliminar_nulos"):
        for col in regras["eliminar_nulos"]:
            if col in df.columns:
                df = df.dropna(subset=[col]).copy()

    if regras.get("preencher_mediana"):
        for col in regras["preencher_mediana"]:
            if col in df.columns:
                df[col] = df[col].fillna(df[col].median())

    if regras.get("preencher_valor"):
        for col, valor in regras["preencher_valor"].items():
            if col in df.columns:
                df[col] = df[col].fillna(valor)

    if regras.get("padronizar_texto"):
        for col in regras["padronizar_texto"]:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().str.title()

    if regras.get("filtrar_limites"):
        for col, limites in regras["filtrar_limites"].items():
            if col in df.columns:
                if limites.get("min") is not None:
                    df = df[df[col] >= limites["min"]].copy()
                if limites.get("max") is not None:
                    df = df[df[col] <= limites["max"]].copy()

    return df.drop_duplicates().copy()


def tratar_integridade_referencial(tabelas_limpas):
    """Identifica clientes órfãos nos pedidos e injeta 'Clientes Fantasma'.

    Args:
        tabelas_limpas (dict): Dicionário contendo os DataFrames já limpos.

    Returns:
        dict: Dicionário atualizado com a integridade referencial ajustada.
    """
    print("\n A verificar Integridade Referencial entre Pedidos e Clientes...")

    df_clientes = tabelas_limpas.get("customers.csv")
    df_pedidos = tabelas_limpas.get("orders.csv")

    if df_clientes is None or df_pedidos is None:
        return tabelas_limpas

    ids_clientes_cadastrados = set(df_clientes["CustomerID"])
    ids_clientes_nas_compras = set(df_pedidos["CustomerID"])

    ids_orfaos = ids_clientes_nas_compras - ids_clientes_cadastrados

    if len(ids_orfaos) > 0:
        print(
            f" Alerta: Foram encontrados {len(ids_orfaos)} IDs de "
            "clientes órfãos (fizeram compras mas não têm cadastro)."
        )

        mediana_idades = df_clientes["Age"].median()
        novos_clientes = [
            {
                "CustomerID": id_orfao,
                "CustomerName": "Cliente Convidado (Ghost)",
                "Age": mediana_idades,
                "City": "Não Informado",
            }
            for id_orfao in ids_orfaos
        ]

        df_fantasmas = pd.DataFrame(novos_clientes)
        df_clientes = pd.concat(
            [df_clientes, df_fantasmas], ignore_index=True
        )
        tabelas_limpas["customers.csv"] = df_clientes

        print(
            " Clientes fantasmas criados e injetados com sucesso! "
            
        )
    else:
        print(
            " A integridade referencial está perfeita. Não há clientes órfãos."
        )

    return tabelas_limpas


def executar_pipeline(pasta_destino="dbset/dados_limpos"):
    """Executa o ciclo completo de ETL: Extração, Transformação e Carga."""
    print("🚀 A iniciar a Pipeline de Transformação Baseada em Regras...")

    os.makedirs(pasta_destino, exist_ok=True)

    # 1. Extração
    tabelas_importadas = xray.carregar_todos_csv("data/ECOMERCE")
    tabelas_limpas = {}

    # 2. Transformação por tabela
    for nome_arquivo, df_original in tabelas_importadas.items():
        if nome_arquivo.startswith("bi_"):
            continue

        regras = REGRAS_NEGOCIO.get(nome_arquivo)
        if regras:
            df_limpo = aplicar_regras_transformacao(df_original, regras)
        else:
            df_limpo = df_original.drop_duplicates().copy()

        tabelas_limpas[nome_arquivo] = df_limpo

    # 3. Tratamento de Integridade Referencial
    tabelas_limpas = tratar_integridade_referencial(tabelas_limpas)

    # 4. Carga / Exportação
    print("\n A exportar ficheiros finais...")
    for nome_arquivo, df_final in tabelas_limpas.items():
        nome_exportacao = f"bi_{nome_arquivo}"
        caminho_completo = os.path.join(pasta_destino, nome_exportacao)

        df_final.to_csv(caminho_completo, index=False, encoding="utf-8-sig")
        print(f" Tratamento concluído: {nome_arquivo} -> {caminho_completo}")

    print(
        "\n✨ Pipeline ETL concluída! Bases prontas para "
        "modelagem sem erros de vazio."
    )


# --- EXECUÇÃO PRINCIPAL ---

if __name__ == "__main__":
    executar_pipeline()