import os

import numpy as np
import pandas as pd

OUT = "outputs"

# ---------------------------------------------------------------------------
# PREMISSAS DE NEGOCIO
# ---------------------------------------------------------------------------
P = {
    # --- derivados do src/06_yield.py (mantidos iguais p/ coerencia) ---
    # Custo de compra: ITBI + escritura/registro/expedientes somam ~5%.
    "pct_custos_compra": 0.05,
    # Mobilia e enxoval completo de temporada (camas, moveis, TV, louca).
    "mobilia": 60000.0,
    # Comissao do canal (Airbnb/plataforma): ~15% do bruto.
    "comissao_canal_pct": 0.15,
    # Limpeza e troca de enxoval por estadia (R$). Praia, temporada: R$ 120.
    "custo_limpeza_por_reserva": 120.0,
    # Manutencao anual ~5% da receita bruta.
    "manutencao_pct": 0.05,
    # Taxa de administracao da operadora de temporada (tipo Seazone): ~20%.
    "taxa_administracao_pct": 0.20,
    # Noites medias por estadia (mesma do src/02_receita.py).
    "noites_por_estadia": 4.0,

    # --- variacoes de cenario da sensibilidade ---
    # Ocupacao +- 10 pontos percentuais (pp) em cima da ocupacao mediana do
    # grupo. Ex.: ocupacao 15% vira 25% ou 5%.
    "variacao_ocupacao_pp": 0.10,
    # Diaria +- 10% multiplicativa em cima da diaria mediana.
    "variacao_diaria_pct": 0.10,
    # Piso de ocupacao usado ao subtrair 10pp (evita divisao por zero e
    # ocupacao negativa; preserva um cenario de baixa, nao zero absoluto).
    "piso_ocupacao": 0.01,
}

# cenario: nome, delta_ocupacao_pp, fator_diaria
CENARIOS = [
    ("base",                   0.0,            1.0),
    ("oc+10pp / di+10%",       +P["variacao_ocupacao_pp"], 1 + P["variacao_diaria_pct"]),
    ("oc+10pp / di-10%",       +P["variacao_ocupacao_pp"], 1 - P["variacao_diaria_pct"]),
    ("oc-10pp / di+10%",       -P["variacao_ocupacao_pp"], 1 + P["variacao_diaria_pct"]),
    ("oc-10pp / di-10%",       -P["variacao_ocupacao_pp"], 1 - P["variacao_diaria_pct"]),
]

KEYS = ["bairro", "tipo_imovel", "quartos", "tipo_anuncio"]


def calc(linha, delta_oc, fator_di):
    invest = linha["investimento_total"]
    bruta = linha["fat_anual_mediana"] * ((max(linha["ocupacao_mediana"], P["piso_ocupacao"]) + delta_oc)
                                          / max(linha["ocupacao_mediana"], P["piso_ocupacao"])) * fator_di
    diaria_cen = linha["diaria_mediana"] * fator_di
    reservas = bruta / (diaria_cen * P["noites_por_estadia"]) if (diaria_cen and diaria_cen > 0) else np.nan
    comissao = bruta * P["comissao_canal_pct"]
    limpeza = reservas * P["custo_limpeza_por_reserva"]
    cond_anual = linha["condominio_anual"]
    iptu = linha["iptu"]
    manut = bruta * P["manutencao_pct"]
    taxa = bruta * P["taxa_administracao_pct"]
    liq = bruta - comissao - limpeza - cond_anual - iptu - manut - taxa
    ret_bruto = bruta / invest * 100
    ret_liq = liq / invest * 100
    anos = invest / liq if liq > 0 else np.inf
    return bruta, reservas, comissao, limpeza, liq, ret_bruto, ret_liq, anos


def main():
    y = pd.read_csv(os.path.join(OUT, "yield_por_segmento.csv"))
    seg = pd.read_csv(os.path.join(OUT, "segmentos.csv"))
    df = y.merge(
        seg[KEYS + ["diaria_mediana", "ocupacao_mediana"]],
        on=KEYS, how="left",
    )
    df = df[~df["falta_dado_vivareal"]].copy()
    n_validos = len(df)

    linhas = []
    for _, r in df.iterrows():
        for nome_cen, delta_oc, fator_di in CENARIOS:
            bruta, reservas, comissao, limpeza, liq, ret_b, ret_l, anos = calc(r, delta_oc, fator_di)
            linhas.append({
                **{k: r[k] for k in KEYS},
                "n": r["n"], "n_vivareal": r["n_vivareal"],
                "alerta_n_pequeno": r["alerta_n_pequeno"],
                "ocupacao_mediana": r["ocupacao_mediana"],
                "diaria_mediana": r["diaria_mediana"],
                "cenario": nome_cen,
                "fator_diaria": fator_di,
                "delta_ocupacao_pp": delta_oc,
                "receita_bruta": round(bruta, 2),
                "reservas_estimadas": round(reservas, 1),
                "custo_limpeza": round(limpeza, 2),
                "receita_liquida": round(liq, 2),
                "retorno_bruto_pct": round(ret_b, 2),
                "retorno_liquido_pct": round(ret_l, 2),
                "anos_para_pagar": anos,
            })

    out = pd.DataFrame(linhas)
    out.to_csv(os.path.join(OUT, "sensibilidade.csv"), index=False)

    # ---- ranking dos "melhores grupos" (n>=20, sem alerta) por cenario ----
    validos = out[~out["alerta_n_pequeno"]]
    ranking = {}
    for nome_cen in [c[0] for c in CENARIOS]:
        sub = validos[validos["cenario"] == nome_cen].sort_values(
            "retorno_liquido_pct", ascending=False)
        ranking[nome_cen] = list(zip(sub["bairro"], sub["quartos"], sub["tipo_anuncio"], sub["retorno_liquido_pct"]))

    ordem_ref = ranking["base"]
    top_ref = [(b, q, t) for b, q, t, _ in ordem_ref[:5]]
    mudou = False
    msg = []
    for nome_cen in [c[0] for c in CENARIOS][1:]:
        top_cen = [(b, q, t) for b, q, t, _ in ranking[nome_cen][:5]]
        igual = top_cen == top_ref
        msg.append(f"{nome_cen}: top-5 {'igual' if igual else 'MUDOU'} -> {top_cen}")
        if not igual:
            mudou = True

    print(f"premissas: {P}")
    print(f"segmentos com preco de venda e yield: {n_validos} | linhas em sensibilidade.csv: {len(out)}")
    print(f"salvo em outputs/sensibilidade.csv")
    print()
    print("== TOP-5 grupos por cenario (n>=20; bairro, quartos, tipo, ret.liquido%) ==")
    for nome_cen in [c[0] for c in CENARIOS]:
        print(f"  {nome_cen:<22}" + " | ".join(f"{b}/{q}/{t} {r:.2f}%" for b, q, t, r in ranking[nome_cen][:5]))
    print()
    print("== A ordem dos melhores grupos muda com o cenario? ==")
    for m in msg:
        print("  " + m)
    print("  >>> ORDEM TROCA ENTRE CENARIOS" if mudou else "  >>> ORDEM ESTAVEL (top-5 igual)")


if __name__ == "__main__":
    main()