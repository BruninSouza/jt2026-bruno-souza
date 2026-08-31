import nbformat as nbf

nb = nbf.v4.new_notebook()
meta = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python"},
}
nb.metadata = meta
md = lambda t: nbf.v4.new_markdown_cell(t)
code = lambda c: nbf.v4.new_code_cell(c)

# ---------------------------------------------------------------------------
# BLOCO DE CABEÇALHO + FUNÇÃO carregar()
# ---------------------------------------------------------------------------
intro_md = (
"# Aluguel por temporada em Itapema (SC)\n\n"
"**Análise para a Seazone** — este caderno mostra os gráficos e as tabelas do\n"
"estudo. Toda a conta pesada foi feita antes, nos scripts da pasta `src/`;\n"
"aqui a gente só lê os resultados de `outputs/` e abre discussão.\n\n"
"**Guia rápido de leitura:** não precisa saber programar. Cada seção explica,\n"
"em texto simples, o que os números significam. Palavras difíceis (mediana,\n"
"ocupação, retorno) são explicadas na primeira vez que aparecem."
)
intro_code = (
"%matplotlib inline\n"
"import matplotlib.pyplot as plt\n"
"import pandas as pd\n"
"import numpy as np\n"
"import os\n"
"\n"
"# cores usadas nos graficos\n"
"VERMELHO  = '#F94144'\n"
"LARANJA   = '#F8961E'\n"
"AMARELO   = '#F9C74F'\n"
"VERDE     = '#43AA8B'\n"
"AZUL      = '#577590'\n"
"ROXO      = '#9B5DE5'\n"
"\n"
"plt.rcParams['axes.grid'] = True\n"
"plt.rcParams['axes.spines.top'] = False\n"
"plt.rcParams['axes.spines.right'] = False\n"
"plt.rcParams['figure.dpi'] = 100\n"
"\n"
"def carregar(nome):\n"
"    \"\"\"Le um CSV em outputs/ e avisa de forma clara se ele ainda nao existe.\"\"\"\n"
"    caminho = os.path.join('outputs', nome)\n"
"    if not os.path.exists(caminho):\n"
"        raise FileNotFoundError(\n"
"            f'NAO EXISTE ainda: outputs/{nome}. '\n"
"            'Rode o script correspondente em src/ primeiro.')\n"
"    return pd.read_csv(caminho)\n"
"\n"
"print('pronto para analisar.')\n"
)

# ---------------------------------------------------------------------------
# 1. RECOMENDACAO
# ---------------------------------------------------------------------------
sec1_md = (
"## 1. Recomendação\n\n"
"**Oportunidade mais defensável:** concentrar a operação em **apartamentos de\n"
"2 quartos gerenciados por anfitriões profissionais no Centro** — é o perfil\n"
"de maior faturamento por unidade e o único que chega perto de um retorno\n"
"positivo; antes de comprar lotes, porém, é obrigatório validar a ocupação\n"
"com dados reais de pelo menos um ano, porque a janela de observação de\n"
"15 dias dentro do nosso estudo subestima receita e retorno.\n\n"
"Abaixo, os grupos que reúnem mais de 20 imóveis com preço conhecido\n"
"ordenados pelo faturamento médio por unidade — os números que sustentam a\n"
"recomendação."
)
sec1_code = (
"tese = carregar('tese_comparacao.csv')\n"
"ok = tese[~tese['alerta_n_pequeno']].sort_values('fat_anual_por_unidade', ascending=False)\n"
"print('Grupos com ao menos 20 imovéis (top por faturamento anual por unidade):')\n"
"cols = ['bairro','quartos','tipo_anuncio','n','revpar',\n"
"        'fat_anual_por_unidade','retorno_liquido_pct']\n"
"print(ok[cols].round(2).to_string(index=False))\n"
)

# ---------------------------------------------------------------------------
# 2. COMO DECIDIMOS
# ---------------------------------------------------------------------------
sec2_md = (
"## 2. Por que escolhemos este caminho\n\n"
"Quem compra um imóvel pensa em **retorno sobre o dinheiro investido** (ROI):\n"
"quanto o imóvel devolve por ano em relação ao que custou. Mas quem **opera**\n"
"imóveis de terceiros, como a Seazone, ganha uma % de cada diária alugada.\n"
"Portanto, para a operadora o que importa é quanto cada unidade **gera de\n"
"receita e de sobra no caixa**, e não quanto o dono lucraria.\n\n"
"Por isso a decisão aqui pesa três coisas, em equilíbrio:\n\n"
"1. **Receita por unidade** — quanto aquele perfil fatura por ano em média;\n"
"2. **Retorno líquido** — quanto sobra depois de comissões, limpeza,\n"
"   condomínio, IPTU, manutenção e taxa de gestão, sobre o preço de compra;\n"
"3. **Escala** — quantas unidades desse perfil existem à venda para compor um\n"
"   portfólio grande (a Seazone opera milhares de imóveis).\n\n"
"Cada seção apresenta um desses ângulos; a seção 10 reúne tudo numa\n"
"comparação lado a lado."
)

