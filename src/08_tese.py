import os
import unicodedata

import pandas as pd

DATA = "data"
OUT = "outputs"

# ---------------------------------------------------------------------------
# PREMISSAS DE NEGOCIO
# ---------------------------------------------------------------------------
P = {
    # % da receita anual concentrada em jan-abr (mesma do src/02_receita.py).
    # Usada para transformar o padrao mensal observado (jan-abr) em fracao
    # do ano; janeiro usado como proxy de dezembro (dez/2024 fora da coleta,
    # mesma alta temporada de jan/2025). Logo, "% receita de dez-mar" e uma
    # ESTIMATIVA derivada dessas duas premissas.
    "proporcao_receita_janela_4_meses": 0.70,
    "dezembro_prox_de_janeiro": True,
}


def _noacc(s):
    if not isinstance(s, str):
        return ""
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").lower().strip()


def bucket_quartos(q):
    if pd.isna(q):
        return "nao_informado"
    q = int(q)
    if q <= 0:
        return "0 (tenda/estudio)"
    if q <= 3:
        return str(q)
    return "4+"


def rotulo_prof(v):
    if pd.isna(v):
        return "nao_informado"
    return "profissional" if v else "particular"


def main():
    rec = pd.read_csv(os.path.join(OUT, "receita_por_listing.csv"))
    seg = pd.read_csv(os.path.join(OUT, "segmentos.csv"))
    yld = pd.read_csv(os.path.join(OUT, "yield_por_segmento.csv"))
    det = pd.read_csv(os.path.join(DATA, "Details_Itapema.csv"))
    mesh = pd.read_csv(os.path.join(DATA, "Mesh_Ids_Data_Itapema.csv"))

    KEYS = ["bairro", "tipo_imovel", "quartos", "tipo_anuncio"]

    # ---- mapa listing -> grupo ----
    mp = (
        det[["airbnb_listing_id", "listing_type", "number_of_bedrooms", "is_professional"]]
        .merge(mesh[["airbnb_listing_id", "suburb"]], on="airbnb_listing_id", how="left")
    )
    mp["bairro"] = mp["suburb"].fillna("nao_informado")
    mp["tipo_imovel"] = mp["listing_type"].fillna("nao_informado")
    mp["quartos"] = mp["number_of_bedrooms"].map(bucket_quartos)
    mp["tipo_anuncio"] = mp["is_professional"].map(rotulo_prof)

    r = rec.merge(mp[["airbnb_listing_id"] + KEYS], on="airbnb_listing_id", how="left")

    # ---- percentual de receita de dez-mar (estimativa) por grupo ----
    for m in ["2025-01", "2025-02", "2025-03", "2025-04"]:
        col_d = f"diaria_mediana_{m}"
        col_o = f"ocupacao_{m}"
        if col_d not in r.columns or col_o not in r.columns:
            print(f"ATENCAO: {col_d}/{col_o} inexistente; pulando.")
            r[col_d] = 0.0
            r[col_o] = 0.0
        r[f"rp_{m}"] = (r[col_d] * r[col_o]).fillna(0.0)

    grp = r.groupby(KEYS)
    jan = grp["rp_2025-01"].sum()
    fev = grp["rp_2025-02"].sum()
    mar = grp["rp_2025-03"].sum()
    abr = grp["rp_2025-04"].sum()
    S = jan + fev + mar + abr
    dez = jan * 1.0 if P["dezembro_prox_de_janeiro"] else 0.0
    fracao_dez_mar = ((dez + jan + fev + mar) / (S / P["proporcao_receita_janela_4_meses"])).clip(0, None)
    pct = (fracao_dez_mar * 100).round(1).rename("pct_receita_dez_mar").reset_index()

    # ---- monta tabela base: 5 colunas pedidas ----
    base = seg.merge(pct, on=KEYS, how="left").merge(
        yld[KEYS + ["retorno_liquido_pct", "n_vivareal"]],
        on=KEYS, how="left",
    )
    base["revpar"] = (base["diaria_mediana"] * base["ocupacao_mediana"]).round(2)
    base = base.rename(columns={"fat_anual_mediana": "fat_anual_por_unidade",
                                "n_vivareal": "unidades_a_venda"})

    final = base[KEYS + ["n", "revpar", "fat_anual_por_unidade", "retorno_liquido_pct",
                         "unidades_a_venda", "pct_receita_dez_mar", "alerta_n_pequeno"]].copy()
    final["compacto_centro"] = (
        (final["bairro"] == "Centro")
        & final["quartos"].isin(["0 (tenda/estudio)", "1"])
    )
    final = final.sort_values("fat_anual_por_unidade", ascending=False)
    final.to_csv(os.path.join(OUT, "tese_comparacao.csv"), index=False)
    final_centro = final[final["bairro"] == "Centro"].copy()

    pd.set_option("display.width", 240)
    pd.set_option("display.max_rows", 100)

    c = ["bairro", "tipo_imovel", "quartos", "tipo_anuncio", "n", "revpar",
         "fat_anual_por_unidade", "retorno_liquido_pct", "unidades_a_venda",
         "pct_receita_dez_mar", "compacto_centro"]
    print("==" * 60)
    print("TABELA GERAL — todos os grupos ('compacto_centro' = studio+1q no Centro)")
    print("==" * 60)
    print(final[c].round(2).to_string(index=False))

    print()
    # resumo: compacto no centro somando 0-1q vs cada outro grupo
    print("-- CENTRO compacto (0-1q) somado --")
    ck = final_centro[final_centro["compacto_centro"]]
    print(ck[c].round(2).to_string(index=False))

    print()
    print("==" * 60)
    print("(a) compacto vs 2q vs 3q -- DENTRO do mesmo bairro (apartamento)")
    print("==" * 60)
    for b in ["Centro", "Meia Praia", "Morretes", "Tabuleiro dos Oliveiras"]:
        sub = final[(final["bairro"] == b) & (final["tipo_imovel"] == "apartamento")].copy()
        if sub.empty:
            continue
        sub = sub.sort_values("quartos")
        print(f"\n-- {b} --")
        print(sub[c].round(2).to_string(index=False))

    print()
    print("==" * 60)
    print("(b) Centro vs demais bairros -- DENTRO da mesma tipologia")
    print("==" * 60)
    for tt, q, anc in [("apartamento", "1", "profissional"), ("apartamento", "2", "profissional"),
                       ("apartamento", "2", "particular"), ("apartamento", "3", "particular")]:
        sub = final[(final["tipo_imovel"] == tt) & (final["quartos"] == q) & (final["tipo_anuncio"] == anc)].copy()
        if sub.empty:
            continue
        sub = sub.sort_values("fat_anual_por_unidade", ascending=False)
        print(f"\n-- {tt} {q}q {anc} --")
        print(sub[c].round(2).to_string(index=False))


if __name__ == "__main__":
    main()