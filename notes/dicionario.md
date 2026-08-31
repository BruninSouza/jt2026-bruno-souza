# Dicionário de dados — hackathon Seazone

Neste resumo, cada arquivo da pasta `data/` vira uma ficha simples.
Todos os dados são de anúncios de aluguel de temporada em Itapema (SC),
coletados do **Airbnb** (3 primeiros arquivos) e do **VivaReal** (o último).

## Como todos se conectam (resumo)

Pense no `airbnb_listing_id` como o "RG" do anúncio no Airbnb.
Ele é a peça que liga quase tudo:

```
Details ──(owner_id)──> Hosts_ids
Details ──(airbnb_listing_id)──> Mesh_Ids ──> traz o bairro (suburb)
Details ──(airbnb_listing_id)──> Price_AV ──> traz preço e data de cada diária
```

Detalhe importante: **Price_AV só tem preço para 1005 anúncios** (22,5% dos
4441 anúncios do Airbnb). O VivaReal é outro site; **não compartilha id**
com o Airbnb e só se compara por bairro ou cidade.

---

## 1. Details_Itapema.csv — os anúncios (4441 linhas)

O que é: um cadastro com **cada anúncio** de temporada no Airbnb em Itapema.

| Assunto | Coluna |
|---|---|
| Identificação | `airbnb_listing_id` (o RG do anúncio) |
| Localização | `latitude`, `longitude` |
| Tamanho do imóvel | `number_of_bedrooms`, `number_of_bathrooms`, `number_of_beds` |
| Convidados | `number_of_guests` |
| Dinheiro | `cleaning_fee` (taxa de limpeza em R$) |
| Avaliações | `number_of_reviews`, `star_rating`, notas de atendimento etc. |
| Regras | `check_in`, `check_out`, `min_nights` |
| Outros | `listing_type` (ex.: apartamento), `is_professional`, `amenities` |

Observações:
- Sem falhas nas colunas principais.
- Esta tabela **não tem o preço por noite** (isso fica no Price_AV).

## 2. Hosts_ids_Itapema.csv — os donos (4440 linhas)

O que é: ficha de **cada proprietário (host)** que tem anúncio em Itapema.

| Assunto | Coluna |
|---|---|
| Identificação | `owner_id` (o RG do dono) |
| Nome | `owner` |
| Reputação | `is_superhost`, `star_rating_host`, `number_of_reviews_host` |
| Verificação | `is_verified` |
| Experiência | `years_host`, `months_host` |
| Momento da foto | `host_snapshot_date` |

Conecta com: Details pelo `owner_id`. `response_rate_shown` e
`response_time_shown` estão 100% vazios (não dá para usar).

## 3. Mesh_Ids_Data_Itapema.csv — o bairro (4441 linhas)

O que é: um "endereço inferior" de cada anúncio, com a **divisão por bairro**.

| Assunto | Coluna |
|---|---|
| Identificação | `airbnb_listing_id` |
| Localização | `latitude`, `longitude` |
| Bairro | `suburb` |
| Território | `country`, `state`, `city` |

Conecta com: Details pelo `airbnb_listing_id` (100% dos anúncios têm linha).
**Este é o único arquivo que diz o bairro** (`suburb`) — usado para
analisar Meia Praia, Centro, Morretes etc.

## 4. Price_AV_Itapema.csv — preço por noite (118839 linhas)

O que é: o **histórico de preço de cada diária**. Uma linha = um par
(anúncio, noite). Cobre o período de **06/jan/2025 até 20/abr/2025**.

| Assunto | Coluna |
|---|---|
| Identificação | `airbnb_listing_id` |
| Noite (data da diária) | `date` |
| Preço da diária (R$) | `price` |
| Quando a coleta foi feita | `aquisition_date` (06 a 20/jan/2025) |

Pontos de atenção:
- Tem linha só para **1005 anúncios** (22,5% do total). O resto não aparece aqui.
- **Não existe coluna de "noite ocupada/livre"** aqui. A gente só sabe o
  preço; a ocupação tem de ser medida pelo nosso script (noites presentes
  no arquivo = noites que apareceram na coleta).
- `price` é o valor (R$) da diária; quando pau era simulado/estimado, nós
  explicamos no próprio script que divulgou o número.

## 5. VivaReal_Itapema.csv — o outro site (8329 linhas)

O que é: anúncios de **compra e venda ou aluguel tradicional** do VivaReal,
não aluguel de temporada.

| Assunto | Coluna |
|---|---|
| Identificação | `listing_id` (id do VivaReal, não é o do Airbnb) |
| Título e tipo | `listing_title`, `property_type`, `listing_type` |
| Preços | `sale_price` (venda), `rental_price` (aluguel) |
| Custos mensais | `yearly_iptu`, `monthly_condo_fee` |
| Estrutura | `usable_area`, `bathrooms`, `bedrooms`, `parking_spaces` |
| Bairro/cidade | `suburb`, `city`, `state` |
| Anunciante | `advertiser_name`, `portal` |

Observações:
- `rental_price` e `rental_period` estão 100% vazios: este arquivo serve
  praticamente só para preços de **venda**.
- Não compartilha `id` com o Airbnb; entra na comparação só por
  **bairro** (`suburb`).

---

## Nota sobre datas

- `aquisition_date` = quando o robô pegou o dado (período curto de coleta).
- `date` (no Price_AV) = a noite a que aquele preço se refere.