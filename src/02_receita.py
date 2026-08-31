import os
from collections import defaultdict

import pandas as pd

DATA = "data"
OUT = "outputs"

# ---------------------------------------------------------------------------
# PREMISSAS DE NEGOCIO
# ---------------------------------------------------------------------------
P = {
    # Sem coluna de disponibilidade nos dados. Metodo A: uma noite presente na
    # PRIMEIRA coleta e ausente em coleta posterior conta como VENDA observada
    # entre as coletas (periodo de 6-7 a 20/jan/2025).
    # Uma noite ja ausente na primeira coleta = "nascida ocupada": e tratada a
    # parte (provarelmente bloqueio do dono ou venda anterior) e NAO gera
    # receita, para nao superestimar a alta temporada.
    "tratar_nascida_ocupada_como_bloqueio": True,
    # Janela de observacao = entre a menor e a maior data presente no arquivo
    # do anuncio (aprox. jan-abr/2025). Noites sem preco em nenhuma coleta
    # dentro da janela = "disponiveis" (livres; alem do horizonte de reserva).
    # Ocupacao = vendidas / (vendidas + disponiveis), bloqueio excluido.
    "definicao_ocupacao": "vendidas / (vendidas + disponiveis)",
    # Itapema concentra a receita na alta temporada (jul, dez-mar). Os dados
    # so enxergam jan-abr. Premissa conservadora: jan-abr = 70% da receita
    # anual. Faturamento anual = receita da janela / 0.70.
    # VERIFICAR na secao 9 (sensibilidade): resultados mudam se 0.70 variar.
    "proporcao_receita_janela_4_meses": 0.70,
}

MESES = ["2025-01", "2025-02", "2025-03", "2025-04"]


def main():
    pv = pd.read_csv(os.path.join(DATA, "Price_AV_Itapema.csv"))
    linhas_entrada = len(pv)
    anun_entrada = pv["airbnb_listing_id"].nunique()

    pv = pv.dropna(subset=["date", "price", "aquisition_date"])
    linhas_dropna = linhas_entrada - len(pv)

    pv["date"] = pd.to_datetime(pv["date"], errors="coerce")
    pv["aquisition_date"] = pd.to_datetime(pv["aquisition_date"], format="mixed").dt.normalize()
    pv = pv.sort_values(["airbnb_listing_id", "aquisition_date", "date"])

    snaps_per_listing = pv.groupby("airbnb_listing_id")["aquisition_date"].nunique()
    anun_1_snap = int((snaps_per_listing < 2).sum())
    linhas_1_snap = int(pv["airbnb_listing_id"].isin(
        snaps_per_listing[snaps_per_listing < 2].index).sum())

    linhas = []
    removidos = {"sem_segunda_coleta": 0}

    for lid, g in pv.groupby("airbnb_listing_id", sort=True):
        snaps = sorted(g["aquisition_date"].unique())
        if len(snaps) < 2:
            removidos["sem_segunda_coleta"] += 1
            continue

        # dicionario: noite -> set de dias de coleta em que aparece
        presente = defaultdict(set)
        precos_noite_mes = defaultdict(list)
        for snap, date, price in zip(g["aquisition_date"], g["date"], g["price"]):
            presente[date].add(snap)
            precos_noite_mes[(snap, date.to_period("M"))].append(price)

        janela = pd.date_range(g["date"].min(), g["date"].max(), freq="D")
        snap0, snap_last = snaps[0], snaps[-1]

        # classificacao por noite
        contagem = {"vendidas": 0, "nascidas_ocupadas": 0, "disponiveis": 0}
        vendidas_mes = defaultdict(int)
        disp_mes = defaultdict(int)
        for noite in janela:
            s = presente.get(noite)
            mes = str(noite.to_period("M"))
            if not s:
                contagem["disponiveis"] += 1
                disp_mes[mes] += 1
                continue
            if snap0 not in s:
                contagem["nascidas_ocupadas"] += 1  # ja ocupada na 1a coleta
                continue
            if snap_last in s:
                contagem["disponiveis"] += 1
                disp_mes[mes] += 1
            else:
                contagem["vendidas"] += 1
                vendidas_mes[mes] += 1

        tot_vend = contagem["vendidas"]
        tot_disp = contagem["disponiveis"]
        ocupacao = tot_vend / max(tot_vend + tot_disp, 1)

        # diaria mediana geral e por mes (noites que apareceram em alguma coleta)
        diaria_med = float(g["price"].median())
        diaria_mes = {}
        for mes in MESES:
            vals = [pr for (sn, mm), prs in precos_noite_mes.items()
                    if str(mm) == mes for pr in prs]
            diaria_mes[mes] = float(pd.Series(vals).median()) if vals else float("nan")

        receita_janela = tot_vend * diaria_med
        fat_anual = receita_janela / P["proporcao_receita_janela_4_meses"]

        linha = {
            "airbnb_listing_id": lid,
            "n_snapshots": len(snaps),
            "n_noites_janela": len(janela),
            "vendidas": tot_vend,
            "nascidas_ocupadas": contagem["nascidas_ocupadas"],
            "disponiveis": tot_disp,
            "ocupacao": round(ocupacao, 4),
            "diaria_mediana": diaria_med,
            "receita_janela": round(receita_janela, 2),
            "faturamento_anual": round(fat_anual, 2),
        }
        for mes in MESES:
            linha[f"diaria_mediana_{mes}"] = diaria_mes[mes]
            oc = vendidas_mes[mes] / max(vendidas_mes[mes] + disp_mes[mes], 1)
            linha[f"ocupacao_{mes}"] = round(oc, 4)
        linhas.append(linha)

    out = pd.DataFrame(linhas).dropna(subset=["airbnb_listing_id"])
    out = out.sort_values("faturamento_anual", ascending=False)
    out.to_csv(os.path.join(OUT, "receita_por_listing.csv"), index=False)

    print(f"premissas: {P}")
    print(f"linhas em Price_AV:   {linhas_entrada}")
    print(f"  caidas por data/preco/coleta invalida: {linhas_dropna}")
    print(f"anuncios em Price_AV: {anun_entrada}")
    print(f"  removidos (so 1 coleta, sem transicao): {removidos['sem_segunda_coleta']}")
    print(f"  anuncios com receita calculada: {len(out)}")
    print(f"salvo em outputs/receita_por_listing.csv")
    print(out.head(10).to_string())


if __name__ == "__main__":
    main()