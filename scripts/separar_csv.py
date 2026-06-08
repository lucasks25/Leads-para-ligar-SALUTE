"""
Separa os leads do Instagram em arquivos CSV por curso e por mês.
Uso: python3 scripts/separar_csv.py
"""
import csv
import os
from datetime import datetime
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE = os.path.join(BASE_DIR, "Cadastros_no_Instagram.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "Leads_Separados")

MESES_PT = {
    1: "01_Janeiro", 2: "02_Fevereiro", 3: "03_Marco", 4: "04_Abril",
    5: "05_Maio", 6: "06_Junho", 7: "07_Julho", 8: "08_Agosto",
    9: "09_Setembro", 10: "10_Outubro", 11: "11_Novembro", 12: "12_Dezembro"
}

COLUNAS_PT = {
    "Form Name": "Campanha",
    "Qual o curso que você tem interesse?": "Curso",
    "Full name": "Nome",
    "Email": "Email",
    "Phone number": "Telefone",
    "Created Time": "Data de Cadastro",
    "Campaign Name": "Nome da Campanha",
    "Stage Name": "Etapa",
}


def nome_seguro(texto):
    chars = r'\/:*?"<>|'
    for c in chars:
        texto = texto.replace(c, "_")
    return texto.strip() or "Sem_Nome"


def ler_csv():
    rows = []
    with open(INPUT_FILE, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for r in reader:
            data_raw = r.get("Created Time", "")
            try:
                dt = datetime.fromisoformat(data_raw)
                r["Created Time"] = dt.strftime("%d/%m/%Y %H:%M")
                r["_mes_pasta"] = f"{MESES_PT[dt.month]}_{dt.year}"
                r["_mes_sort"] = dt.strftime("%Y-%m")
            except Exception:
                r["_mes_pasta"] = "Sem_Data"
                r["_mes_sort"] = "9999-99"
            rows.append(r)
    return rows, fieldnames


def escrever_csv(caminho, rows, fieldnames):
    colunas_pt = [COLUNAS_PT.get(f, f) for f in fieldnames]
    with open(caminho, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(colunas_pt)
        for r in rows:
            writer.writerow([r.get(col, "") for col in fieldnames])


def main():
    print(f"Lendo: {INPUT_FILE}")
    rows, fieldnames = ler_csv()
    fieldnames = [f for f in fieldnames if not f.startswith("_")]
    print(f"Total de leads: {len(rows)}")

    # Agrupa por curso
    por_curso = defaultdict(list)
    for r in rows:
        curso = r.get("Qual o curso que você tem interesse?", "").strip() or "Sem Curso"
        por_curso[curso].append(r)

    # Agrupa por mês
    por_mes = defaultdict(list)
    for r in rows:
        por_mes[(r["_mes_sort"], r["_mes_pasta"])].append(r)

    # Pasta por curso
    pasta_cursos = os.path.join(OUTPUT_DIR, "Por_Curso")
    os.makedirs(pasta_cursos, exist_ok=True)
    for curso, leads in sorted(por_curso.items(), key=lambda x: -len(x[1])):
        nome = nome_seguro(curso)
        caminho = os.path.join(pasta_cursos, f"{nome}.csv")
        escrever_csv(caminho, leads, fieldnames)
        print(f"  {nome}.csv — {len(leads)} leads")

    # Pasta por mês
    pasta_meses = os.path.join(OUTPUT_DIR, "Por_Mes")
    os.makedirs(pasta_meses, exist_ok=True)
    for (sort_key, mes_pasta), leads in sorted(por_mes.items(), key=lambda x: x[0][0]):
        nome = nome_seguro(mes_pasta)
        caminho = os.path.join(pasta_meses, f"{nome}.csv")
        leads_ord = sorted(leads, key=lambda r: r["_mes_sort"])
        escrever_csv(caminho, leads_ord, fieldnames)
        print(f"  {nome}.csv — {len(leads)} leads")

    print(f"\nPastas geradas em: {OUTPUT_DIR}")
    print(f"  Por_Curso/ — {len(por_curso)} arquivos")
    print(f"  Por_Mes/   — {len(por_mes)} arquivos")


if __name__ == "__main__":
    main()
