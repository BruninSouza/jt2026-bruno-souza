import os

import pandas as pd

DATA = "data"
OUT = "outputs"

# ---------------------------------------------------------------------------
# PREMISSAS DE NEGOCIO
# ---------------------------------------------------------------------------
P = {
    # Alerta para grupos com menos de 20 anuncios: amostra pequena demais para
    # mediana/o IQR serem confiaveis (ruido em vez de sinal).
    "alerta_abaixo_de_n_anuncios": 20,
    # Agrupamento de quartos: 4+ vira 1 categoria para evitar grupos vazios
    # (poucos anuncios com 5+ quartos). 0 = tenda/estudio (sem quarto dedicado).
    "agrupar_quartos_4_mais": True,
    # numero de anuncios sem receita (nunca apareceram em Price_AV) -> contados
    # no diagnostico e excluidos do agrupamento (nao ha faturamento para eles).
    "anuncios_sem_preco_excluidos_do_agrupamento": True,
}


def rotulo_quartos(q):
    if pd.isna(q):
        return "nao_informado"
    q = int(q)
    if q == 0:
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
    det = pd.read_csv(os.path.join(DATA, "Details_Itapema.csv"))
    mesh = pd.read_csv(os.path.join(DATA, "Mesh_Ids_Data_Itapema.csv"))

    rec_ids = set(rec["airbnb_listing_id"])
    det_ids = set(det["airbnb_listing_id"])
    mesh_ids = set(mesh["airbnb_listing_id"])

    sem_preco_det = len(det_ids - rec_ids)
    sem_preco_mesh = len(mesh_ids - rec_ids)

    df = (
        rec
        .merge(det[["airbnb_listing_id", "listing_type", "number_of_bedrooms",
                    "is_professional"]], on="airbnb_listing_id", how="left")
        .merge(mesh[["airbnb_listing_id", "suburb"]], on="airbnb_listing_id", how="left")
    )
    df["tipo_imovel"] = df["listing_type"].fillna("nao_informado")
    df["quartos"] = df["number_of_bedrooms"].map(rotulo_quartos)
    df["tipo_anuncio"] = df["is_professional"].map(rotulo_prof)
    df["bairro"] = df["suburb"].where(~df["suburb"].isna(), "nao_informado")

    grupos = (
        df
        .groupby(["bairro", "tipo_imovel", "quartos", "tipo_anuncio"])
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
    grupos["alerta_n_pequeno"] = grupos["n"] < P["alerta_abaixo_de_n_anuncios"]
    grupos = grupos.sort_values(
        ["fat_anual_mediana", "n"], ascending=[False, False]
    ).reset_index(drop=True)
    grupos.to_csv(os.path.join(OUT, "segmentos.csv"), index=False)

    print(f"anuncios com receita: {len(rec)} | sem preco no Details: {sem_preco_det} | sem preco no Mesh: {sem_preco_mesh}")
    print(f"grupos de segmento:   {len(grupos)} | com alerta n<20: {int(grupos['alerta_n_pequeno'].sum())}")
    print(f"salvo em outputs/segmentos.csv")


if __name__ == "__main__":
    main()