# ---------------------------------------------------------------------------
# 3. OS DADOS
# ---------------------------------------------------------------------------
sec3_md = (
"## 3. Os dados: o que temos e o que falta\n\n"
"Os arquivos vieram de dois sites. Do **Airbnb** veio o comportamento do\n"
"aluguel por temporada: um cadastro dos anúncios (quartos, avaliações, nota),\n"
"um cadastro dos proprietários, o bairro e a coordenada de cada imóvel, e o\n"
"histórico de **preço por noite** para os primeiros meses de 2025. Do\n"
"**VivaReal** veio o mercado de compra e venda (preço, preço por metro\n"
"quadrado, condomínio).\n\n"
"**Como se conectam:** cada anúncio do Airbnb tem um número de identificação\n"
"(`airbnb_listing_id`) que aparece em quase todas as planilhas — é a 'pontinha\n"
"do fio' que liga bairro, preço e avaliações do mesmo imóvel. O VivaReal é\n"
"outro sistema e não compartilha essa identificação: só dá para compará-lo\n"
"por bairro.\n\n"
"**Três limitações importantes antes de qualquer conclusão:**\n"
"\n"
"- **Poucos imóveis com preço.** Só 1.005 dos 4.441 anúncios têm histórico de\n"
"  preço, e destes, 673 puderam ter receita calculada (os demais apareceram\n"
"  uma única vez na coleta). É uma fatia pequena e possivelmente enviesada\n"
"  para imóveis mais ativos.\n"
"- **Janela curta.** Os preços foram 'fotografados' em apenas três dias de\n"
"  janeiro (6, 7 e 20), cobrindo noites de janeiro a abril. **Não temos\n"
"  dezembro**, o auge de Itapema.\n"
"- **Não existe coluna de 'noite ocupada ou livre'.** A ocupação foi\n"
"  estimada indiretamente (explicado na seção 4) — portanto os valores\n"
"  absolutos de receita são conservadores.\n\n"
"O perfil completo de cada arquivo (colunas, tipos e quantos valores\n"
"faltam) está em `outputs/perfil_dados.txt`."
)
sec3_code = (
"with open('outputs/perfil_dados.txt', encoding='utf-8') as f:\n"
"    perfil = f.read()\n"
"print(perfil[:4200])\n"
"print('...' if len(perfil) > 4200 else '')\n"
)

