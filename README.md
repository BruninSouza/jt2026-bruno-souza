# Itapema (SC), aluguel por temporada — Seazone

> **Vídeo (3 min):** https://drive.google.com/file/d/1ddU-Am_eFpRRFJCo6bqE6XecXTj0aPDG/view?usp=drive_link

**Recomendação de investimento imobiliário para a Seazone**, construída com o apoio de IA (OpenCode), a partir de dados reais de anúncios de Airbnb e de venda (VivaReal) na cidade de Itapema, Santa Catarina.

Se você quer só a conclusão, leia o [`Relatorio.md`](Relatorio.md). Se quiser entender o caminho completo, com gráficos e tabelas, siga a leitura deste README, depois abra o caderno [`analise.ipynb`](analise.ipynb).

---

## 1. Do que se trata o projeto

A Seazone gerencia mais de 3.000 imóveis de aluguel por temporada no Brasil e precisa decidir **onde e no que investir**. Este projeto responde a quatro perguntas para a cidade de Itapema:

1. Qual o **melhor perfil de imóvel** para investir (tipo, número de quartos, quem administra o anúncio)?
2. Qual a **melhor localização** em termos de receita?
3. Quais **características explicam** as melhores receitas?
4. Se a Seazone investisse hoje, **o que comprar e por quê**, com estimativa de retorno?

O desafio também pede posicionamento sobre uma tese interna: **apartamentos compactos (studio e 1 quarto) no Centro seriam a aposta mais eficiente**. Este trabalho responde isso com os dados na seção 10 do caderno e no relatório.

**Resposta em uma frase:** os dados apontam para **apartamentos de 2 quartos operados por anfitrião profissional no Centro (e secundariamente no Tabuleiro dos Oliveiras)** como o perfil mais defensável, e **não sustentam a tese dos compactos no Centro**.

---

## 2. O que você recebeu (estrutura do projeto)

Estes são apenas os arquivos que fazem parte da entrega (itens sensíveis e gerados já são ignorados pelo `.gitignore`). Passe o mouse ou abra cada pasta para ver o que ela faz.

```
hackathon/
├── README.md             este guia, com o passo a passo para rodar tudo
├── Relatorio.md          a recomendação final, escrita para qualquer pessoa ler
├── analise.ipynb         o caderno principal: gráficos e tabelas que contam a história
├── hipoteses.md          as hipóteses (escritas antes de ver os resultados) e o critério de decisão
├── index.html            o desafio original, como foi passado
├── AGENTS.md             instruções de trabalho usadas com a IA durante a construção
│
├── requirements.txt      snapshot completo do ambiente (o que foi usado)
├── requirements-core.txt lista enxuta do que é preciso instalar para rodar do zero
│
├── data/                 (ignorado no git) os 5 arquivos-fonte de Itapema
│   ├── Details_Itapema.csv        anúncios do Airbnb (quartos, avaliações, notas, tipo)
│   ├── Hosts_ids_Itapema.csv      anfitriões (superhost, anos de host)
│   ├── Mesh_Ids_Data_Itapema.csv  bairro e coordenada de cada imóvel
│   ├── Price_AV_Itapema.csv       preço por noite de estadia (jan–abr 2025)
│   └── VivaReal_Itapema.csv       mercado de venda (preço, condomínio, área)
│
├── outputs/              (ignorado no git) resultados salvos por cada script
│   ├── perfil_dados.txt             diagnóstico das colunas e ligações
│   ├── receita_por_listing.csv      receita anual estimada por imóvel
│   ├── segmentos.csv                agrupamentos (bairro × tipo × quartos × anúncio)
│   ├── localizacao.csv              receita e ocupação por bairro
│   ├── regressao.csv                modelo que explora o que explica as receitas
│   ├── yield_por_segmento.csv       conta de custo e retorno por segmento
│   ├── sensibilidade.csv            retorno sob variações de ocupação e diária
│   └── tese_comparacao.csv          comparação da tese dos compactos no Centro
│
├── src/                  os códigos, numerados na ordem em que devem rodar
│   ├── 01_perfil.py                  inspeciona os arquivos (colunas, ligações)
│   ├── 02_receita.py                 estima a receita anual por imóvel
│   ├── 03_segmentos.py               agrupa imóveis e calcula diária/ocupação/faturamento
│   ├── 04_localizacao.py             consolida receita por bairro
│   ├── 05_regressao.py               regressão do faturamento contra características
│   ├── 06_yield.py                   cruza com VivaReal e calcula retorno
│   ├── 07_sensibilidade.py           varia premissas e mede impacto no retorno
│   ├── 08_tese.py                    monta as tabelas da tese dos compactos
│   └── _build_notebook.py            reconstrói o analise.ipynb a partir do texto
│
├── notes/
│   └── dicionario.md     explicação simples de cada arquivo de dados e das colunas
│
├── figs/                 gráficos usados no Relatorio.md (extraídos do caderno)
│   ├── fig_histograma.png
│   ├── fig_perfis.png
│   ├── fig_localizacao.png
│   ├── fig_regressao.png
│   └── fig_sensibilidade.png
│
└── ai-log/               conversas com a IA em texto (parte da avaliação)
    └── session-ses_fa77.md
```

