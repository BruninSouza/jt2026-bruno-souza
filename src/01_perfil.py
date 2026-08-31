import os
import pandas as pd

DATA = "data"
OUT = "outputs"

FILE_COLS = {
    "Details_Itapema.csv": ["price", "homeType", "bedrooms", "source", "lat", "lon", "listing_id"],
    "Hosts_ids_Itapema.csv": ["host_id", "listing_id"],
    "Mesh_Ids_Data_Itapema.csv": ["mesh_id", "listing_id"],
    "Price_AV_Itapema.csv": ["price", "date", "collected", "listing_id"],
    "VivaReal_Itapema.csv": ["logo_name", "price", "listing_id"],
}

LINK_COLS = {
    "listing_id": ["listing_id"],
    "host_id": ["host_id", "listing_id"],
    "mesh_id": ["mesh_id", "listing_id"],
}

PREMIss_a_disp = (
    "Sem coluna de disponibilidade nos dados; tratamos 'ausencia de linha na Price_AV' "
    "(a partir do primeiro e ate o ultimo date presente) como noite LIVRE."
)

bairros = ["neighborhood", "bairro", "district", "address", "listing_name"]


def col_tipo(vals):
    if pd.api.types.is_integer_dtype(vals):
        return "int"
    if pd.api.types.is_float_dtype(vals):
        return "float"
    if pd.api.types.is_bool_dtype(vals):
        return "bool"
    if pd.api.types.is_datetime64_any_dtype(vals):
        return "datetime"
    return "object"


def resumo(df, nome):
    print("====", nome, "====")
    print("linhas:", len(df))
    print("colunas:", list(df.columns))
    for c in df.columns:
        print(f"  {c}: {col_tipo(df[c])} faltando={df[c].isna().mean()*100:.1f}%")
    print()


def links(dfs):
    print("==== LIGACOES ====")
    nomes = list(dfs)
    for i, a in enumerate(nomes):
        for b in nomes[i + 1:]:
            da, db = dfs[a], dfs[b]
            comun = [c for c in da.columns if c in db.columns]
            if not comun:
                print(f"{a} <-> {b}: sem coluna comum")
                continue
            for c in comun:
                sa = set(da[c].dropna())
                sb = set(db[c].dropna())
                n = len(sa & sb)
                print(f"{a} <-> {b} [{c}]: {n} casam "
                      f"({100*n/max(len(sa),1):.1f}% em {a}, {100*n/max(len(sb),1):.1f}% em {b})")
    print()


def preco_data(df):
    print("==== PRICE_AV: COLUNAS-CHAVE ====")
    for c in df.columns:
        if "listarea" in c.lower() or "collect" in c.lower() or "scrapp" in c.lower() or "crawl" in c.lower():
            print(f"  {c}: FAKE-DE-DATA (coleta)")
        elif c.lower() == "date" or "diaria" in c.lower() or c.lower().startswith("data") or c.lower().startswith("dt"):
            print(f"  {c}: FAKE-DE-DATA (diaria)")
        elif c.lower() in ("price", "preco") or "price" in c.lower():
            print(f"  {c}: PRECO")
    print("valores unicos em price:", df["price"].dropna().unique()[:5] if "price" in df.columns else "-")
    print("valores unicos em date:", df["date"].dropna().unique()[:5] if "date" in df.columns else "-")
    print()


def bairro(df):
    print("==== BAIRROS ====")
    col = next((c for c in df.columns if c.lower() in ("neighborhood", "bairro", "district")), None)
    if col:
        print("coluna de bairro:", col)
        print(df[col].value_counts())
    else:
        print("nenhuma coluna obvia de bairro; amostra das colunas textuals:")
        for c in df.columns:
            if df[c].dtype == object:
                print("  ", c, df[c].dropna().unique()[:10])
    print()


def periodo(df):
    print("==== PERIODO ====")
    for c in df.columns:
        if c in ("date", "collect") or "collect" in c.lower() or ("date" in c.lower() and df[c].dtype in (object, "datetime64[ns]")):
            s = pd.to_datetime(df[c], errors="coerce", format="mixed")
            print(f"  {c}: {s.min()} a {s.max()}")
    print()


def main():
    os.makedirs(OUT, exist_ok=True)
    dfs = {f: pd.read_csv(os.path.join(DATA, f)) for f in FILE_COLS}
    with open(os.path.join(OUT, "perfil_dados.txt"), "w", encoding="utf-8") as f:
        import contextlib, sys
        orig = sys.stdout
        sys.stdout = f
        for nome in FILE_COLS:
            resumo(dfs[nome], nome)
        links(dfs)
        preco_data(dfs["Price_AV_Itapema.csv"])
        bairro(dfs["Details_Itapema.csv"])
        periodo(dfs["Price_AV_Itapema.csv"])
        sys.stdout = orig
    print("salvo em outputs/perfil_dados.txt")


if __name__ == "__main__":
    main()