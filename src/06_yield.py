import os
import unicodedata

import numpy as np
import pandas as pd

DATA = "data"
OUT = "outputs"

# ---------------------------------------------------------------------------
# PREMISSAS DE NEGOCIO
# ---------------------------------------------------------------------------
P = {
    # Custo de compra: ITBI (~2-3%) + escritura/registro/expedientes somam ~5%.
    "pct_custos_compra": 0.05,
    # Mobilia e enxoval completo para temporada (camas, moveis, TV, louca).
    # Ajustavel: imovel costeiro com rotatividade pesada.
    "mobilia": 60000.0,
    # Comissao de canal (Airbnb/plataforma): ~15% do bruto. Flutua 14-18%
    # conforme plataforma e contrato.
    "comissao_canal_pct": 0.15,
    # Limpeza e troca de enxoval por estadia (R$). Praia, temporada: R$ 120.
    "custo_limpeza_por_reserva": 120.0,
    # Manutencao anual e reposicao de quebras/reposicao de enxoval
    # (simulacao de ST): ~5% da receita bruta.
    "manutencao_pct": 0.05,
    # Taxa de administracao da operadora de temporada (tipo Seazone): servico
    # completo de gestao. ~20% da receita bruta.
    "taxa_administracao_pct": 0.20,
    # Noites medias por estadia (usada para estimar numero de reservas).
    # Mesma premissa do src/02_receita.py.
    "noites_por_estadia": 4.0,
    # A receita bruta aqui e o faturamento_anual vindo de src/02_receita.py
    # (que ja extrapolou jan-abr / 0.70). Mantido igual para coerencia.
    "proporcao_receita_janela_4_meses": 0.70,
    # Condominio/IPTU faltantes no VivaReal: quando faltam num grupo, cai para
    # a mediana do bairro; se ainda faltar, assume 0 (casas sem condominio) e
    # marca a flag. Sem isso a conta inteira viraria NaN por causa de ~30% de
    # valores ausentes nessas colunas.
    "condominio_faltante_pra_zero": True,
}


def _noacc(s):
    if not isinstance(s, str):
        return ""
    return "".join(
        c for c in unicodedata.normalize("NFD", s)
        if unicodedata.category(c) != "Mn"
    ).lower().strip()


def bucket_quartos(q):
    if pd.isna(q):
        return "nao_informado"
    q = int(q)
    if q == 0:
        return "0 (tenda/estudio)"
    if q <= 3:
        return str(q)
    return "4+"