**Fluxo de trabalho:** os scripts em `src/` leem de `data/` e gravam em `outputs/`. O caderno `analise.ipynb` apenas lê `outputs/`, monta gráficos e apresenta. O `Relatorio.md` usa os gráficos de `figs/` e os números de `outputs/`.

---

## 3. Tudo o que você precisa ter instalado

- **Python 3.11 ou superior** (testado com 3.13/3.14).
- **Jupyter** (opcional, só para abrir o caderno).

No Windows, o jeito mais simples é baixar o Python pelo site oficial e marcar a opção "Add to PATH" na instalação.

---

## 4. Colocando o projeto para rodar, passo a passo

Abra o **Prompt de Comando** ou o **PowerShell** na pasta do projeto.

### Passo 1. Crie um ambiente isolado (recomendado)

```bash
python -m venv .venv
```

No PowerShell ative com:

```bash
.venv\Scripts\Activate.ps1
```

(Se der erro de permissão, rode `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` e tente de novo.)

### Passo 2. Instale as dependências

```bash
pip install -r requirements-core.txt
```

Se preferir reproduzir exatamente o ambiente usado, instale o completo:

```bash
pip install -r requirements.txt
```

A pasta `.venv/` fica fora do git (o `.gitignore` cuida disso), então nada disso vaza para o repositório.

### Passo 3. Coloque os dados

A pasta `data/` está ignorada no git. Os 5 arquivos vieram do repositório do desafio. Coloque-os aqui:

```
data/
  Details_Itapema.csv
  Hosts_ids_Itapema.csv
  Mesh_Ids_Data_Itapema.csv
  Price_AV_Itapema.csv
  VivaReal_Itapema.csv
```

### Passo 4. Rode os scripts na ordem

Cada script lê de `data/` e grava em `outputs/`, e imprime no final quantas linhas entraram, quantas ficaram após os filtros e quantas caíram.

```bash
python src/01_perfil.py
python src/02_receita.py
python src/03_segmentos.py
python src/04_localizacao.py
python src/05_regressao.py
python src/06_yield.py
python src/07_sensibilidade.py
python src/08_tese.py
```

Você verá criar-se (ou atualizar-se) cada arquivo em `outputs/`.

### Passo 5. Abra o caderno de análise

```bash
jupyter notebook analise.ipynb
```

Ou, se quiser o caderno executado automaticamente:

```bash
python -m nbconvert --to notebook --execute --inplace analise.ipynb
```

O caderno reconstroi os gráficos e tabelas a partir dos arquivos de `outputs/`.

### Passo 6. Leia a conclusão

Tudo o que os gráficos contam está resumido de forma simples em [`Relatorio.md`](Relatorio.md).

---

## 5. Como a estimativa de receita funciona (o coração da análise)

Como os dados não têm uma coluna "noite ocupada ou livre", a receita foi estimada por um método indireto:

- Uma noite que estava **livre** na coleta de 6/7 de janeiro e **sumiu** na coleta de 20 de janeiro foi contada como **venda**.
- Uma noite já **ocupada na primeira coleta** não foi contada como receita (pode ser reserva ou bloqueio do proprietário; por prudência, não soma).
- Com isso medimos **ocupação** e **diária mediana** por imóvel e projetamos o ano assumindo que **janeiro a abril concentram 70% da receita** de Itapema.

Todas as premissas de negócio ficam em um dicionário no topo de cada script, com comentário explicando o porquê. Esse detalhe é importante para transparência e para a sensibilidade (seção 9 do caderno) testar justamente essas premissas.

---

## 6. Principais achados

1. **Perfil:** apartamento de **2 quartos com anúncio profissional** no Centro é o que mais fatura (cerca de R$ 14,7 mil/ano típico) e o único com retorno líquido positivo relevante.
2. **Localização:** o **Centro** lidera a receita típica; a Meia Praia tem muito mais oferta (competição), e o Morretes é o mais fraco.
3. **O que explica receita:** quase nada das características da planilha explica as diferenças (R² ≈ 7%). Gestão e reputação valem mais.
4. **Tese dos compactos:** **não se sustenta**. Compactos no Centro faturam menos por unidade e têm retorno negativo; a tese falha também em escala (poucas unidades à venda).
5. **Ressalva honesta:** a janela de dados é curta (sem dezembro), então as receitas são um **piso**, não um teto. A ordem entre bairros e perfis, porém, se mantém sob os testes de sensibilidade.

---

## 7. Entregas exigidas pelo desafio

- [ x ] **Repositório público** com código, leitura, `ai-log/` e esta recomendação escrita.
- [ x ] **Pasta `ai-log/`** com as conversas com a IA exportadas em texto (não vale print).
- [ x ] **Vídeo de até 3 minutos**, com o link na primeira linha deste README.

O detalhe original de todas as regras e prazo está no [`index.html`](index.html) deste repositório.

---

*Seazone · Hackathon Jovens Talentos AI Builder 2026*