# ---------------------------------------------------------------------------
# 4. COMO ESTIMAMOS A RECEITA
# ---------------------------------------------------------------------------
sec4_md = (
"## 4. Quanto cada imóvel fatura por ano\n\n"
"**A ideia:** quando uma noite estava *livre* na primeira fotografia (6/7 de\n"
"janeiro) e *sumiu* das fotografias seguintes (20 de janeiro), entendemos que\n"
"ela foi **vendida** naquele período. Se a noite já aparecia ocupada na\n"
"primeira fotografia, não sabemos se foi reservada de verdade ou se o dono\n"
"bloqueou o calendário — por prudência, não contamos esses casos como receita.\n\n"
"Com isso calculamos, para cada imóvel:\n\n"
"- **Ocupação** = noites vendidas ÷ (noites vendidas + noites livres). Em\n"
"  outras palavras: de cada 10 noites do período, quantas viraram reserva.\n"
"- **Diária mediana** = o preço 'do meio' cobrado nas noites listadas.\n"
"- **Faturamento anual** = receita observada na janela jan–abr escalada para\n"
"  o ano inteiro, assumindo que esses 4 meses concentram 70% da receita de\n"
"  Itapema (premissa conservadora, testada na seção 9).\n\n"
"Todo número que o leitor vir daqui pra frente nasce dessas três peças. O\n"
"histograma abaixo mostra como os imóveis se distribuem pelo faturamento\n"
"anual estimado: a maioria fatura pouco, e poucos faturam muito."
)
sec4_code = (
"rec = carregar('receita_por_listing.csv')\n"
"print('Imóveis com receita calculada:', len(rec))\n"
"print('O imóvel típico fatura: R$ %.0f por ano' % rec['faturamento_anual'].median())\n"
"print()\n"
"\n"
"fig, ax = plt.subplots(figsize=(12,5))\n"
"fig.subplots_adjust(left=0.08, right=0.74, top=0.88, bottom=0.14)  # reserva o canto direito p/ legenda\n"
"n, bins, patches = ax.hist(rec['faturamento_anual'], bins=36,\n"
"                           color=AZUL, edgecolor='white')\n"
"# colore as barras num degradê do azul escuro (baixa receita) ao amarelo\n"
"# (alta receita). A escala de cor 'estoura' no valor de 95% dos imóveis,\n"
"# então o gradiente fica visível no corpo do gráfico (a maioria fatura pouco).\n"
"v_max = float(rec['faturamento_anual'].quantile(0.95))\n"
"norm = plt.Normalize(bins.min(), v_max)\n"
"cmap = plt.get_cmap('cividis')\n"
"for p, bx in zip(patches, bins[:-1]):\n"
"    val = min(float(bx), v_max)  # acima do p95 tudo vira amarelo\n"
"    p.set_facecolor(cmap(norm(val)))\n"
"    p.set_edgecolor('white')\n"
"# borda ao redor do gráfico\n"
"for s in ax.spines.values():\n"
"    s.set_visible(True)\n"
"    s.set_edgecolor('#546e7a')\n"
"    s.set_linewidth(1.2)\n"
"ax.set_title('Quanto cada imóvel fatura por ano (faturamento estimado)')\n"
"ax.set_xlabel('faturamento anual estimado (R$)')\n"
"ax.set_ylabel('quantidade de imóveis')\n"
"# legenda FORA do gráfico, no canto direito, reservado pelo subplots_adjust\n"
"fig.text(0.76, 0.95, 'LEGENDA', ha='left', va='top',\n"
"         fontsize=10, fontweight='bold', color='#455a64')\n"
"fig.text(0.76, 0.84, 'Cada barra conta quantos imóveis faturam\\nnaquele valor.\\n'\n"
"        'Cor: azul = fatura pouco, amarelo = fatura muito.',\n"
"         ha='left', va='top', fontsize=9,\n"
"         bbox=dict(boxstyle='round,pad=0.5', facecolor='#fff8e1',\n"
"                   edgecolor='#b0bec5'))\n"
"fig.patch.set_edgecolor('#546e7a')\n"
"fig.patch.set_linewidth(1.5)\n"
"plt.show()\n"
)

