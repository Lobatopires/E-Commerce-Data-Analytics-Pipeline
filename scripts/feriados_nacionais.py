import pandas as pd
import requests

def extrair_feriados(ano, codigo_pais):
    """
    Função que faz o pedido à API de feriados e devolve um DataFrame.
    """
    # Endpoint da API pública
    url = f"https://date.nager.at/api/v3/PublicHolidays/{ano}/{codigo_pais}"
    
    # Fazer a chamada HTTP (o equivalente a abrir a página no navegador)
    resposta = requests.get(url)
    
    # Verificar se o servidor respondeu com sucesso (Código 200 = OK)
    if resposta.status_code == 200:
        # Converter a resposta JSON bruta numa Tabela do Pandas
        dados = resposta.json()
        df = pd.DataFrame(dados)
        
        # Selecionar e renomear as colunas que interessam ao negócio
        df_limpo = df[['date', 'localName']].rename(columns={
            'date': 'Data', 
            'localName': 'Nome_Feriado'
        })
        return df_limpo
    else:
        print(f" Erro na API para o ano {ano}. Código: {resposta.status_code}")
        return pd.DataFrame()

print(" A iniciar a Pipeline de Feriados (API)...")

# 1. EXTRACT (Extrair)
# Vamos buscar os feriados de Portugal ('PT') para os anos que cobrem os seus dados
print("A extrair dados de 2024, 2025 e 2026...")
feriados_2024 = extrair_feriados(2024, 'PT')
feriados_2025 = extrair_feriados(2025, 'PT')
feriados_2026 = extrair_feriados(2026, 'PT')

# 2. TRANSFORM (Transformar)
# Unir todos os anos numa única tabela vertical e tipar a coluna de datas
df_calendario_feriados = pd.concat([feriados_2024, feriados_2025, feriados_2026], ignore_index=True)
df_calendario_feriados['Data'] = pd.to_datetime(df_calendario_feriados['Data'])

# 3. LOAD (Carregar)
# Exportar a tabela limpa para a mesma pasta dos seus dados
nome_ficheiro = 'data/ECOMERCE/feriados_nacionais.csv'
df_calendario_feriados.to_csv(nome_ficheiro, index=False, encoding='utf-8')

print(f" Pipeline concluída com sucesso! Ficheiro '{nome_ficheiro}' gerado com {df_calendario_feriados.shape[0]} feriados.")
