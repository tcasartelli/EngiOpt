from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

doc = Document()

title = doc.add_heading("NMSE Threshold Sweep — Full Results (corrected)", level=1)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER

doc.add_paragraph(
    "Grid sweep over τ (NMSE threshold) for Constrained LVAE on thermoelastic2D. "
    "Colours: 🟡 = best val NMSE | 🟠 = early stop prematuro (patience=10, start=0) — risultati non validi | "
    "🟧 = early stop moderato (patience=100) | bianco = patience=500 (converged)."
)

# τ | Train NMSE | Val NMSE | Active dims | vol_active | Epoch stop | patience | es_start | Note
headers = ["τ", "Train NMSE", "Val NMSE", "Active dims", "vol_active", "Epoch stop", "patience", "es_start", "Note"]

# (tau, train_nmse, val_nmse, active_dims, vol_active, epoch_stop, patience, es_start, note, fill_hex)
# fills: INVALID=FFD0D0 (light red), MODERATE=FFF0D0 (light orange), BEST=FFFAAA (yellow), NORMAL=FFFFFF
rows = [
    ("0.01", "0.0949", "0.1703", "100/100", "✗", "91",   "10",  "0",    "❌ Invalid (ES too early)", "FFD0D0"),
    ("0.03", "0.1081", "0.1738", "100/100", "✗", "80",   "10",  "0",    "❌ Invalid (ES too early)", "FFD0D0"),
    ("0.05", "0.1133", "0.1722", "100/100", "✗", "74",   "10",  "0",    "❌ Invalid (ES too early)", "FFD0D0"),
    ("0.10", "0.1085", "0.1763", "100/100", "✗", "91",   "10",  "0",    "❌ Invalid (ES too early)", "FFD0D0"),
    ("0.15", "0.0468", "0.2203", "71/100",  "✓", "3502", "500", "3000", "Over-compress",             "FFFFFF"),
    ("0.18", "0.0626", "0.2022", "80/100",  "✓", "2103", "100", "2000", "⚠️ ES moderato",            "FFF0D0"),
    ("0.20", "0.0486", "0.2052", "78/100",  "✓", "3512", "500", "3000", "Compression",               "FFFFFF"),
    ("0.22", "0.0565", "0.1866", "91/100",  "✓", "3502", "500", "3000", "Near sweet spot",           "FFFFFF"),
    ("0.25", "0.0626", "0.1790", "95/100",  "✓", "3509", "500", "3000", "★ Best val",                "FFFAAA"),
    ("0.30", "0.1167", "0.2388", "43/100",  "✓", "2100", "100", "2000", "⚠️ ES moderato",            "FFF0D0"),
    ("0.50", "0.1259", "0.2510", "45/100",  "✓", "2109", "100", "2000", "⚠️ ES moderato",            "FFF0D0"),
    ("0.70", "0.1314", "0.3173", "14/100",  "✓", "2116", "100", "2000", "⚠️ ES moderato",            "FFF0D0"),
]

BEST_ROW = 8  # τ=0.25

table = doc.add_table(rows=1 + len(rows), cols=len(headers))
table.style = "Table Grid"

# header row
hdr = table.rows[0]
for i, h in enumerate(headers):
    cell = hdr.cells[i]
    cell.text = h
    run = cell.paragraphs[0].runs[0]
    run.bold = True
    run.font.size = Pt(10)
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), "1F3864")
    tcPr.append(shd)
    run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

# data rows
for r_idx, row_data in enumerate(rows):
    row = table.rows[r_idx + 1]
    *values, fill = row_data
    is_best = r_idx == BEST_ROW

    for c_idx, val in enumerate(values):
        cell = row.cells[c_idx]
        cell.text = val
        run = cell.paragraphs[0].runs[0]
        run.font.size = Pt(10)
        if is_best:
            run.bold = True
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        tc = cell._tc
        tcPr = tc.get_or_add_tcPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), fill)
        tcPr.append(shd)

widths = [1.0, 2.0, 1.9, 2.0, 2.0, 2.0, 1.8, 1.8, 3.8]
for i, w in enumerate(widths):
    for cell in table.columns[i].cells:
        cell.width = Cm(w)

doc.add_paragraph("")
note = doc.add_paragraph()
note.add_run("Legenda colori: ").bold = True
note.add_run(
    "Rosso = run non validi (early stopping con start=0, patience=10 → fermati a <100 epoche). "
    "Arancione = early stopping moderato (patience=100). "
    "Bianco = convergenza corretta (patience=500, start=3000). "
    "Giallo = miglior val NMSE (τ=0.25, val=0.1790)."
)
doc.add_paragraph("")
obs = doc.add_paragraph()
obs.add_run("Osservazioni: ").bold = True
obs.add_run(
    "Il sweet spot reale è τ=0.25 (val NMSE=0.1790, 95/100 dims attive). "
    "Tra τ=0.25 e τ=0.30 c'è un salto brusco: 95→43 dims, val NMSE 0.179→0.239. "
    "I run τ≤0.10 sono invalidi (early stop a <100 epoche). "
    "I run τ=0.18, 0.30, 0.50, 0.70 potrebbero migliorare con patience=500."
)

out = "/cluster/home/tcasartelli/projects/EngiOpt/engiopt/vanilla_thomas_thermo2D/sweep_results_table.docx"
doc.save(out)
print(f"Saved: {out}")
