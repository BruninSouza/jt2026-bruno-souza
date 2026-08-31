# Meu critério de decisão

## Critério original (ancorado)

"Melhor" = o perfil de imóvel com maior **retorno anual líquido sobre o
valor investido** para comprá-lo. Só recomendo um perfil se ele passar
em três testes:

1. ESCALA — existem unidades suficientes à venda nesse perfil? A Seazone
   opera 3.000 imóveis; um perfil ótimo com 4 unidades não serve.
2. DENSIDADE — unidades concentradas em poucos prédios barateiam limpeza
   e check-in.
3. RISCO — quanto da receita depende de dezembro a março? Quantos
   concorrentes já existem?

## Revisão do critério (o que eu levaria para a decisão)

O ROI é a lente do **dono do imóvel**, não da **operadora**. O negócio da
Seazone ganha sobre a *receita* (taxa de gestão), não sobre o capital do
dono — então a decisão final deveria ser a lucratividade **por unidade
operada**, em nível de portfólio.

Falhas do ROI/testes como objetivo:

- ROI % premia imóvel barato; um retorno alto pode render tão pouco que a
  taxa de gestão **não cobre o custo de servir** (limpeza, check-in,
  reposição) → margem negativa por unidade.
- ESCALA tende a aprovar o segmento **mais comum = mais concorrido**,
  exatamente onde tarifa desce e marketing fica caro.
- DENSIDADE sem piso de *pipeline*: 8 unidades no mesmo prédio só servem
  se existir segundo prédio para escalar; senão vira bolha.
- RISCO olha só "quanto vem de dez–mar", não se o perfil **dá caixa
  negativo** no vazio da baixa temporada.
- Ignora **canibalização**: recomendar "mais do mesmo" no bairro já
  saturado pelo próprio portfólio maximiza receita média, não marginal.

### Critério proposto (a validar nos dados)

> **"Melhor" = maior margem de contribuição por unidade operada, no portfólio.**

> receita bruta anual × taxa de gestão − custo fixo por unidade − custo
> variável por diária efetivada,

com três restrições:

1. **piso de receita absoluta** por unidade (fee mínimo que cobre servir);
2. **limite de concentração** por prédio/bairro (diversificação em vez de
   densidade pura);
3. **estoque em pipeline** (à venda no trimestre) e receita **marginal**
   descontando canibalização das unidades já operadas.

Se mantivermos o ROI, ele vira **restrição** (piso para leitura do
investidor), e não objetivo.

---

# Hipóteses

## Hipóteses originais (escritas ANTES de ver os resultados)

- H1 (tese da Seazone): studio e 1 quarto no Centro são a melhor aposta.
- H2: compactos ganham em receita/m², mas imóveis maiores ganham em
  receita/unidade (cabem famílias). Qual vence depende do critério.
- H3: o bairro que mais fatura não é o de melhor retorno — o preço de
  venda já embutiu esse faturamento.
- H4: o que mais explica a receita não é tipologia nem bairro, e sim a
  qualidade da operação (superhost, avaliações, nota) ou a distância da praia.

## Hipóteses novas (deste debate)

- H5: existem perfis com ROI alto cuja receita absoluta **não cobre o
  custo de servir** — devem ser descartados apesar do ROI.
- H6: os bairros de maior volume (ESCALA) têm ocupação/tarifa mais
  pressionada por concorrência → pior receita marginal que o meio-termo.
- H7: o portfólio da Seazone **já satura os melhores bairros**; uma nova
  unidade lá canibaliza receita de unidades próprias.
- H8: perfis "uniformes" o ano todo mas fracos nos 4 meses de pico geram
  caixa negativo na baixa temporada — não passam no critério revisado.

## Validação das hipóteses (a preencher conforme os scripts rodam)

| Hipótese | Status | Evidência (gerada por src/ e lida em analise.ipynb) |
|---|---|---|
| H1 compactos/Centro | a validar | receita por perfil e bairro (src/05, src/06) |
| H2 receita/m² vs /unidade | a validar | receita por tipologia e tamanho |
| H3 bairro/clientela vs ROI | a validar | receita x preço de venda por bairro |
| H4 operação/distância da praia | a validar | correlações com superhost/notas/distância |
| H5 ROI alto × custo de servir | a validar | margem por unidade | 
| H6 volume = concorrência | a validar | ocupação/tarifa por bairro |
| H7 canibalização do portfólio | a validar | receita marginal por bairro |
| H8 vazio de baixa temporada | a validar | receita mensal e custo fixo mensal |

## Espaço para hipóteses futuras

- escreva aqui novas hipóteses ANTES de olhar os outputs correspondentes;
- cada hipótese nova vira linha da tabela de validação acima;
- nada de corrigir hipótese depois de ver o resultado: ou se escreve antes
  (e vale como previsão), ou se anota como "explicação pós-resultado".