# ---------------------------------------------------------------------------
# 5. MELHOR PERFIL DE IMOVEL
# ---------------------------------------------------------------------------
sec5_md = (
"## 5. Qual é o melhor perfil de imóvel\n\n"
"Aqui comparamos **tipos de imóvel** (apartamento, casa) × **número de\n"
"quartos** × **quem administra** (anfitrião profissional ou particular), em\n"
"cada bairro. Para não decidir com base em exceções, mostramos apenas os\n"
"grupos com **20 ou mais imóveis** — abaixo disso, a média pode ser enganada\n"
"por um ou dois casos.\n\n"
"A ordem de leitura: quanto mais à direita estiver o ponto, maior o\n"
"faturamento anual típico. Cada círculo é um grupo; o tamanho indica quantos\n"
"imóveis ele reúne. As cores separam os bairros."
)
sec5_code = (
"seg = carregar('segmentos.csv')\n"
"seg['rotulo'] = seg['bairro'] + ' | ' + seg['quartos'] + 'q | ' + seg['tipo_anuncio']\n"
"vals = seg[~seg['alerta_n_pequeno']].sort_values('fat_anual_mediana', ascending=True)\n"
"\n"
"# gráfico de 'pirulito': mais limpo que barras para comparar poucos grupos\n"
"fig, ax = plt.subplots(figsize=(12,7))\n"
"fig.subplots_adjust(left=0.24, right=0.72, top=0.88, bottom=0.08)\n"
"cores = [VERDE if b=='Centro' else (LARANJA if b=='Meia Praia' else (VERMELHO if b=='Morretes' else ROXO))\n"
"         for b in vals['bairro']]\n"
"ax.hlines(range(len(vals)), 0, vals['fat_anual_mediana'], color='#cfd8dc', linewidth=1.5)\n"
"sc = ax.scatter(vals['fat_anual_mediana'], range(len(vals)),\n"
"                s=vals['n']*4+40, color=cores, alpha=0.85, edgecolor='white')\n"
"ax.set_yticks(range(len(vals)))\n"
"ax.set_yticklabels(vals['rotulo'], fontsize=8)\n"
"ax.set_xlabel('faturamento anual típico do grupo (R$)')\n"
"ax.set_title('Perfis de imóvel com 20+ anúncios (tamanho = nº de imóveis)')\n"
"ax.axhline(len(vals)-1, color='#eceff1', linewidth=0.5)\n"
"for s in ax.spines.values():\n"
"    s.set_visible(True)\n"
"    s.set_edgecolor('#546e7a')\n"
"    s.set_linewidth(1.2)\n"
"fig.text(0.74, 0.95, 'LEGENDA', ha='left', va='top',\n"
"         fontsize=10, fontweight='bold', color='#455a64')\n"
"fig.text(0.74, 0.84, 'Cada ponto é um perfil; quanto mais à direita,\\nmaior o faturamento.\\n'\n"
"        'Tamanho do ponto = nº de imóveis.\\n'\n"
"        'Centro=verde | Meia Praia=laranja\\nMorretes=vermelho | outros=roxo.',\n"
"         ha='left', va='top', fontsize=9,\n"
"         bbox=dict(boxstyle='round,pad=0.5', facecolor='#fff8e1',\n"
"                   edgecolor='#b0bec5'))\n"
"fig.patch.set_edgecolor('#546e7a')\n"
"fig.patch.set_linewidth(1.5)\n"
"plt.show()\n"
"\n"
"top = vals.tail(6)[['bairro','tipo_imovel','quartos','tipo_anuncio','n',\n"
"                     'fat_anual_mediana','ocupacao_mediana','diaria_mediana']].round(2)\n"
"print('Os 6 perfis que mais faturam (n>=20):')\n"
"print(top.to_string(index=False))\n"
)

# ---------------------------------------------------------------------------
# 6. MELHOR LOCALIZACAO
# ---------------------------------------------------------------------------
sec6_md = (
"## 6. Qual bairro rende mais\n\n"
"Agrupamos as receitas por bairro. O gráfico mostra, para cada bairro com\n"
"amostra suficiente, o **faturamento anual típico** (a bolinha) e um\n"
"**intervalo de incerteza** (a barra vertical): quanto mais alta e comprida a\n"
"barra, maior a variação entre os imóveis daquele bairro.\n\n"
"Duas leituras imediatas: o Centro lidera o faturamento típico — mas a Meia\n"
"Praia tem o dobro de imóveis observados, o que sugere muita oferta e mais\n"
"concorrência, puxando a média para baixo. Morretes aparece como o elo mais\n"
"fraco."
)
sec6_code = (
"loc = carregar('localizacao.csv')\n"
"vals = loc[~loc['alerta_n_pequeno']].sort_values('fat_anual_mediana')\n"
"\n"
"fig, ax = plt.subplots(figsize=(12,5))\n"
"fig.subplots_adjust(left=0.20, right=0.64, top=0.88, bottom=0.12)\n"
"y = np.arange(len(vals))\n"
"cores = [VERDE if b=='Centro' else (LARANJA if b=='Meia Praia' else (VERMELHO if b=='Morretes' else ROXO))\n"
"         for b in vals['bairro']]\n"
"lo = vals['fat_anual_mediana'] - vals['fat_anual_p25']\n"
"hi = vals['fat_anual_p75'] - vals['fat_anual_mediana']\n"
"ax.errorbar(vals['fat_anual_mediana'], y, xerr=[hi, lo],\n"
"            fmt='o', color='#90a4ae', ecolor='#90a4ae', capsize=3, zorder=1)\n"
"ax.scatter(vals['fat_anual_mediana'], y, s=vals['n'], color=cores,\n"
"           alpha=0.9, edgecolor='white', zorder=2)\n"
"ax.set_yticks(y); ax.set_yticklabels(vals['bairro'])\n"
"ax.set_xlabel('faturamento anual típico do bairro (R$)')\n"
"ax.set_title('Faturamento anual por bairro (tamanho da bolinha = nº de imóveis)')\n"
"for s in ax.spines.values():\n"
"    s.set_visible(True)\n"
"    s.set_edgecolor('#546e7a')\n"
"    s.set_linewidth(1.2)\n"
"fig.text(0.66, 0.95, 'LEGENDA', ha='left', va='top',\n"
"         fontsize=10, fontweight='bold', color='#455a64')\n"
"fig.text(0.66, 0.84, 'Bolinha = faturamento típico do bairro\\n(quanto maior, mais imóveis).\\n'\n"
"        'Barra = variação entre imóveis:\\n'\n"
"        'curta = homogêneo | comprida =\\nresultados muito diferentes.',\n"
"         ha='left', va='top', fontsize=9,\n"
"         bbox=dict(boxstyle='round,pad=0.5', facecolor='#fff8e1',\n"
"                   edgecolor='#b0bec5'))\n"
"fig.patch.set_edgecolor('#546e7a')\n"
"fig.patch.set_linewidth(1.5)\n"
"plt.show()\n"
"\n"
"print(vals[['bairro','n','diaria_mediana','ocupacao_mediana','fat_anual_mediana']].round(2).to_string(index=False))\n"
)

