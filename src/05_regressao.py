import os
import unicodedata

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

DATA = "data"
OUT = "outputs"

# ---------------------------------------------------------------------------
# PREMISSAS DE NEGOCIO
# ---------------------------------------------------------------------------
P = {
    # Alvo log1p(faturamento_anual): 158 anuncios tem faturamento zero
    # (nenhuma noite vendida na janela). log(0) nao existe; somar 1 preserva
    # esses anuncios na regressao em vez de deixar cair.
    "nao_droppar_fat_zero": True,
    # Distancia da praia: nao ha arquivo de linha de costa. Proxy = distancia
    # em km, na linha de latitude do anuncio, ate o ponto mais a leste de TODOS
    # os anuncios na mesma faixa de latitude (o mar fica a leste em Itapema).
    # So-Called 'frente praia' = distancia ~0. Feito sobre o Mesh inteiro
    # (4461 pontos) para o proxy nao depender so dos que tem receita.
    "proxy_distancia_praia": "leste do anuncio ate longitude da faixa de latitude no Mesh total",
    # Acentos removidos do titulo para casar 'frente mar', 'vista mar',
    # 'piscina' e 'beira mar' (muito comum em Itapema e claramente sinal de
    # frente praia, alem das 3 palavras pedidas).
    "palavras_titulo": ["frente mar", "vista mar", "piscina", "beira mar"],
    # Hosts_ids tem 1 linha por (owner, snapshot); deduplico mantendo o ultimo
    # snapshot (o mais recente) para nao multiplicar anuncio x host.
    "join_hosts_owner_1x1_ultimo_snapshot": True,
}


def _noacc(s):
    return "".join(
        c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn"
    ).lower()


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dp = p2 - p1
    dl = np.radians(lon2 - lon1)
    a = np.sin(dp / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(a))


def main():
    rec = pd.read_csv(os.path.join(OUT, "receita_por_listing.csv"))
    mesh = pd.read_csv(os.path.join(DATA, "Mesh_Ids_Data_Itapema.csv"))
    det = pd.read_csv(os.path.join(DATA, "Details_Itapema.csv"))
    host = pd.read_csv(os.path.join(DATA, "Hosts_ids_Itapema.csv"))

    n_entrada = len(rec)

    # --- proxy de linha de praia sobre o Mesh inteiro (por faixa de latitude)
    mesh["lat_band"] = mesh["latitude"].round(3)
    costa = mesh.groupby("lat_band")["longitude"].max().rename("lon_costa")
    mesh_all = mesh.merge(costa, on="lat_band", how="left")
    mesh_all["dist_praia_km"] = haversine_km(
        mesh_all["latitude"], mesh_all["longitude"],
        mesh_all["latitude"], mesh_all["lon_costa"],
    )

    df = rec.merge(
        mesh_all[["airbnb_listing_id", "suburb", "lat_band", "dist_praia_km"]],
        on="airbnb_listing_id", how="left",
    )
    df = df.merge(
        det[["airbnb_listing_id", "owner_id", "number_of_reviews", "star_rating",
             "number_of_guests", "number_of_bedrooms", "ad_name"]],
        on="airbnb_listing_id", how="left",
    )

    host_dedup = (
        host.sort_values("host_snapshot_date")
        .groupby("owner_id", as_index=False)
        .last()
    )
    df = df.merge(
        host_dedup[["owner_id", "is_superhost", "years_host"]],
        on="owner_id", how="left",
    )

    # palavras no titulo
    tit = df["ad_name"].fillna("").apply(_noacc)
    for palavra in P["palavras_titulo"]:
        df[f"titulo_{palavra.replace(' ', '_')}"] = tit.str.contains(palavra).astype(int)

    df["log_fat"] = np.log1p(df["faturamento_anual"])
    df["log_reviews"] = np.log1p(df["number_of_reviews"].fillna(0))

    n_apos_join = n_entrada - len(df) + len(df)  # sem perda aqui
    n_apos_join = len(df)

    # limpeza de preditores
    pred_cols = ["suburb", "number_of_bedrooms", "is_superhost", "years_host",
                 "number_of_reviews", "star_rating", "number_of_guests",
                 "dist_praia_km"] + [f"titulo_{p.replace(' ', '_')}" for p in P["palavras_titulo"]]
    n_antes_drop = len(df)
    df = df.dropna(subset=pred_cols + ["log_fat"])
    n_apos_drop = len(df)

    formula = (
        "log_fat ~ "
        + " + ".join([f"titulo_{p.replace(' ', '_')}" for p in P["palavras_titulo"]])
        + " + C(suburb)"
        + " + number_of_bedrooms + is_superhost + years_host"
        + " + log_reviews + star_rating + number_of_guests + dist_praia_km"
    )
    modelo = smf.ols(formula, data=df).fit()

    coefs = modelo.params.to_frame("coef").join(modelo.pvalues.to_frame("pvalue"))
    ci = modelo.conf_int()
    coefs["ci_low"] = ci[0]
    coefs["ci_high"] = ci[1]
    coefs = coefs.rename_axis("variavel").reset_index()
    coefs["exp_coef"] = np.expm1(coefs["coef"]).round(4)
    coefs.to_csv(os.path.join(OUT, "regressao.csv"), index=False)

    m = modelo
    print(f"premissas: {P}")
    print(f"anuncios (entrada):        {n_entrada}")
    print(f"  apos join (com preco+geo):{n_apos_join}")
    print(f"  apos dropna preditores:  {n_apos_drop} (caidos {n_antes_drop - n_apos_drop})")
    print(f"R^2        = {m.rsquared:.3f}")
    print(f"R^2 ajust. = {m.rsquared_adj:.3f}")
    print(f"salvo em outputs/regressao.csv")
    print()
    ex = coefs[coefs["variavel"] != "Intercept"].sort_values("coef", ascending=False)
    for _, r in ex.iterrows():
        sig = "***" if r["pvalue"] < 0.01 else ("**" if r["pvalue"] < 0.05 else ("*" if r["pvalue"] < 0.1 else ""))
        print(f"  {r['variavel']:<42} coef={r['coef']:+.3f}  exp={r['exp_coef']:+.3f}  p={r['pvalue']:.3f} {sig}")


if __name__ == "__main__":
    main()