import os

import pandas as pd

DATA = "data"
OUT = "outputs"

# ---------------------------------------------------------------------------
# PREMISSAS DE NEGOCIO
# ---------------------------------------------------------------------------
P = {
    # Alerta para bairros com menos de 20 anuncios com receita calculada:
    # mediana/IQR nao sao confiaveis com amostra pequena.
    "alerta_bairro_abaixo_de_n": 20,
    # Precos de venda (VivaReal) por bairro sao usados na secao 8 (custo).
    "sem_preco_de_venda_aqui": True,
}


def main():
    rec = pd.read_csv(os.path.join(OUT, "receita_por_listing.csv"))
    mesh = pd.read_csv(os.path.join(DATA, "Mesh_Ids_Data_Itapema.csv"))

    antes = rec["airbnb_listing_id"].nunique()

    df = rec.merge(
        mesh[["airbnb_listing_id", "suburb"]],
        on="airbnb_listing_id",
        how="left",
    )
    df["bairro"] = df["suburb"].fillna("nao_informado")

    dep_nao_info = int((df["suburb"].isna()).sum())
    n_sem_suburb = df.loc[df["bairro"] == "nao_informado", "airbnb_listing_id"].nunique()

    loc = (
        df
        .groupby("bairro")
        .agg(
            n=("faturamento_anual", "size"),
            diaria_mediana=("diaria_mediana", "median"),
            diaria_p25=("diaria_mediana", lambda s: s.quantile(0.25)),
            diaria_p75=("diaria_mediana", lambda s: s.quantile(0.75)),
            ocupacao_mediana=("ocupacao", "median"),
            ocupacao_p25=("ocupacao", lambda s: s.quantile(0.25)),
            ocupacao_p75=("ocupacao", lambda s: s.quantile(0.75)),
            fat_anual_mediana=("faturamento_anual", "median"),
            fat_anual_p25=("faturamento_anual", lambda s: s.quantile(0.25)),
            fat_anual_p75=("faturamento_anual", lambda s: s.quantile(0.75)),
        )
        .reset_index()
    )
    loc["alerta_n_pequeno"] = loc["n"] < P["alerta_bairro_abaixo_de_n"]
    loc = loc.sort_values(
        ["fat_anual_mediana", "n"], ascending=[False, False]
    ).reset_index(drop=True)
    loc.to_csv(os.path.join(OUT, "localizacao.csv"), index=False)

    print(f"anuncios com receita no join: {antes} | orfaos (sem suburb): {n_sem_suburb} (removidos da analise)")
    print(f"bairros agrupados: {len(loc)} | com alerta n<20: {int(loc['alerta_n_pequeno'].sum())}")
    print(f"salvo em outputs/localizacao.csv")


if __name__ == "__main__":
    main()