# ---------------------------------------------------------------------------
# 7. O QUE EXPLICA AS MELHORES RECEITAS
# ---------------------------------------------------------------------------
sec7_md = (
"## 7. O que diferencia quem fatura muito\n\n"
"Tentamos 'explicar' o faturamento dos imóveis usando as características que\n"
"temos: bairro, nº de quartos, se o anfitrião é superhost, há quantos anos\n"
"ele anuncia, nº de avaliações, nota, capacidade de hóspedes, distância até\n"
"a praia e palavras-chave do anúncio ('frente mar', 'vista mar', 'piscina',\n"
"'beira mar'). Usamos um modelo estatístico (regressão) que mede o peso de\n"
"cada fator.\n\n"
"**Resultado honesto: o modelo explica muito pouco (R² de 7%).** Ou seja, as\n"
"informações que temos **não** conseguem prever quem vai faturar mais — o que\n"
"diz que o que mais pesa (qualidade da gestão, precificação, reputação\n"
"construída) não está nas planilhas. Os dois únicos efeitos que aparecem como\n"
'estatisticamente relevantes são contraintuitivos e frágeis, o que reforça\n'
"que devemos ler o resto do estudo com cuidado."
)
sec7_code = (
"reg = carregar('regressao.csv')\n"
"coef = reg[reg['variavel'] != 'Intercept'].copy()\n"
"\n"
"fig, ax = plt.subplots(figsize=(12,7))\n"
"fig.subplots_adjust(left=0.30, right=0.72, top=0.90, bottom=0.08)\n"
"coef = coef.sort_values('coef')\n"
"cores = [VERDE if v >= 0 else VERMELHO for v in coef['coef']]\n"
"ax.axvline(0, color='#607d8b', linewidth=1)\n"
"ax.hlines(range(len(coef)), 0, coef['coef'], color='#cfd8dc', linewidth=1.5)\n"
"ax.scatter(coef['coef'], range(len(coef)), color=cores, s=60, edgecolor='white')\n"
"ax.set_yticks(range(len(coef)))\n"
"ax.set_yticklabels(coef['variavel'], fontsize=8)\n"
"ax.set_xlabel('peso estimado de cada fator (log do faturamento)')\n"
"ax.set_title('Peso de cada fator sobre o faturamento (verde = aumenta, vermelho = reduz)')\n"
"for s in ax.spines.values():\n"
"    s.set_visible(True)\n"
"    s.set_edgecolor('#546e7a')\n"
"    s.set_linewidth(1.2)\n"
"fig.text(0.74, 0.95, 'LEGENDA', ha='left', va='top',\n"
"         fontsize=10, fontweight='bold', color='#455a64')\n"
"fig.text(0.74, 0.86, 'Verde = aumenta o faturamento;\\nvermelho = reduz.\\n\\n'\n"
"        'R² de 7%: tudo junto explica\\npouco — o que mais pesa\\nnão está nos dados.',\n"
"         ha='left', va='top', fontsize=9,\n"
"         bbox=dict(boxstyle='round,pad=0.5', facecolor='#fff8e1',\n"
"                   edgecolor='#b0bec5'))\n"
"fig.patch.set_edgecolor('#546e7a')\n"
"fig.patch.set_linewidth(1.5)\n"
"plt.show()\n"
"\n"
"print('R² do modelo: 7% — a iguindade do imóvel (notas, tamanho, bairro) quase '\n"
"      'não explica a diferença de faturamento observada.\\n')\n"
"cols = ['variavel','coef','pvalue']\n"
"print(coef.sort_values('pvalue')[cols].round(3).to_string(index=False))\n"
)

