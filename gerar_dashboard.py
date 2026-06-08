import csv
import json
import os
import glob
from datetime import datetime

PASTA_CURSOS = "Leads_Separados/Por_Curso"
SAIDA = "index.html"

cursos_cor = {
    "Sem Curso": "#ef4444",
    "Téc. Radiologia": "#8b5cf6",
    "Téc. Enfermagem": "#3b82f6",
    "Aux. Enfermagem": "#06b6d4",
    "Estética": "#ec4899",
    "Seguraça do Trabalho": "#f59e0b",
    "Cuidador de idosos": "#10b981",
    "Bombeiro Civil": "#f97316",
    "Reciclagem de Bombeiro": "#ef4444",
    "Portaria": "#6b7280",
    "Auxiliar de Classe": "#84cc16",
    "Berçarista": "#a78bfa",
    "Enfermagem do Trabalho": "#0ea5e9",
    "Tec. Administração": "#d97706",
    "Outros": "#9ca3af",
}

todos_leads = []
leads_vistos = set()

for arquivo in glob.glob(os.path.join(PASTA_CURSOS, "*.csv")):
    nome_curso = os.path.splitext(os.path.basename(arquivo))[0]
    with open(arquivo, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            telefone = row.get("Telefone", "").strip()
            # Formata telefone para WhatsApp (remove +, espaços)
            tel_wa = telefone.replace("+", "").replace(" ", "").replace("-", "")
            email = row.get("Email", "").strip()
            nome = row.get("Nome", "").strip()
            
            identificador = tel_wa or email or nome
            if identificador and identificador in leads_vistos:
                continue
            if identificador:
                leads_vistos.add(identificador)
            data_str = row.get("Data de Cadastro", "").strip()
            try:
                data_obj = datetime.strptime(data_str, "%d/%m/%Y %H:%M")
                data_fmt = data_obj.strftime("%d/%m/%Y")
                mes_ano = data_obj.strftime("%m/%Y")
                data_iso = data_obj.isoformat()
            except:
                data_fmt = data_str
                mes_ano = ""
                data_iso = ""

            curso = row.get("Curso", "").strip() or "Sem Curso"
            todos_leads.append({
                "nome": row.get("Nome", "").strip(),
                "email": row.get("Email", "").strip(),
                "telefone": telefone,
                "tel_wa": tel_wa,
                "curso": curso,
                "data": data_fmt,
                "data_iso": data_iso,
                "mes_ano": mes_ano,
                "etapa": row.get("Etapa", "").strip(),
                "campanha": row.get("Campanha", "").strip(),
            })

# Ordena por data decrescente
todos_leads.sort(key=lambda x: x["data_iso"], reverse=True)

# Stats
from collections import Counter
por_curso = Counter(l["curso"] for l in todos_leads)
por_mes = Counter(l["mes_ano"] for l in todos_leads if l["mes_ano"])

cursos_lista = sorted(por_curso.items(), key=lambda x: -x[1])
meses_lista = sorted(por_mes.items())

leads_json = json.dumps(todos_leads, ensure_ascii=False)
cores_json = json.dumps(cursos_cor, ensure_ascii=False)

HTML = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Salute — Gestão de Leads</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root {{
    --blue:       #005eff;
    --blue-nav:   #003bb5;
    --blue-deep:  #002880;
    --blue-soft:  #eef4ff;
    --blue-mist:  #dce8ff;
    --blue-ring:  rgba(0,94,255,.15);
    --text:       #0c1a3a;
    --text-2:     #3d5280;
    --text-3:     #8494b0;
    --border:     #d6e0f7;
    --bg:         #eef4ff;
    --surface:    #ffffff;
    --red:        #d63030;
    --red-bg:     #fff2f2;
    --red-border: #ffc9c9;
    --green:      #15803d;
  }}

  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Inter', system-ui, sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; font-size: 14px; line-height: 1.5; }}

  /* ── HEADER ── */
  .header {{
    background: var(--blue-nav);
    padding: 0 40px;
    height: 60px;
    display: flex;
    align-items: center;
    gap: 16px;
    position: sticky;
    top: 0;
    z-index: 20;
    box-shadow: 0 2px 12px rgba(0,40,128,.35);
  }}
  .logo {{ display: flex; align-items: center; gap: 10px; text-decoration: none; flex-shrink: 0; }}
  .logo-mark {{
    width: 34px; height: 34px;
    background: rgba(255,255,255,.15);
    border: 1px solid rgba(255,255,255,.25);
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    color: #fff; font-weight: 800; font-size: 0.82rem; letter-spacing: -0.03em;
    flex-shrink: 0;
  }}
  .logo-text {{ display: flex; flex-direction: column; line-height: 1.2; }}
  .logo-name  {{ font-size: 0.85rem; font-weight: 700; color: #fff; letter-spacing: -0.01em; white-space: nowrap; }}
  .logo-sub   {{ font-size: 0.58rem; font-weight: 500; color: rgba(255,255,255,.5); text-transform: uppercase; letter-spacing: 0.07em; }}
  .header-right {{ margin-left: auto; display: flex; align-items: center; gap: 24px; flex-shrink: 0; }}
  .hstat {{ text-align: center; }}
  .hstat .n {{ font-size: 1.05rem; font-weight: 700; color: #fff; letter-spacing: -0.02em; line-height: 1; }}
  .hstat .l {{ font-size: 0.58rem; font-weight: 500; color: rgba(255,255,255,.5); text-transform: uppercase; letter-spacing: 0.07em; margin-top: 2px; }}
  .hstat.danger .n {{ color: #ffaaaa; }}
  .header-div {{ width: 1px; height: 24px; background: rgba(255,255,255,.15); }}

  /* ── CONTAINER ── */
  .container {{ max-width: 1320px; margin: 0 auto; padding: 28px 40px; }}

  /* ── BANNER ── */
  .banner {{
    background: linear-gradient(120deg, var(--blue-deep) 0%, var(--blue-nav) 55%, var(--blue) 100%);
    border-radius: 14px;
    padding: 28px 32px;
    margin-bottom: 32px;
    display: flex;
    align-items: center;
    gap: 28px;
    color: #fff;
    overflow: hidden;
    position: relative;
  }}
  .banner::after {{
    content: '';
    position: absolute;
    right: -80px; top: -80px;
    width: 260px; height: 260px;
    border-radius: 50%;
    background: rgba(255,255,255,.04);
    pointer-events: none;
  }}
  .banner-icon {{
    width: 48px; height: 48px;
    background: rgba(255,255,255,.12);
    border: 1px solid rgba(255,255,255,.2);
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px; flex-shrink: 0;
  }}
  .banner-text {{ flex: 1; min-width: 0; }}
  .banner-text h2  {{ font-size: 1.1rem; font-weight: 700; letter-spacing: -0.02em; }}
  .banner-text p   {{ font-size: 0.8rem; color: rgba(255,255,255,.6); margin-top: 5px; line-height: 1.5; }}
  .banner-stats    {{ display: flex; gap: 0; align-items: stretch; flex-shrink: 0; background: rgba(255,255,255,.08); border-radius: 10px; overflow: hidden; }}
  .bstat           {{ text-align: center; padding: 14px 24px; }}
  .bstat .n        {{ font-size: 1.8rem; font-weight: 800; letter-spacing: -0.04em; line-height: 1; }}
  .bstat .l        {{ font-size: 0.6rem; color: rgba(255,255,255,.55); text-transform: uppercase; letter-spacing: 0.08em; margin-top: 4px; font-weight: 500; white-space: nowrap; }}
  .bstat-div       {{ width: 1px; background: rgba(255,255,255,.12); }}

  /* ── SECTION LABEL ── */
  .slabel {{ font-size: 0.67rem; font-weight: 700; color: var(--text-3); text-transform: uppercase; letter-spacing: 0.12em; margin-bottom: 12px; }}

  /* ── STAT CARDS ── */
  .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(148px, 1fr)); gap: 10px; margin-bottom: 32px; }}
  .stat-card {{
    background: var(--surface);
    border: 1.5px solid var(--border);
    border-radius: 10px;
    padding: 16px 18px;
    cursor: pointer;
    transition: border-color .15s, box-shadow .15s, transform .12s;
    box-shadow: 0 1px 4px rgba(0,60,180,.06);
  }}
  .stat-card:hover {{ border-color: #a8bff7; box-shadow: 0 4px 14px rgba(0,60,180,.1); transform: translateY(-2px); }}
  .stat-card.active {{
    border-color: var(--blue);
    background: var(--blue-soft);
    box-shadow: 0 0 0 3px var(--blue-ring), 0 4px 12px rgba(0,60,180,.1);
  }}
  .stat-card.active .snum {{ color: var(--blue); }}
  .stat-card.active .slbl {{ color: var(--blue-nav); opacity: 0.9; }}
  .snum {{ font-size: 1.7rem; font-weight: 700; color: var(--text); letter-spacing: -0.04em; line-height: 1; margin-bottom: 8px; }}
  .slbl {{ font-size: 0.72rem; color: var(--text-3); font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: flex; align-items: center; gap: 0; }}
  .cdot {{ display: inline-block; width: 7px; height: 7px; border-radius: 50%; background: var(--cor, var(--border)); margin-right: 6px; flex-shrink: 0; }}
  .stat-card.warn {{ border-color: var(--red-border); }}
  .stat-card.warn .snum {{ color: var(--red); }}
  .stat-card.warn .slbl {{ color: var(--red); opacity: 0.85; }}
  .stat-card.warn.active {{ background: var(--red-bg); border-color: var(--red); box-shadow: 0 0 0 3px rgba(214,48,48,.12); }}

  /* ── NOTICE ── */
  .notice {{
    background: var(--red-bg);
    border: 1.5px solid var(--red-border);
    border-left: 4px solid var(--red);
    border-radius: 10px;
    padding: 14px 20px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 14px;
  }}
  .notice p {{ font-size: 0.83rem; color: var(--text-2); line-height: 1.5; }}
  .notice strong {{ color: var(--red); font-weight: 600; }}
  .notice-btn {{ margin-left: auto; font-size: 0.75rem; color: var(--red); font-weight: 600; background: none; border: 1.5px solid var(--red-border); padding: 6px 14px; border-radius: 7px; cursor: pointer; white-space: nowrap; transition: background .15s; flex-shrink: 0; font-family: inherit; }}
  .notice-btn:hover {{ background: #ffe0e0; }}

  /* ── TOOLBAR ── */
  .toolbar {{ display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-bottom: 14px; }}
  .search-wrap {{ position: relative; flex: 1; min-width: 200px; max-width: 310px; }}
  .search-wrap svg {{ position: absolute; left: 10px; top: 50%; transform: translateY(-50%); width: 14px; height: 14px; color: var(--text-3); pointer-events: none; }}
  input[type=text] {{ width: 100%; background: var(--surface); border: 1.5px solid var(--border); color: var(--text); padding: 8px 10px 8px 32px; border-radius: 8px; font-size: 0.83rem; font-family: inherit; outline: none; transition: border-color .15s, box-shadow .15s; line-height: 1.4; }}
  input[type=text]::placeholder {{ color: var(--text-3); }}
  input[type=text]:focus {{ border-color: var(--blue); box-shadow: 0 0 0 3px var(--blue-ring); }}
  select {{ background: var(--surface); border: 1.5px solid var(--border); color: var(--text-2); padding: 8px 28px 8px 10px; border-radius: 8px; font-size: 0.83rem; font-family: inherit; outline: none; cursor: pointer; appearance: none; -webkit-appearance: none; background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%238494b0' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E"); background-repeat: no-repeat; background-position: right 8px center; transition: border-color .15s, box-shadow .15s; }}
  select:focus {{ border-color: var(--blue); box-shadow: 0 0 0 3px var(--blue-ring); }}
  .btn-clear {{ background: var(--surface); border: 1.5px solid var(--border); border-radius: 8px; font-size: 0.78rem; color: var(--text-3); cursor: pointer; padding: 8px 14px; font-family: inherit; transition: all .15s; }}
  .btn-clear:hover {{ border-color: #a8bff7; color: var(--blue-nav); }}
  .toolbar-right {{ margin-left: auto; }}
  .tcount {{ font-size: 0.78rem; color: var(--text-3); font-weight: 500; }}
  .tcount b {{ color: var(--blue-nav); font-weight: 700; }}

  /* ── TABLE ── */
  .table-wrap {{ background: var(--surface); border: 1.5px solid var(--border); border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,60,180,.06); }}
  table {{ width: 100%; border-collapse: collapse; }}
  thead {{ background: var(--blue-soft); }}
  th {{ padding: 12px 18px; text-align: left; font-size: 0.67rem; font-weight: 700; color: var(--blue-nav); text-transform: uppercase; letter-spacing: 0.09em; border-bottom: 1.5px solid var(--blue-mist); }}
  td {{ padding: 14px 18px; border-bottom: 1px solid var(--blue-mist); vertical-align: middle; line-height: 1.4; }}
  tr:last-child td {{ border-bottom: none; }}
  tbody tr {{ transition: background .1s; }}
  tbody tr:nth-child(even) td {{ background: #f6f9ff; }}
  tbody tr:hover td {{ background: var(--blue-mist) !important; }}
  tbody tr.sem-curso td {{ background: #fff5f5; }}
  tbody tr.sem-curso:hover td {{ background: #ffe8e8 !important; }}

  .idx  {{ color: #c8d5ee; font-size: 0.7rem; font-variant-numeric: tabular-nums; width: 36px; }}
  .nome {{ font-weight: 600; color: var(--text); font-size: 0.86rem; line-height: 1.3; }}
  .sub  {{ font-size: 0.73rem; color: var(--text-3); margin-top: 3px; }}
  .pill {{ display: inline-flex; align-items: center; gap: 5px; padding: 4px 10px; border-radius: 5px; font-size: 0.71rem; font-weight: 600; line-height: 1; }}
  .pill-dot {{ width: 5px; height: 5px; border-radius: 50%; flex-shrink: 0; }}
  .warn-tag {{ font-size: 0.67rem; color: var(--red); font-weight: 500; display: inline-block; margin-left: 6px; white-space: nowrap; }}
  .tel  {{ font-size: 0.81rem; color: var(--text-2); font-variant-numeric: tabular-nums; white-space: nowrap; }}
  .date {{ font-size: 0.77rem; color: var(--text-3); white-space: nowrap; font-variant-numeric: tabular-nums; }}
  .tag-nc {{ display: inline-block; background: #fff8e6; border: 1px solid #ffd970; color: #7a5200; padding: 3px 10px; border-radius: 5px; font-size: 0.68rem; font-weight: 600; white-space: nowrap; }}
  .tag-ok {{ display: inline-block; background: #edfff5; border: 1px solid #6ee7a8; color: #0d5c2f; padding: 3px 10px; border-radius: 5px; font-size: 0.68rem; font-weight: 600; white-space: nowrap; }}

  .btn-wa {{ display: inline-flex; align-items: center; justify-content: center; background: #16a34a; color: #fff; border: none; width: 32px; height: 32px; border-radius: 8px; cursor: pointer; text-decoration: none; transition: background .15s, box-shadow .15s; flex-shrink: 0; }}
  .btn-wa:hover {{ background: #15803d; box-shadow: 0 3px 8px rgba(21,128,61,.3); }}
  .btn-wa svg {{ flex-shrink: 0; }}
  .btn-wa-off {{ display: inline-block; width: 32px; text-align: center; color: #c8d5ee; font-size: 0.9rem; }}

  /* ── MODAL CRM ── */
  .modal-overlay {{ position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,24,64,.5); display: none; align-items: center; justify-content: center; z-index: 100; backdrop-filter: blur(2px); }}
  .modal {{ background: var(--surface); width: 100%; max-width: 400px; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,30,80,.15); padding: 24px; position: relative; }}
  .modal h3 {{ font-size: 1.1rem; color: var(--text); margin-bottom: 6px; }}
  .modal p.m-sub {{ font-size: 0.8rem; color: var(--text-3); margin-bottom: 20px; }}
  .modal-close {{ position: absolute; top: 16px; right: 16px; background: none; border: none; font-size: 1.2rem; color: var(--text-3); cursor: pointer; }}
  .form-group {{ margin-bottom: 16px; }}
  .form-group label {{ display: block; font-size: 0.75rem; font-weight: 600; color: var(--text-2); margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.05em; }}
  .form-group select, .form-group textarea {{ width: 100%; background: #f6f9ff; border: 1.5px solid var(--border); color: var(--text); border-radius: 8px; padding: 10px 12px; font-family: inherit; font-size: 0.85rem; outline: none; transition: border-color .15s; }}
  .form-group select:focus, .form-group textarea:focus {{ border-color: var(--blue); background: #fff; }}
  .form-group textarea {{ resize: vertical; min-height: 80px; }}
  .btn-save {{ background: var(--blue); color: #fff; border: none; width: 100%; padding: 12px; border-radius: 8px; font-weight: 600; font-size: 0.9rem; cursor: pointer; transition: background .15s; }}
  .btn-save:hover {{ background: var(--blue-nav); }}
  .btn-export {{ background: #fff; border: 1.5px solid var(--blue-mist); color: var(--blue-nav); padding: 8px 14px; border-radius: 8px; font-size: 0.78rem; font-weight: 600; cursor: pointer; transition: all .15s; display: inline-flex; align-items: center; gap: 6px; }}
  .btn-export:hover {{ border-color: var(--blue); background: var(--blue-soft); }}
  .btn-crm {{ display: inline-flex; align-items: center; justify-content: center; background: transparent; color: #cbd5e1; border: 1px solid transparent; width: 32px; height: 32px; border-radius: 8px; cursor: pointer; transition: all .15s; margin-left: 6px; }}
  .btn-crm:hover {{ background: #f8fafc; color: #64748b; border-color: #e2e8f0; }}
  .btn-crm.has-notes {{ color: var(--blue); background: var(--blue-soft); }}
  .btn-crm.has-notes:hover {{ background: #dbeafe; }}
  
  .crm-nao_respondeu {{ background: #f3f4f6; border: 1px solid #d1d5db; color: #4b5563; }}
  .crm-em_negociacao {{ background: #fef08a; border: 1px solid #fde047; color: #854d0e; }}
  .crm-contatado {{ background: #e0e7ff; border: 1px solid #a5b4fc; color: #3730a3; }}

  /* ── EMPTY ── */
  .empty {{ text-align: center; padding: 60px 20px; color: var(--text-3); }}
  .empty p {{ font-size: 0.85rem; }}

  /* ── PAGINATION ── */
  .pagination {{ display: flex; align-items: center; justify-content: center; gap: 4px; padding: 20px; }}
  .pg {{ background: var(--surface); border: 1.5px solid var(--border); color: var(--text-2); padding: 6px 12px; border-radius: 7px; font-size: 0.8rem; cursor: pointer; font-family: inherit; transition: all .15s; min-width: 36px; }}
  .pg:hover:not(:disabled) {{ border-color: var(--blue); color: var(--blue); background: var(--blue-soft); }}
  .pg.on {{ background: var(--blue); border-color: var(--blue); color: #fff; font-weight: 700; box-shadow: 0 2px 8px rgba(0,94,255,.3); }}
  .pg:disabled {{ opacity: 0.3; cursor: not-allowed; }}

  @media (max-width: 900px) {{
    .header {{ padding: 0 20px; }}
    .container {{ padding: 24px 20px; }}
    .banner {{ flex-wrap: wrap; gap: 20px; padding: 22px 24px; }}
    .banner-text {{ min-width: 100%; }}
    .banner-stats {{ width: 100%; }}
    .bstat {{ flex: 1; }}
    .stats-grid {{ grid-template-columns: repeat(3, 1fr); }}
    .search-wrap {{ max-width: none; }}
  }}
  @media (max-width: 768px) {{
    .stats-grid {{ grid-template-columns: repeat(2, 1fr); }}
    .toolbar {{ flex-direction: column; align-items: stretch; gap: 12px; }}
    .toolbar-right {{ margin-left: 0; margin-top: 8px; }}
    
    .table-wrap {{ border: none; background: transparent; padding: 0; box-shadow: none; }}
    table, thead, tbody, th, td, tr {{ display: block; }}
    thead {{ display: none; }}
    tr {{ margin-bottom: 16px; background: #fff; border: 1.5px solid var(--border); border-radius: 12px; padding: 16px; position: relative; box-shadow: 0 4px 12px rgba(0,0,0,0.02); }}
    td {{ border-bottom: none !important; padding: 0 !important; display: block; }}
    
    .td-idx {{ display: none; }}
    .td-nome {{ padding-right: 80px !important; margin-bottom: 8px; }}
    .td-nome .nome {{ font-size: 1.15rem; color: var(--text); }}
    .td-nome .sub {{ display: none; }}
    .td-curso {{ margin-bottom: 6px; }}
    .td-tel {{ margin-bottom: 6px; font-size: 0.85rem; color: var(--text-2); font-weight: 500; }}
    .td-tel::before {{ content: "📱 "; }}
    .td-email {{ margin-bottom: 12px; font-size: 0.85rem; color: var(--text-2); word-break: break-all; }}
    .td-email::before {{ content: "✉️ "; }}
    .td-data {{ display: inline-block; font-size: 0.75rem; color: var(--text-3); background: #f1f5f9; padding: 4px 8px; border-radius: 6px; margin-bottom: 12px; }}
    .td-etapa {{ display: block; border-top: 1.5px dashed var(--border); padding-top: 14px !important; margin-top: 4px; }}
    .td-actions {{ position: absolute; top: 16px; right: 16px; margin: 0; }}
  }}
  @media (max-width: 600px) {{
    .header {{ padding: 0 16px; height: 54px; }}
    .logo-sub {{ display: none; }}
    .stats-grid {{ grid-template-columns: repeat(2, 1fr); }}
    .toolbar {{ flex-direction: column; align-items: stretch; }}
    .toolbar-right {{ margin-left: 0; }}
  }}
  @media (max-width: 480px) {{
    .stats-grid {{ grid-template-columns: 1fr; }}
  }}
</style>
</head>
<body>

<div class="header">
  <div class="logo">
    <div class="logo-mark">CE</div>
    <div class="logo-text">
      <span class="logo-name">Centro Educacional Salute</span>
      <span class="logo-sub">Captação de Leads</span>
    </div>
  </div>
  <div class="header-div"></div>
  <div class="header-right">
    <div class="hstat">
      <div class="n">{len(todos_leads)}</div>
      <div class="l">Leads</div>
    </div>
    <div class="hstat danger">
      <div class="n">{por_curso.get('Sem Curso', 0)}</div>
      <div class="l">Sem curso</div>
    </div>
  </div>
</div>

<div class="container">

  <!-- BANNER -->
  <div class="banner">
    <div class="banner-icon">🎓</div>
    <div class="banner-text">
      <h2>Painel de Captação de Leads</h2>
      <p>Visualize seus contatos, filtre por curso ou período e inicie conversas no WhatsApp com um clique.</p>
    </div>
    <div class="banner-stats">
      <div class="bstat">
        <div class="n">{len(todos_leads)}</div>
        <div class="l">Total de leads</div>
      </div>
      <div class="bstat-div"></div>
      <div class="bstat">
        <div class="n">{len(cursos_lista) - 1}</div>
        <div class="l">Cursos</div>
      </div>
      <div class="bstat-div"></div>
      <div class="bstat">
        <div class="n">{por_curso.get('Sem Curso', 0)}</div>
        <div class="l">Sem curso</div>
      </div>
    </div>
  </div>

  <p class="slabel">Leads por curso — clique para filtrar</p>
  <div class="stats-grid" id="statsGrid">
    <div class="stat-card active" onclick="filtrarCurso('')" id="card-all">
      <div class="snum">{len(todos_leads)}</div>
      <div class="slbl"><span class="cdot" style="--cor:var(--blue)"></span>Todos os leads</div>
    </div>
"""

for curso, qtd in cursos_lista:
    cor = cursos_cor.get(curso, "#6b7280")
    curso_js = curso.replace("'", "\\'")
    card_id = curso.replace(' ','-').replace('.','').replace('/','').replace('(','').replace(')','').replace("'","")
    warn_cls = ' warn' if curso == "Sem Curso" else ""
    HTML += f"""    <div class="stat-card{warn_cls}" onclick="filtrarCurso('{curso_js}')" id="card-{card_id}">
      <div class="snum">{qtd}</div>
      <div class="slbl"><span class="cdot" style="--cor:{cor}"></span>{curso}</div>
    </div>
"""

HTML += f"""  </div>

  <!-- NOTICE -->
  <div class="notice">
    <p><strong>{por_curso.get('Sem Curso', 0)} leads sem curso definido.</strong> Esses contatos se cadastraram sem escolher um curso. Vale entrar em contato via WhatsApp para entender o interesse e apresentar as opções.</p>
    <button class="notice-btn" onclick="filtrarCurso('Sem Curso')">Ver lista →</button>
  </div>

  <!-- TOOLBAR -->
  <div class="toolbar">
    <div class="search-wrap">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
      <input type="text" id="busca" placeholder="Buscar por nome, email ou telefone…" oninput="aplicarFiltros()">
    </div>
    <select id="filtroCurso" onchange="aplicarFiltros()">
      <option value="">Todos os cursos</option>
"""

for curso, _ in cursos_lista:
    HTML += f'        <option value="{curso}">{curso}</option>\n'

HTML += f"""    </select>
    <select id="filtroMes" onchange="aplicarFiltros()">
      <option value="">Todos os meses</option>
"""

meses_nome = {
    "03": "Março", "04": "Abril", "05": "Maio", "06": "Junho"
}
for mes_ano, qtd in sorted(meses_lista, reverse=True):
    if "/" in mes_ano:
        m, a = mes_ano.split("/")
        label = f"{meses_nome.get(m, m)}/{a} ({qtd})"
        HTML += f'      <option value="{mes_ano}">{label}</option>\n'

HTML += f"""    </select>
    <div style="display:inline-flex;align-items:center;gap:4px;margin-left:8px;margin-right:8px;">
      <span style="font-size:0.8rem;color:var(--text-3);font-weight:500;">De</span>
      <input type="date" id="dataInicio" onchange="aplicarFiltros()" style="border:1.5px solid var(--border);border-radius:6px;padding:4px;font-size:0.8rem;color:var(--text);font-family:inherit;">
      <span style="font-size:0.8rem;color:var(--text-3);font-weight:500;">Até</span>
      <input type="date" id="dataFim" onchange="aplicarFiltros()" style="border:1.5px solid var(--border);border-radius:6px;padding:4px;font-size:0.8rem;color:var(--text);font-family:inherit;">
    </div>
    <button class="btn-clear" onclick="limparFiltros()">Limpar filtros</button>
    <button class="btn-export" onclick="document.getElementById('importCsv').click()">📤 Importar Leads (CSV)</button>
    <input type="file" id="importCsv" accept=".csv" style="display:none" onchange="importarLeads(event)">
    <div class="toolbar-right">
      <div class="tcount"><b id="countNum">0</b> resultados</div>
    </div>
  </div>

  <!-- TABELA -->
  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th style="width:40px">#</th>
          <th>Nome</th>
          <th>Curso</th>
          <th>Telefone</th>
          <th class="hide-sm">Email</th>
          <th>Data</th>
          <th class="hide-sm">Etapa</th>
          <th></th>
        </tr>
      </thead>
      <tbody id="tabelaBody"></tbody>
    </table>
    <div id="emptyState" class="empty" style="display:none">
      <p>Nenhum lead encontrado.</p>
    </div>
  </div>

  <div class="pagination" id="paginacao"></div>

  <div style="text-align:center; padding: 30px 20px 40px 20px; margin-top: 20px; border-top: 1px dashed var(--border);">
    <button onclick="exportarCRM()" style="background:transparent;border:none;color:var(--text-3);font-size:0.75rem;cursor:pointer;transition:color .15s;" onmouseover="this.style.color='var(--text-2)'" onmouseout="this.style.color='var(--text-3)'">📥 Exportar Backup CRM e Leads Importados</button>
  </div>

  <div id="modalCRM" class="modal-overlay">
    <div class="modal">
      <button class="modal-close" onclick="fecharModal()">×</button>
      <h3 id="modalNome">Nome do Lead</h3>
      <p class="m-sub" id="modalIdentificador">Telefone/Email</p>
      
      <div class="form-group">
        <label>Status da Negociação</label>
        <select id="crmStatus">
          <option value="">Apenas Contatado (Sem status)</option>
          <option value="Em negociação">Em negociação</option>
          <option value="Fechou">Fechou</option>
          <option value="Recusou">Recusou</option>
          <option value="Não Respondeu">Não Respondeu</option>
        </select>
      </div>
      
      <div class="form-group">
        <label>Anotações</label>
        <textarea id="crmNotas" placeholder="Descreva como foi a conversa..."></textarea>
      </div>
      
      <button class="btn-save" onclick="salvarCRM()">Salvar no Navegador</button>
    </div>
  </div>

</div>

<script>
const LEADS = {leads_json};
const CORES = {cores_json};
const POR_PAG = 50;
let paginaAtual = 1;

// LocalStorage CRM e Leads Importados
const CRM_KEY = 'salute_crm_leads';
let CRM_DATA = JSON.parse(localStorage.getItem(CRM_KEY) || '{{}}');
let IMPORTED_LEADS = JSON.parse(localStorage.getItem('salute_imported_leads') || '[]');

let telefones_vistos = new Set(LEADS.map(l => l.tel_wa).filter(Boolean));
let emails_vistos = new Set(LEADS.map(l => l.email).filter(Boolean));

let leads_combinados = [...LEADS];
IMPORTED_LEADS.forEach(l => {{
  if (l.tel_wa && telefones_vistos.has(l.tel_wa)) return;
  if (l.email && emails_vistos.has(l.email)) return;
  leads_combinados.push(l);
}});

let leadsFiltrados = [...leads_combinados];
let leadAtualId = null;

function importarLeads(event) {{
  const file = event.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = function(e) {{
    const text = e.target.result;
    const lines = text.split('\\n');
    if (lines.length < 2) return alert("Arquivo inválido ou vazio!");

    const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''));
    let colNome = -1, colTel = -1, colEmail = -1, colCurso = -1, colData = -1;
    
    headers.forEach((h, i) => {{
      const lower = h.toLowerCase();
      if (lower.includes('nome')) colNome = i;
      else if (lower.includes('telefone') || lower.includes('celular') || lower.includes('whatsapp') || lower.includes('tel')) colTel = i;
      else if (lower.includes('email') || lower.includes('e-mail')) colEmail = i;
      else if (lower.includes('curso') || lower.includes('interesse')) colCurso = i;
      else if (lower.includes('data') || lower.includes('criado') || lower.includes('cadastro')) colData = i;
    }});

    let importados_novos = 0;
    
    for (let i = 1; i < lines.length; i++) {{
      const row = lines[i].split(/,(?=(?:(?:[^"]*"){2})*[^"]*$)/).map(c => c.trim().replace(/(^"|"$)/g, ''));
      if (row.length < 2) continue;
      
      const nome = colNome >= 0 && row[colNome] ? row[colNome] : '';
      const telefone = colTel >= 0 && row[colTel] ? row[colTel] : '';
      const email = colEmail >= 0 && row[colEmail] ? row[colEmail] : '';
      const curso = colCurso >= 0 && row[colCurso] ? row[colCurso] : 'Sem Curso';
      const data_str = colData >= 0 && row[colData] ? row[colData].split(' ')[0] : '';
      
      const tel_wa = telefone.replace(/\\+/g, '').replace(/ /g, '').replace(/-/g, '');
      const id = tel_wa || email || nome;
      if (!id) continue;
      
      let data_iso = "";
      if (data_str && data_str.includes('/')) {{
        const partes = data_str.split('/');
        if (partes.length === 3) data_iso = `${{partes[2]}}-${{partes[1]}}-${{partes[0]}}`;
      }} else if (data_str && data_str.includes('-')) {{
        data_iso = data_str;
      }}
      
      if (tel_wa && telefones_vistos.has(tel_wa)) continue;
      if (email && emails_vistos.has(email)) continue;
      
      const novoLead = {{
        nome, email, telefone, tel_wa, curso,
        data: data_str, data_iso, mes_ano: '', etapa: 'Not contacted'
      }};
      
      IMPORTED_LEADS.push(novoLead);
      leads_combinados.push(novoLead);
      if (tel_wa) telefones_vistos.add(tel_wa);
      if (email) emails_vistos.add(email);
      importados_novos++;
    }}
    
    localStorage.setItem('salute_imported_leads', JSON.stringify(IMPORTED_LEADS));
    aplicarFiltros();
    alert(`Importação concluída! ${{importados_novos}} novos leads adicionados.`);
    event.target.value = '';
  }};
  reader.readAsText(file);
}}

function abrirModal(id, nome) {{
  leadAtualId = id;
  document.getElementById('modalNome').textContent = nome || 'Lead';
  document.getElementById('modalIdentificador').textContent = id;
  
  const data = CRM_DATA[id] || {{ status: '', notas: '' }};
  document.getElementById('crmStatus').value = data.status || '';
  document.getElementById('crmNotas').value = data.notas || '';
  
  document.getElementById('modalCRM').style.display = 'flex';
}}

function fecharModal() {{
  document.getElementById('modalCRM').style.display = 'none';
  leadAtualId = null;
}}

function salvarCRM() {{
  if (!leadAtualId) return;
  const status = document.getElementById('crmStatus').value;
  const notas = document.getElementById('crmNotas').value;
  
  if (status || notas) {{
    CRM_DATA[leadAtualId] = {{ status, notas }};
  }} else {{
    delete CRM_DATA[leadAtualId];
  }}
  
  localStorage.setItem(CRM_KEY, JSON.stringify(CRM_DATA));
  fecharModal();
  renderizar();
}}

function exportarCRM() {{
  let csvContent = "data:text/csv;charset=utf-8,";
  csvContent += "Nome,Telefone,Email,Curso,Data Cadastro,Status Original,Status CRM,Anotações CRM\\n";
  
  leads_combinados.forEach(l => {{
    const id = l.tel_wa || l.email || l.nome;
    const crm = CRM_DATA[id];
    if (crm || l.etapa !== 'Not contacted') {{
      const nome = `"${{l.nome || ''}}"`;
      const tel = `"${{l.telefone || ''}}"`;
      const email = `"${{l.email || ''}}"`;
      const curso = `"${{l.curso || ''}}"`;
      const data = `"${{l.data || ''}}"`;
      const statusOrig = `"${{l.etapa}}"`;
      const statusCrm = `"${{crm ? crm.status : ''}}"`;
      const notas = `"${{(crm && crm.notas) ? crm.notas.replace(/"/g, '""') : ''}}"`;
      csvContent += `${{nome}},${{tel}},${{email}},${{curso}},${{data}},${{statusOrig}},${{statusCrm}},${{notas}}\\n`;
    }}
  }});
  
  const encodedUri = encodeURI(csvContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", "crm_salute_backup.csv");
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}}

function corCurso(curso) {{
  return CORES[curso] || '#6b7280';
}}

function hexToRgba(hex, alpha) {{
  const r = parseInt(hex.slice(1,3), 16);
  const g = parseInt(hex.slice(3,5), 16);
  const b = parseInt(hex.slice(5,7), 16);
  return `rgba(${{r}},${{g}},${{b}},${{alpha}})`;
}}

function filtrarCurso(curso) {{
  document.getElementById('filtroCurso').value = curso;
  document.getElementById('busca').value = '';
  document.getElementById('filtroMes').value = '';
  aplicarFiltros();
}}

function limparFiltros() {{
  document.getElementById('busca').value = '';
  document.getElementById('filtroCurso').value = '';
  document.getElementById('filtroMes').value = '';
  document.getElementById('dataInicio').value = '';
  document.getElementById('dataFim').value = '';
  aplicarFiltros();
}}

function aplicarFiltros() {{
  const busca = document.getElementById('busca').value.toLowerCase();
  const curso = document.getElementById('filtroCurso').value;
  const mes = document.getElementById('filtroMes').value;
  const dataInicio = document.getElementById('dataInicio').value;
  const dataFim = document.getElementById('dataFim').value;

  leadsFiltrados = leads_combinados.filter(l => {{
    if (curso && l.curso !== curso) return false;
    if (mes && l.mes_ano !== mes) return false;
    if (dataInicio && (!l.data_iso || l.data_iso.slice(0, 10) < dataInicio)) return false;
    if (dataFim && (!l.data_iso || l.data_iso.slice(0, 10) > dataFim)) return false;
    if (busca) {{
      const txt = (l.nome + l.email + l.telefone).toLowerCase();
      if (!txt.includes(busca)) return false;
    }}
    return true;
  }});

  paginaAtual = 1;
  renderizar();
}}

function renderizar() {{
  const total = leadsFiltrados.length;
  document.getElementById('countNum').textContent = total;

  const inicio = (paginaAtual - 1) * POR_PAG;
  const pagina = leadsFiltrados.slice(inicio, inicio + POR_PAG);

  const tbody = document.getElementById('tabelaBody');
  const empty = document.getElementById('emptyState');

  if (total === 0) {{
    tbody.innerHTML = '';
    empty.style.display = 'block';
  }} else {{
    empty.style.display = 'none';
    tbody.innerHTML = pagina.map((l, i) => {{
      const cor = corCurso(l.curso);
      const semCurso = l.curso === 'Sem Curso';
      const n = inicio + i + 1;
      
      const id = l.tel_wa || l.email || l.nome;
      const crm = CRM_DATA[id];
      
      let etapa = '';
      if (crm && (crm.status || crm.notas)) {{
         let cls = 'crm-contatado';
         let lbl = crm.status || 'Contatado';
         if (crm.status === 'Fechou') cls = 'crm-fechou';
         if (crm.status === 'Recusou') cls = 'crm-recusou';
         if (crm.status === 'Não Respondeu') cls = 'crm-nao_respondeu';
         if (crm.status === 'Em negociação') cls = 'crm-em_negociacao';
         
         etapa = `<div class="crm-tag ${{cls}}">${{lbl}}</div>`;
         if (crm.notas) etapa += `<div style="font-size:0.68rem;color:#64748b;max-width:250px;line-height:1.3;margin-top:4px;white-space:normal;word-break:break-word;">${{crm.notas}}</div>`;
      }} else {{
         etapa = l.etapa === 'Not contacted'
          ? `<span class="tag-nc">Não contatado</span>`
          : `<span class="tag-ok">${{l.etapa}}</span>`;
      }}
      
      const WA_SVG = `<svg viewBox="0 0 24 24" width="16" height="16" fill="#fff"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/></svg>`;
      const EDIT_SVG = `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>`;

      const btnWa = l.tel_wa
        ? `<a class="btn-wa" href="https://wa.me/${{l.tel_wa}}" target="_blank" title="${{l.nome}}">${{WA_SVG}}</a>`
        : `<span class="btn-wa-off" title="Sem telefone">—</span>`;
        
      const btnCrmCls = (crm && (crm.status || crm.notas)) ? "btn-crm has-notes" : "btn-crm";
      const btnEdit = `<button class="${{btnCrmCls}}" onclick="abrirModal('${{id.replace(/'/g, "\\\\'")}}', '${{(l.nome||'').replace(/'/g, "\\\\'")}}')" title="Anotações CRM">${{EDIT_SVG}}</button>`;
      
      return `<tr class="${{semCurso ? 'sem-curso' : ''}}">
        <td class="td-idx idx">${{n}}</td>
        <td class="td-nome">
          <div class="nome">${{l.nome || '—'}}</div>
          <div class="sub">${{l.email || '—'}}</div>
        </td>
        <td class="td-curso"><span class="pill" style="background:${{hexToRgba(cor,0.08)}};color:${{cor}}"><span class="pill-dot" style="background:${{cor}}"></span>${{l.curso}}</span></td>
        <td class="td-tel tel">${{l.telefone || '—'}}</td>
        <td class="td-email sub">${{l.email || '—'}}</td>
        <td class="td-data date">${{l.data}}</td>
        <td class="td-etapa">${{etapa}}</td>
        <td class="td-actions" style="display:flex;gap:4px;justify-content:flex-end">${{btnWa}}${{btnEdit}}</td>
      </tr>`;
    }}).join('');
  }}

  renderPaginacao(total);
}}

function renderPaginacao(total) {{
  const totalPags = Math.ceil(total / POR_PAG);
  const div = document.getElementById('paginacao');
  if (totalPags <= 1) {{ div.innerHTML = ''; return; }}

  let html = `<button class="pg" onclick="irPagina(${{paginaAtual-1}})" ${{paginaAtual===1?'disabled':''}}>←</button>`;
  for (let p = 1; p <= totalPags; p++) {{
    if (p === 1 || p === totalPags || (p >= paginaAtual-2 && p <= paginaAtual+2)) {{
      html += `<button class="pg ${{p===paginaAtual?'on':''}}" onclick="irPagina(${{p}})">${{p}}</button>`;
    }} else if (p === paginaAtual-3 || p === paginaAtual+3) {{
      html += `<span style="color:#d1d5db;padding:0 2px;font-size:0.8rem">…</span>`;
    }}
  }}
  html += `<button class="pg" onclick="irPagina(${{paginaAtual+1}})" ${{paginaAtual===totalPags?'disabled':''}}>→</button>`;
  div.innerHTML = html;
}}

function irPagina(p) {{
  const total = leadsFiltrados.length;
  const totalPags = Math.ceil(total / POR_PAG);
  if (p < 1 || p > totalPags) return;
  paginaAtual = p;
  renderizar();
  window.scrollTo({{top: 0, behavior: 'smooth'}});
}}

// Inicializa
limparFiltros();
</script>
</body>
</html>"""

with open(SAIDA, "w", encoding="utf-8") as f:
    f.write(HTML)

print(f"✅ Gerado: {SAIDA}")
print(f"   Total de leads: {len(todos_leads)}")
print(f"   Sem Curso: {por_curso.get('Sem Curso', 0)}")
print(f"   Cursos encontrados: {len(cursos_lista)}")