def main():
    seg = pd.read_csv(os.path.join(OUT, "segmentos.csv"))
    v = pd.read_csv(os.path.join(DATA, "VivaReal_Itapema.csv"))

    # ---- VIVA REAL: mediana de preco/m2/condominio por (bairro, quartos) ----
    v = v.rename(columns={"sale_price": "preco_venda", "usable_area": "area_m2",
                          "monthly_condo_fee": "condominio_mensal", "yearly_iptu": "iptu"})
    n_v_input = len(v)

    v["bairro_norm"] = v["suburb"].map(_noacc)
    v["quartos"] = v["bedrooms"].map(bucket_quartos)
    v["preco_m2"] = v["preco_venda"] / v["area_m2"].where(v["area_m2"] > 0)

    grupos = (
        v.groupby(["bairro_norm", "quartos"])
        .agg(
            n_vivareal=("preco_venda", "size"),
            preco_venda_mediano=("preco_venda", "median"),
            preco_m2_mediano=("preco_m2", "median"),
            condominio_mediano=("condominio_mensal", "median"),
            iptu_mediano=("iptu", "median"),
        )
        .reset_index()
    )
    n_v_apos_grupo = len(grupos)

    # ---- SEGMENTOS: join e rendimento ----
    seg["chave"] = seg["bairro"].map(_noacc) + "|" + seg["quartos"].astype(str)
    grupos["chave"] = grupos["bairro_norm"].astype(str) + "|" + grupos["quartos"].astype(str)

    y = seg.merge(
        grupos[["chave", "n_vivareal", "preco_venda_mediano", "preco_m2_mediano",
                "condominio_mediano", "iptu_mediano"]],
        on="chave", how="left",
    )

    # condominio/iptu caem para mediana do bairro e depois 0, com flag
    med_cond_bairro = v.groupby("bairro_norm")["condominio_mensal"].median()
    med_iptu_bairro = v.groupby("bairro_norm")["iptu"].median()
    y["condominio_mediano"] = y["condominio_mediano"].fillna(
        y["bairro"].map(_noacc).map(med_cond_bairro)).fillna(0)
    y["iptu_mediano"] = y["iptu_mediano"].fillna(
        y["bairro"].map(_noacc).map(med_iptu_bairro)).fillna(0)
    y["falta_dado_vivareal"] = y["preco_venda_mediano"].isna() | y["n_vivareal"].isna()
    y["n_vivareal"] = y["n_vivareal"].fillna(0).astype(int)

    # ---- CALCULO DO RENDIMENTO (por segmento, sobre a receita mediana) ----
    bruta = y["fat_anual_mediana"]
    diaria = y["diaria_mediana"]
    denom = diaria * P["noites_por_estadia"]
    y["reservas_estimadas"] = bruta / denom.where(diaria.notna() & (diaria > 0))
    comissao = bruta * P["comissao_canal_pct"]
    custo_limpeza = y["reservas_estimadas"] * P["custo_limpeza_por_reserva"]
    cond_anual = y["condominio_mediano"] * 12
    iptu = y["iptu_mediano"]
    manutencao = bruta * P["manutencao_pct"]
    taxa_admin = bruta * P["taxa_administracao_pct"]
    custos_compra = y["preco_venda_mediano"] * P["pct_custos_compra"]

    y["investimento_total"] = y["preco_venda_mediano"] + custos_compra + P["mobilia"]
    y["comissao_canal"] = comissao
    y["custo_limpeza"] = custo_limpeza
    y["condominio_anual"] = cond_anual
    y["iptu"] = iptu
    y["manutencao"] = manutencao
    y["taxa_admin"] = taxa_admin
    y["receita_liquida"] = (
        bruta - comissao - custo_limpeza - cond_anual - iptu
        - manutencao - taxa_admin
    )
    y["retorno_bruto_pct"] = bruta / y["investimento_total"] * 100
    y["retorno_liquido_pct"] = y["receita_liquida"] / y["investimento_total"] * 100
    y["anos_para_pagar"] = np.where(
        y["receita_liquida"] > 0,
        y["investimento_total"] / y["receita_liquida"],
        np.inf,
    )

    cols = [
        "bairro", "tipo_imovel", "quartos", "tipo_anuncio", "n", "n_vivareal",
        "preco_venda_mediano", "preco_m2_mediano", "condominio_mediano",
        "iptu_mediano", "investimento_total", "fat_anual_mediana",
        "reservas_estimadas", "comissao_canal", "custo_limpeza",
        "condominio_anual", "iptu", "manutencao", "taxa_admin",
        "receita_liquida", "retorno_bruto_pct", "retorno_liquido_pct",
        "anos_para_pagar", "alerta_n_pequeno", "falta_dado_vivareal",
    ]
    y = y[cols].sort_values("retorno_liquido_pct", ascending=False)
    y.to_csv(os.path.join(OUT, "yield_por_segmento.csv"), index=False)

    print(f"VivaReal entrada: {n_v_input} | grupos (bairro, quartos): {n_v_apos_grupo}")
    print(f"segmentos: {len(seg)} | com preco de venda no VivaReal: {int((~y['falta_dado_vivareal']).sum())}")
    print(f"  sem preco de venda no VivaReal (yield NaN): {int(y['falta_dado_vivareal'].sum())}")
    print(f"salvo em outputs/yield_por_segmento.csv")
    print()
    show = y[~y["falta_dado_vivareal"]].head(15)
    cols_show = ["bairro", "quartos", "tipo_imovel", "tipo_anuncio", "n", "n_vivareal",
                 "preco_venda_mediano", "preco_m2_mediano", "investimento_total",
                 "fat_anual_mediana", "reservas_estimadas", "receita_liquida",
                 "retorno_bruto_pct", "retorno_liquido_pct", "anos_para_pagar"]
    print(show[cols_show].round(2).to_string(index=False))


if __name__ == "__main__":
    main()