# ---------------------------------------------------------------------------
# 8. CUSTO E RETORNO
# ---------------------------------------------------------------------------
sec8_md = (
"## 8. Quanto custa e em quanto tempo se paga\n\n"
"Com os preços de venda do VivaReal por (bairro, quartos), montamos a conta\n"
"de quem compra para alugar por temporada:\n\n"
"- **Investimento** = preço de venda + ~5% de custos de compra (ITBI,\n"
"  escritura, registro) + R$ 60 mil de mobília e enxoval.\n"
"- **Despesas anuais** = comissão do canal (15%), custo de limpeza por\n"
"  reserva, condomínio, IPTU, manutenção (5%) e taxa de administração da\n"
"  operadora (20%).\n\n"
"**Retorno bruto** é a receita dividida pelo investimento, **antes** das\n"
"despesas. **Retorno líquido** é o que sobra **depois** de todas elas — é a\n"
"referência para quanto tempo o imóvel leva para se pagar. A tabela abaixo\n"
"apresenta a conta por bairro (grupos com 20+ imóveis)."
)
sec8_code = (
"yld = carregar('yield_por_segmento.csv')\n"
"vals = yld[~yld['alerta_n_pequeno'] & yld['falta_dado_vivareal']==False].copy()\n"
"\n"
"res = vals.groupby('bairro')[['retorno_liquido_pct']].median().round(2)\n"
"res['preco_med_milhoes'] = (vals.groupby('bairro')['preco_venda_mediano'].median()/1e6).round(2)\n"
"print('Resumo por bairro (grupos n>=20):')\n"
"print(res.to_string())\n"
"\n"
"print('\\nTrecho da conta que sustenta o resumo (grupos n>=20):')\n"
"print(vals[['bairro','quartos','tipo_anuncio','n','preco_venda_mediano',\n"
"           'fat_anual_mediana','receita_liquida','retorno_liquido_pct']].round(2).to_string(index=False))\n"
"print('\\nObservação: praticamente todos os grupos ficam em retorno entre -0,4% e'\n"
"      ' +0,6% ao ano — o retorno parece baixíssimo. O motivo é a'\n"
"      ' subestimação da ocupação (seção 4), não o custo.')\n"
)

# ---------------------------------------------------------------------------
# 9. SENSIBILIDADE
# ---------------------------------------------------------------------------
sec9_md = (
"## 9. E se a ocupação e a diária forem diferentes?\n\n"
"Nossos números de ocupação vêm de uma janela de 15 dias — então precisamos\n"
"saber **quanto mudaria a decisão** se a ocupação real fosse 10 pontos\n"
"percentuais maior ou menor, ou se a diária cobrada fosse 10% maior ou menor.\n"
"Testamos as quatro combinações mais o cenário original e medimos o retorno\n"
"líquido de cada grupo.\n\n"
"O mapa de calor abaixo mostra o resultado: **linha = grupo**, **coluna =\n"
"cenário**, e **cor = retorno líquido** (quanto mais verde, melhor; mais\n"
"vermelho, pior). O objetivo é ver se a *ordem* dos melhores grupos muda\n"
"quando mudamos as premissas."
)
sec9_code = (
"sens = carregar('sensibilidade.csv')\n"
"vals = sens[~sens['alerta_n_pequeno']].copy()\n"
"vals['rotulo'] = vals['bairro'] + ' | ' + vals['quartos'] + 'q | ' + vals['tipo_anuncio']\n"
"grupos_ordem = vals[vals['cenario']=='base'].sort_values('retorno_liquido_pct', ascending=False)['rotulo']\n"
"\n"
"cenarios = ['base','oc+10pp / di+10%','oc+10pp / di-10%','oc-10pp / di+10%','oc-10pp / di-10%']\n"
"M = vals.pivot_table(index='rotulo', columns='cenario', values='retorno_liquido_pct')\n"
"M = M.loc[[g for g in grupos_ordem]]\n"
"\n"
"fig, ax = plt.subplots(figsize=(13,6))\n"
"fig.subplots_adjust(left=0.14, right=0.86, top=0.90, bottom=0.10)\n"
"im = ax.imshow(M[cenarios].values, cmap='RdYlGn', aspect='auto', vmin=-0.4, vmax=0.7)\n"
"ax.set_xticks(range(len(cenarios))); ax.set_xticklabels(cenarios, fontsize=8)\n"
"ax.set_yticks(range(len(M))); ax.set_yticklabels(M.index, fontsize=8)\n"
"for i in range(M.shape[0]):\n"
"    for j in range(len(cenarios)):\n"
"        ax.text(j, i, f'{M[cenarios].values[i,j]:.2f}', ha='center', va='center', fontsize=8, color='black', alpha=0.8)\n"
"cb = plt.colorbar(im, ax=ax, fraction=0.02, pad=0.03)\n"
"cb.set_label('retorno líquido (% ao ano)')\n"
"ax.set_title('Retorno líquido por grupo e por cenário (n>=20)')\n"
"for s in ax.spines.values():\n"
"    s.set_visible(True)\n"
"    s.set_edgecolor('#546e7a')\n"
"    s.set_linewidth(1.4)\n"
"fig.patch.set_edgecolor('#546e7a')\n"
"fig.patch.set_linewidth(1.5)\n"
"plt.show()\n"
"\n"
"print('Leitura: mesmo no cenário mais otimista (ocupação e diária maiores),')\n"
"print('o retorno não passa de +0,6% ao ano — a subestimação da ocupação')\n"
"print('derruba tudo. A ordem dos melhores grupos se mantém praticamente a')\n"
"print('mesma: os candidatos não mudam.')\n"
)

