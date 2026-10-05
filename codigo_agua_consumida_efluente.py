import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

linhas_processadas = []

# 1. Leitura e normalização das quebras de linha e delimitadores
with open("efluente_agua_consumida.csv", "r", encoding="cp1252") as f:
    for linha in f:
        linha_limpa = linha.strip()
        if not linha_limpa:
            continue
            
        linha_limpa = linha_limpa.strip('"')
        linha_normalizada = linha_limpa.replace('","', '|').replace('""', '').replace('"', '')
        campos = [campo.strip() for campo in linha_normalizada.split('|')]
        linhas_processadas.append(campos)

max_colunas = max(len(l) for l in linhas_processadas)
linhas_alinhadas = [l + [''] * (max_colunas - len(l)) for l in linhas_processadas]

# 2. Construção do DataFrame
cabecalho = linhas_alinhadas[0]
dados = linhas_alinhadas[1:]

tabela = pd.DataFrame(dados, columns=cabecalho)
tabela.columns = tabela.columns.str.replace('"', '').str.strip()

# 3. Isolamento da coluna Município e descarte do código IBGE
tabela['Município'] = tabela['Município,ibge'].str.split(',').str[0]
tabela = tabela.drop(columns=['Município,ibge'], errors='ignore')

# 4. Simplificação dos cabeçalhos anuais
novos_nomes = {}
for col in tabela.columns:
    if "consumida" in col:
        ano = col.split("consumida")[-1].split("(%)")[0].strip()
        novos_nomes[col] = ano
tabela = tabela.rename(columns=novos_nomes)

anos = [col for col in tabela.columns if col.isdigit()]

# 5. Conversão dos valores para numérico e tratamento de valores nulos
for ano in anos:
    tabela[ano] = tabela[ano].replace('-', np.nan)
    tabela[ano] = tabela[ano].astype(str).str.replace(',', '.')
    tabela[ano] = pd.to_numeric(tabela[ano], errors='coerce')

# 6. Cálculo da média geral estadual
medias_rs = tabela[anos].mean()

# 7. Filtro dos 5 maiores municípios em população
top5_cidades = ['Porto Alegre', 'Caxias do Sul', 'Canoas', 'Pelotas', 'Santa Maria']
df_top5 = tabela[tabela['Município'].isin(top5_cidades)].set_index('Município')

# 8. Renderização do gráfico comparativo
fig, ax = plt.subplots(figsize=(13, 7))

paleta_cores = {
    'Porto Alegre': '#1f77b4',
    'Caxias do Sul': '#2ca02c',
    'Canoas': '#ff7f0e',
    'Pelotas': '#9467bd',
    'Santa Maria': '#8c564b'
}

for cidade in top5_cidades:
    if cidade in df_top5.index:
        ax.plot(
            anos, 
            df_top5.loc[cidade, anos], 
            marker='o', 
            markersize=5,
            linewidth=2.2, 
            label=cidade, 
            color=paleta_cores.get(cidade)
        )

# Traçado da média geral estadual
ax.plot(
    anos, 
    medias_rs.values, 
    color='#111111', 
    linestyle='--', 
    linewidth=2.5, 
    label='Média Geral RS (todos os municípios)',
    zorder=5
)

# 9. Configurações visuais e eixos com especificação clara da razão percentual
ax.set_title(
    'Proporção de Efluente Tratado em Relação ao Volume de Água Consumida (%)\n'
    'Top 5 Cidades vs. Média Estadual do RS (1998–2022)', 
    fontsize=13, 
    fontweight='bold', 
    pad=15
)

ax.set_xlabel('Ano de Referência', fontsize=11, labelpad=8)
ax.set_ylabel('Razão: Volume Tratado / Volume Consumido (%)', fontsize=11, labelpad=8)
ax.set_ylim(-2, 105)
ax.tick_params(axis='x', rotation=45)
ax.grid(True, linestyle='--', alpha=0.5)
ax.legend(loc='upper left', frameon=True, facecolor='white', framealpha=0.9, fontsize=10)

# 10. Créditos padronizados de Fonte e Autor
plt.figtext(
    0.06, 0.01, 
    "Fonte: Portal Dados RS — SPGG/DEE (Saneamento - Esgoto - Tratamento)", 
    fontsize=9, 
    fontstyle='italic', 
    color='#444444', 
    ha='left'
)

plt.figtext(
    0.94, 0.01, 
    "Autor: Gabriel Siqueira dos Santos", 
    fontsize=9, 
    fontweight='bold', 
    color='#222222', 
    ha='right'
)

plt.subplots_adjust(bottom=0.12)

# Exportação do arquivo em alta resolução e visualização
plt.savefig('top5_cidades_esgoto_RS.png', dpi=300, bbox_inches='tight')
print("Gráfico das 5 principais cidades salvo com sucesso como 'top5_cidades_esgoto_RS.png'.")
plt.show()

# 11. Sumário de conferência no terminal
print("\nMédia do período (1998–2022) por município:")
print(df_top5[anos].mean(axis=1).round(2).sort_values(ascending=False))
print(f"\nMédia histórica geral de todo o RS: {medias_rs.mean():.2f}%")

#FIM DO SCRIPT