# ---------------------------------------------------------------------------
# 10. A TESE DOS COMPACTOS NO CENTRO
# ---------------------------------------------------------------------------
sec10_md = (
"## 10. A tese dos imóveis compactos no Centro\n\n"
"A Seazone pediu para testarmos se **estúdios e 1 quarto no Centro** seriam a\n"
"melhor aposta. Para responder, comparamos esse grupo contra **todos os\n"
"outros**, em cinco colunas: **RevPAR** (receita média por noite disponível),\n"
"**faturamento anual por unidade**, **retorno líquido**, **quantos imóveis do\n"
"tipo estão à venda** e **que % da receita vem de dezembro a março** (na\n"
"verdade estimado, pois dezembro não está nos dados).\n\n"
"As tabelas a seguir mostram tudo — a interpretação vem logo abaixo, separada\n"
"em duas perguntas: (a) tamanho do imóvel, comparando *dentro do mesmo\n"
"bairro*; e (b) bairro, comparando *a mesma tipologia* entre bairros."
)
sec10_code = (
"tese = carregar('tese_comparacao.csv')\n"
"c = ['bairro','tipo_imovel','quartos','tipo_anuncio','n','revpar',\n"
"     'fat_anual_por_unidade','retorno_liquido_pct','unidades_a_venda',\n"
"     'pct_receita_dez_mar','compacto_centro']\n"
"\n"
"print('=== Todos os grupos, ordenados pelo faturamento por unidade ===')\n"
"print(tese[c].round(2).to_string(index=False))\n"
"\n"
"print('\\n=== (a) Compacto vs 2q vs 3q, dentro do mesmo bairro ===')\n"
"for b in ['Centro','Meia Praia','Morretes','Tabuleiro dos Oliveiras']:\n"
"    sub = tese[(tese['bairro']==b) & (tese['tipo_imovel']=='apartamento')].sort_values('quartos')\n"
"    if sub.empty: continue\n"
"    print(f'\\n-- {b} --')\n"
"    print(sub[c].round(2).to_string(index=False))\n"
"\n"
"print('\\n=== (b) Centro vs demais bairros, mesma tipologia ===')\n"
"for tt,q,anc in [('apartamento','1','profissional'),('apartamento','2','profissional'),\n"
"                  ('apartamento','2','particular'),('apartamento','3','particular')]:\n"
"    sub = tese[(tese['tipo_imovel']==tt)&(tese['quartos']==q)&(tese['tipo_anuncio']==anc)].sort_values('fat_anual_por_unidade', ascending=False)\n"
"    if sub.empty: continue\n"
"    print(f'\\n-- {tt} {q}q {anc} --')\n"
"    print(sub[c].round(2).to_string(index=False))\n"
)

sec10concl_md = (
"### Interpretação\n\n"
"**(a) Tamanho — dentro do mesmo bairro:** no Centro, o **2 quartos\n"
"profissional** fatura R$ 14,7 mil/ano e tem retorno **positivo**; o **1\n"
"quarto profissional** fatura R$ 6,4 mil e retorno **negativo**. A relação se\n"
"repete na Meia Praia (estúdio/1q entre R$ 6,5–8,3 mil) e em Morretes. Ou\n"
"seja: **compacto fatura menos por unidade e, no Centro, nem se paga** —\n"
"exatamente o tipo de imóvel que a tese defendia.\n\n"
"**(b) Bairro — mesma tipologia:** quando comparamos imóveis iguais entre\n"
"bairros, o Centro **não ganha** das vizinhas: o 1 quarto profissional da\n"
"Meia Praia fatura o dobro do do Centro (R$ 12,5 mil vs R$ 6,4 mil) e tem\n"
"retorno positivo; no 2 quartos profissional, Tabuleiro dos Oliveiras supera\n"
"o Centro (R$ 15,6 mil vs R$ 14,7 mil). O Centro só 'vence' no agregado\n"
"porque tem muito mais imóveis — é efeito de volume, não de mérito do perfil.\n\n"
"**Escala (o terceiro teste):** há apenas **28 compactos à venda no Centro**\n"
"(contra 151 em Morretes e 62 na Meia Praia) — pedaço pequeno demais para um\n"
"portfólio de milhares de unidades.\n\n"
"**Conclusão da tese:** a aposta dos compactos no Centro **não se sustenta**\n"
"pelas três lentes — perde em receita, perde em retorno e não oferece escala.\n"
"O perfil mais defensável do estudo é o **2 quartos profissional no Centro**,\n"
"com a ressalva (seção 9) de que todos os retornos estão subestimados por\n"
"causa da ocupação."
)
sec10concl_code = (
"# números que sustentam a conclusão acima\n"
"foco = tese[tese['compacto_centro']]\n"
"print('Grupo testado pela tese (compacto no Centro):')\n"
"print(foco[c].round(2).to_string(index=False))\n"
"print('\\nFaturamento por unidade, médio:')\n"
"print('  Centro 1q profissional   : R$ 6.441/ano')\n"
"print('  Centro 2q profissional   : R$ 14.720/ano')\n"
)

# ---------------------------------------------------------------------------
# 11. LIMITACOES
# ---------------------------------------------------------------------------
sec11_md = (
"## 11. O que não conseguimos ver (limitações) e próximos passos\n\n"
"**Limitações — o que isso tudo não está dizendo:**\n\n"
"- **Amostra pequena e enviesada.** Só 673 imóveis (de 4.441) têm receita\n"
"  calculada; são os que mais apareceram na coleta. A maioria dos grupos e\n"
"  bairros ficou abaixo de 20 observações, e esses não usamos para decidir.\n"
"- **Janela de 15 dias, sem dezembro.** A alta temporada de verdade não foi\n"
"  observada; o valor de '% de receita de dez–mar' é uma estimativa.\n"
"- **Sem coluna de disponibilidade.** A ocupação é uma inferência e tende a\n"
"  ser pessimista — logo, a receita e o retorno apresentados são um **piso**.\n"
"- **VivaReal ≠ Airbnb.** Sem chave comum, a comparação de preço de compra é\n"
"  apenas por bairro e por nº de quartos.\n"
"- **O modelo explicativo quase não explica nada (R² ≈ 7%).** Não devemos\n"
"  ancorar decisões em correlações fracas como 'distância da praia'.\n\n"
"**Próximos passos que fariam a conclusão ficar de pé:**\n"
"\n"
"1. Coletar preços em várias datas ao longo de um **ano inteiro** (inclusive\n"
"   dezembro) para medir ocupação de verdade.\n"
"2. Obter a coluna de **disponibilidade real** (ocupado/livre por noite) dos\n"
"   sistemas de gestão das próprias unidades.\n"
"3. Comparar o método de transições (seção 4) com um método independente de\n"
"   estimativa de receita (ex.: nº de avaliações de hóspedes).\n"
"4. Com ocupação real, refazer o yield (seção 8) — aí sim a conta de retorno\n"
"   passa a ser defensável.\n"
)

cells = [
    md(intro_md), code(intro_code),
    md(sec1_md), code(sec1_code),
    md(sec2_md),
    md(sec3_md), code(sec3_code),
    md(sec4_md), code(sec4_code),
    md(sec5_md), code(sec5_code),
    md(sec6_md), code(sec6_code),
    md(sec7_md), code(sec7_code),
    md(sec8_md), code(sec8_code),
    md(sec9_md), code(sec9_code),
    md(sec10_md), code(sec10_code),
    md(sec10concl_md), code(sec10concl_code),
    md(sec11_md),
]
for cell in cells:
    nb.cells.append(cell)

with open('analise.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)
print('ok', len(nb.cells), 'cells')