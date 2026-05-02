"""Build spectral_norm_encoder_presentation.pptx — full update with sweep results."""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
BLACK  = RGBColor(0x1A, 0x1A, 0x2E)
BLUE   = RGBColor(0x1F, 0x6F, 0xEB)
GREEN  = RGBColor(0x0A, 0x7D, 0x57)
ORANGE = RGBColor(0xE8, 0x7D, 0x14)
RED    = RGBColor(0xC0, 0x39, 0x2B)
GREY   = RGBColor(0xF2, 0xF4, 0xF7)
DKGREY = RGBColor(0x55, 0x65, 0x7A)
PURPLE = RGBColor(0x6C, 0x35, 0xDE)

W = Inches(13.33)
H = Inches(7.5)

prs = Presentation()
prs.slide_width  = W
prs.slide_height = H
BLANK = prs.slide_layouts[6]

# ── helpers ────────────────────────────────────────────────────────────────────

def slide():
    sl = prs.slides.add_slide(BLANK)
    bg = sl.background.fill
    bg.solid(); bg.fore_color.rgb = WHITE
    return sl

def tb(sl, text, l, t, w, h, size=16, bold=False, color=BLACK,
       align=PP_ALIGN.LEFT, italic=False):
    txb = sl.shapes.add_textbox(l, t, w, h)
    txb.word_wrap = True
    tf = txb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.alignment = align
    r = p.add_run()
    r.text = text; r.font.size = Pt(size)
    r.font.bold = bold; r.font.italic = italic
    r.font.color.rgb = color
    return txb

def header(sl, title, subtitle=None):
    bar = sl.shapes.add_shape(1, Inches(0), Inches(0), W, Inches(1.15))
    bar.fill.solid(); bar.fill.fore_color.rgb = BLUE; bar.line.fill.background()
    tf = bar.text_frame; tf.word_wrap = False
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.LEFT
    r = p.add_run(); r.text = title
    r.font.size = Pt(28); r.font.bold = True; r.font.color.rgb = WHITE
    if subtitle:
        p2 = tf.add_paragraph(); p2.alignment = PP_ALIGN.LEFT
        r2 = p2.add_run(); r2.text = subtitle
        r2.font.size = Pt(14); r2.font.color.rgb = RGBColor(0xCC, 0xDD, 0xFF)

def rect(sl, l, t, w, h, fill=GREY, border=None, bw=Pt(1.5)):
    s = sl.shapes.add_shape(1, l, t, w, h)
    s.fill.solid(); s.fill.fore_color.rgb = fill
    if border: s.line.color.rgb = border; s.line.width = bw
    else: s.line.fill.background()
    return s

def card(sl, l, t, w, h, fill=GREY):
    return rect(sl, l, t, w, h, fill=fill, border=BLUE)

def bullets(sl, items, l, t, w, h, default_size=14):
    txb = sl.shapes.add_textbox(l, t, w, h)
    txb.word_wrap = True
    tf = txb.text_frame; tf.word_wrap = True
    first = True
    for item in items:
        if isinstance(item, tuple):
            pre, text, sz, bold, color = item
        else:
            pre, text, sz, bold, color = "•  ", item, default_size, False, BLACK
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.alignment = PP_ALIGN.LEFT
        r = p.add_run()
        r.text = pre + text
        r.font.size = Pt(sz); r.font.bold = bold; r.font.color.rgb = color

def tcell(cell, text, size=12, bold=False, color=BLACK,
          align=PP_ALIGN.CENTER, fill=None):
    if fill:
        cell.fill.solid(); cell.fill.fore_color.rgb = fill
    tf = cell.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.alignment = align
    runs = p.runs
    r = runs[0] if runs else p.add_run()
    r.text = text
    r.font.size = Pt(size); r.font.bold = bold; r.font.color.rgb = color

def make_table(sl, col_headers, col_widths, l, t, h):
    n_cols = len(col_headers)
    tbl = sl.shapes.add_table(1, n_cols, l, t, sum(col_widths), h).table
    for ci, cw in enumerate(col_widths):
        tbl.columns[ci].width = cw
    for ci, hdr in enumerate(col_headers):
        c = tbl.cell(0, ci)
        tcell(c, hdr, size=12, bold=True, color=WHITE, fill=BLUE)
    return tbl

def add_row(tbl, vals, row_fill=GREY, color_map=None):
    n = tbl.rows._tbl.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing}tr')
    ri = len(tbl.rows) - 1
    tbl.add_row()
    ri = len(tbl.rows) - 1
    for ci, val in enumerate(vals):
        cell = tbl.cell(ri, ci)
        col = (color_map or {}).get(ci, BLACK)
        al = PP_ALIGN.LEFT if ci == 0 else PP_ALIGN.CENTER
        tcell(cell, val, size=11, color=col, align=al, fill=row_fill)
    return tbl


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 1 — Title
# ══════════════════════════════════════════════════════════════════════════════
sl = slide()
tb(sl, "LVAE for Thermoelastic 2D Topology Optimisation",
   Inches(0.8), Inches(1.6), Inches(11.7), Inches(1.6),
   size=34, bold=True, color=BLACK, align=PP_ALIGN.CENTER)
tb(sl, "Reducing the train/val NMSE gap  ·  Exploring the latent dimensionality sweet spot",
   Inches(0.8), Inches(3.3), Inches(11.7), Inches(0.6),
   size=19, color=DKGREY, align=PP_ALIGN.CENTER)
tb(sl, "Thomas Casartelli  ·  April 2026  ·  EngiOpt / ETH Zürich",
   Inches(0.8), Inches(4.05), Inches(11.7), Inches(0.5),
   size=15, color=DKGREY, align=PP_ALIGN.CENTER, italic=True)
rect(sl, Inches(3.5), Inches(4.75), Inches(6.33), Pt(2), fill=BLUE)
rect(sl, Inches(0), Inches(6.9), W, Inches(0.6), fill=BLUE)
tb(sl, "EngiOpt  ·  ETH Zürich  ·  IDEAL Lab",
   Inches(0.3), Inches(6.95), Inches(6), Inches(0.5), size=13, color=WHITE)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 2 — Problem & dataset
# ══════════════════════════════════════════════════════════════════════════════
sl = slide()
header(sl, "Problem Setting",
       "Thermoelastic 2D topology optimisation  ·  IDEALLab/thermoelastic_2d_v1")

card(sl, Inches(0.3), Inches(1.35), Inches(6.2), Inches(5.7))
tb(sl, "The dataset", Inches(0.5), Inches(1.42), Inches(5.8), Inches(0.4),
   size=15, bold=True, color=BLUE)
bullets(sl, [
    "14 400 train  /  1 800 val  /  1 800 test  (18 000 total, v1)",
    "Each design: 64×64 float32 density field in [0,1] — SIMP-relaxed binary topology.",
    "Goal: minimise structural + thermal compliance under a volume fraction constraint.",
    "Each sample has unique, randomly generated boundary conditions:",
    ("    ", "volfrac ∈ [0.2, 0.5]  ·  weight ∈ [0,1]  ·  load/fix/heatsink positions", 13, False, DKGREY),
    ("→  ", "High inter-sample diversity makes latent generalisation hard but ensures rich Var(data).", 13, False, DKGREY),
], Inches(0.5), Inches(1.90), Inches(5.9), Inches(5.0), default_size=14)

card(sl, Inches(6.7), Inches(1.35), Inches(6.3), Inches(5.7))
tb(sl, "The LVAE", Inches(6.9), Inches(1.42), Inches(5.9), Inches(0.4),
   size=15, bold=True, color=BLUE)
bullets(sl, [
    "Autoencoder that minimises the geometric mean of latent std — compresses unused dimensions.",
    "Volume pressure gated on NMSE ≤ τ, preventing compression before reconstruction is acceptable. NMSE = MSE / Var(data).",
    "Plummet pruning (from epoch 500): detects and removes dimensions with sharply collapsed std.",
    "Three variants tested:",
    ("    ", "Vanilla LVAE — rec loss only", 13, False, DKGREY),
    ("    ", "Constrained LVAE — one-sided NMSE constraint", 13, False, DKGREY),
    ("    ", "Constrained PLVAE — NMSE + performance predictor", 13, False, DKGREY),
    ("→  ", "Key research question: what is the right latent dimensionality and threshold τ for this dataset?", 14, True, BLUE),
], Inches(6.9), Inches(1.90), Inches(6.0), Inches(5.0), default_size=14)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 3 — The train/val gap problem
# ══════════════════════════════════════════════════════════════════════════════
sl = slide()
header(sl, "The Core Problem: Train / Val NMSE Gap",
       "The encoder memorises training data — volume pressure activates prematurely")

card(sl, Inches(0.3), Inches(1.35), Inches(4.0), Inches(5.7), fill=RGBColor(0xFF,0xF0,0xF0))
tb(sl, "Observed numbers", Inches(0.5), Inches(1.42), Inches(3.6), Inches(0.4),
   size=14, bold=True, color=RED)
bullets(sl, [
    ("    ", "Baseline BN encoder (ep 83, stopped early)", 13, True, BLACK),
    ("    ", "Val NMSE 0.171  /  Vol not activated", 13, False, DKGREY),
    ("", "", 5, False, BLACK),
    ("    ", "GN + SN encoder (ep 2088)", 13, True, BLACK),
    ("    ", "Train NMSE 0.048 ✓  /  Val NMSE 0.197 ✗", 13, False, RED),
    ("    ", "Gap = 4.1×  /  Vol never activated", 13, False, DKGREY),
    ("", "", 5, False, BLACK),
    ("    ", "Both with τ = 0.05 (default threshold)", 13, True, BLACK),
    ("", "", 5, False, BLACK),
    ("    ", "14 400 training samples: overfitting", 13, True, RED),
    ("    ", "is NOT a small-dataset effect.", 13, True, RED),
    ("    ", "It is a genuine encoder capacity issue.", 13, False, DKGREY),
], Inches(0.5), Inches(1.90), Inches(3.7), Inches(5.0), default_size=13)

card(sl, Inches(4.55), Inches(1.35), Inches(4.3), Inches(5.7))
tb(sl, "Root cause", Inches(4.75), Inches(1.42), Inches(4.0), Inches(0.4),
   size=14, bold=True, color=BLUE)
bullets(sl, [
    "Encoder maps training samples to tight, precise latent codes. For val samples, codes are noisier and less well-separated.",
    "BN → GN swap eliminated train/eval statistics mismatch but left the gap unchanged: the problem is encoder capacity, not normalisation.",
    "With τ=0.05, train NMSE satisfies the constraint while val NMSE stays at ~0.20. Volume activates on overfitting data → compresses a space that hasn't generalised.",
], Inches(4.75), Inches(1.90), Inches(4.0), Inches(2.9), default_size=13)

card(sl, Inches(4.55), Inches(4.4), Inches(4.3), Inches(2.6))
tb(sl, "Key insight from τ sweep", Inches(4.75), Inches(4.47), Inches(4.0), Inches(0.4),
   size=14, bold=True, color=BLUE)
bullets(sl, [
    "τ is the most sensitive hyperparameter. Too low → vol never activates. Too high → over-compression.",
    ("★  ", "τ = 0.20 is the sweet spot: vol activates reliably, pruning stays light, val NMSE minimised at 0.182.", 13, True, GREEN),
], Inches(4.75), Inches(4.95), Inches(4.0), Inches(1.9), default_size=13)

card(sl, Inches(9.1), Inches(1.35), Inches(3.9), Inches(5.7))
tb(sl, "Strategies tested", Inches(9.3), Inches(1.42), Inches(3.6), Inches(0.4),
   size=14, bold=True, color=BLUE)
strategies = [
    (GREEN,  "1. GN + SN encoder"),
    (GREEN,  "2. Latent noise  σ=0.1"),
    (RED,    "3. Val-gate  τ=0.05"),
    (GREEN,  "4. τ sweep  (8 values)"),
    (ORANGE, "5. τ=0.20 + noise  ← NEW"),
]
y = Inches(1.90)
for col, name in strategies:
    rect(sl, Inches(9.1), y, Inches(0.1), Inches(0.55), fill=col)
    card(sl, Inches(9.25), y, Inches(3.7), Inches(0.55), fill=GREY)
    tb(sl, name, Inches(9.4), y + Inches(0.1), Inches(3.4), Inches(0.38),
       size=13, bold=True, color=BLACK)
    y += Inches(0.65)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 4 — Strategy 1: GN + SN encoder
# ══════════════════════════════════════════════════════════════════════════════
sl = slide()
header(sl, "Strategy 1 — GN + Spectral Norm Encoder  [DONE]",
       "Stabilise encoder output distribution  ·  necessary but insufficient")

card(sl, Inches(0.3), Inches(1.35), Inches(6.2), Inches(5.7))
tb(sl, "WHY & HOW", Inches(0.5), Inches(1.42), Inches(5.8), Inches(0.4),
   size=15, bold=True, color=BLUE)
bullets(sl, [
    "BatchNorm computes running statistics on training data; at eval time these create a distribution shift in z. GroupNorm normalises using each sample's own channel statistics — no train/eval gap.",
    "Spectral Normalisation re-scales each weight matrix so its largest singular value ≤ 1. Encoder becomes 1-Lipschitz: small input changes → equally small or smaller changes in z.",
    ("→  ", "GN removes the artefact; SN bounds sensitivity. Together: a more stable and predictable latent representation.", 14, False, DKGREY),
], Inches(0.5), Inches(1.90), Inches(5.9), Inches(3.2), default_size=14)

tb(sl, "Results", Inches(0.5), Inches(5.2), Inches(5.9), Inches(0.35),
   size=14, bold=True, color=BLUE)
bullets(sl, [
    ("    ", "cLVAE ep 2088:  train 0.048 ✓ / val 0.197 ✗  gap 4.1×  /  100/100 dims", 13, False, RED),
    ("    ", "LVAE ep 2050:   train rec 0.006 / val rec 0.034  gap 5.8×  /  90/100 dims", 13, False, RED),
    ("    ", "cPLVAE ep 2078: NMSE_rec 0.087 / val 0.304  gap 3.5×  /  vol never active", 13, False, RED),
    ("✗  ", "Verdict: BN was NOT the root cause. Gap persists with GN.", 13, True, RED),
], Inches(0.5), Inches(5.6), Inches(5.9), Inches(1.3), default_size=13)

card(sl, Inches(6.7), Inches(1.35), Inches(6.3), Inches(5.7))
tb(sl, "What this means", Inches(6.9), Inches(1.42), Inches(5.9), Inches(0.4),
   size=15, bold=True, color=BLUE)
bullets(sl, [
    "The gap is intrinsic to the encoder's expressive capacity, not to normalisation artifacts.",
    "With 14.4k diverse training samples, the encoder learns to map each sample to a tightly clustered latent region — but this precision doesn't transfer to val samples.",
    "GN + SN is still correct and kept as the encoder standard: it eliminates one source of error and bounds sensitivity. All subsequent experiments use it.",
    ("→  ", "Next needed: regularisation that directly constrains encoder overfitting, OR finding the right threshold τ so volume pressure activates at the right time.", 14, False, DKGREY),
], Inches(6.9), Inches(1.90), Inches(6.0), Inches(5.0), default_size=14)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 5 — τ sweep (the most important experiment)
# ══════════════════════════════════════════════════════════════════════════════
sl = slide()
header(sl, "Strategy 4 — NMSE Threshold Sweep  (τ ∈ {0.01 … 0.70})  [DONE]",
       "Finding the dimensionality sweet spot  ·  8 values  ·  constrained LVAE")

# table
COLS = ["τ", "Train NMSE", "Val NMSE", "Active dims", "Vol active", "Regime"]
CW   = [Inches(0.8), Inches(1.5), Inches(1.5), Inches(1.5), Inches(1.4), Inches(2.4)]

ROWS = [
    ("0.01", "0.035", "0.211", "100/100", "✗", "Unreachable"),
    ("0.03", "0.035", "0.211", "100/100", "✗", "Unreachable"),
    ("0.05", "0.067", "0.198", "100/100", "✗", "Borderline"),
    ("0.10", "0.077", "0.191", "100/100", "✓", "Compression"),
    ("0.20", "0.088", "0.182", "97/100",  "✓", "★ SWEET SPOT"),
    ("0.30", "0.117", "0.239", "43/100",  "✓", "Over-compress"),
    ("0.50", "0.126", "0.251", "45/100",  "✓", "Over-compress"),
    ("0.70", "0.131", "0.317", "14/100",  "✓", "Over-compress"),
]

regime_col = {
    "Unreachable":   RED,
    "Borderline":    ORANGE,
    "Compression":   GREEN,
    "★ SWEET SPOT":  GREEN,
    "Over-compress": RED,
}
vol_col = {"✓": GREEN, "✗": RED}

n_rows = len(ROWS) + 1
n_cols = len(COLS)
tbl = slide().shapes  # dummy — we build below
sl2 = sl  # keep reference
tbl = sl.shapes.add_table(n_rows, n_cols,
                           Inches(0.3), Inches(1.35),
                           sum(CW), Inches(5.65)).table
for ci, cw in enumerate(CW):
    tbl.columns[ci].width = cw
rh = Inches(5.65) // n_rows
for ri in range(n_rows):
    tbl.rows[ri].height = rh

for ci, hdr in enumerate(COLS):
    tcell(tbl.cell(0, ci), hdr, size=13, bold=True, color=WHITE, fill=BLUE)

for ri, row in enumerate(ROWS):
    fill = RGBColor(0xE8,0xFF,0xF0) if row[0] == "0.20" else (GREY if ri % 2 == 0 else WHITE)
    bold_row = row[0] == "0.20"
    for ci, val in enumerate(row):
        cell = tbl.cell(ri + 1, ci)
        col = BLACK
        if ci == 2:  # val NMSE
            try:
                v = float(val)
                col = GREEN if v < 0.185 else (ORANGE if v < 0.200 else RED)
            except ValueError: pass
        if ci == 4: col = vol_col.get(val, BLACK)
        if ci == 5: col = regime_col.get(val, BLACK)
        al = PP_ALIGN.CENTER
        tcell(cell, val, size=12 if not bold_row else 13, bold=bold_row,
              color=col, align=al, fill=fill)

# right panel — analysis
card(sl, Inches(9.7), Inches(1.35), Inches(3.3), Inches(5.7))
tb(sl, "What the sweep shows", Inches(9.9), Inches(1.42), Inches(3.0), Inches(0.4),
   size=14, bold=True, color=BLUE)
bullets(sl, [
    ("U-shape:", "Val NMSE forms a U as τ increases.", 13, True, BLACK),
    ("", "", 6, False, BLACK),
    ("Low τ  ", "(0.01–0.05): vol never activates. Encoder trains freely → memorises.", 12, False, RED),
    ("", "", 5, False, BLACK),
    ("τ=0.20 ", "SWEET SPOT. Vol activates, light pruning (97 dims), val NMSE minimised at 0.182.", 12, True, GREEN),
    ("", "", 5, False, BLACK),
    ("High τ ", "(≥0.30): over-compression. Model forced to squeeze too much into too few dims. Val NMSE climbs back up despite pruning (43 → 14 active dims).", 12, False, RED),
    ("", "", 7, False, BLACK),
    ("→  ", "τ is the most impactful hyperparameter found so far.", 13, True, BLUE),
    ("→  ", "Best val NMSE overall: 0.182 at τ=0.20.", 13, True, GREEN),
], Inches(9.9), Inches(1.90), Inches(3.0), Inches(5.0), default_size=12)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 6 — Strategy 2: Latent Noise
# ══════════════════════════════════════════════════════════════════════════════
sl = slide()
header(sl, "Strategy 2 — Latent Noise Injection  σ=0.1  [DONE]",
       "Forcing decoder robustness against imprecise codes  ·  τ=0.05 in these runs")

card(sl, Inches(0.3), Inches(1.35), Inches(5.5), Inches(5.7))
tb(sl, "Mechanism", Inches(0.5), Inches(1.42), Inches(5.2), Inches(0.4),
   size=15, bold=True, color=BLUE)
bullets(sl, [
    "Gaussian noise (σ=0.1) added to each active latent dim before decoding — training only.",
    "Decoder learns neighbourhood robustness: codes near the encoder output should reconstruct correctly.",
    "Prevents train rec from collapsing to near-zero — model cannot memorise exact codes.",
    "Clean z used for volume pressure and pruning statistics — compression driven by true distribution.",
    ("Analogy:  ", "Dropout in the latent space. Prevents decoder from relying on exact codes.", 13, False, DKGREY),
], Inches(0.5), Inches(1.90), Inches(5.2), Inches(3.5), default_size=14)

tb(sl, "Results by variant (ep ~2050, τ=0.05)", Inches(0.5), Inches(5.45), Inches(5.2), Inches(0.35),
   size=14, bold=True, color=BLUE)
rows_n = [
    ("Vanilla LVAE",  "—",      "rec 0.034", "5.3×", "69/100", "Yes"),
    ("cLVAE  ★",     "0.050",  "0.188",     "3.8×", "100/100","Yes"),
    ("cPLVAE",        "0.091",  "0.311",     "3.4×", "100/100","No"),
]
NCOLS = ["Model", "Train", "Val NMSE", "Gap", "Dims", "Vol"]
NCW   = [Inches(1.5), Inches(0.8), Inches(1.1), Inches(0.8), Inches(1.0), Inches(0.7)]
ntbl  = sl.shapes.add_table(len(rows_n)+1, len(NCOLS),
                              Inches(0.35), Inches(5.85),
                              sum(NCW), Inches(1.4)).table
for ci, cw in enumerate(NCW): ntbl.columns[ci].width = cw
for ri in range(len(rows_n)+1): ntbl.rows[ri].height = Inches(1.4)//(len(rows_n)+1)
for ci, h in enumerate(NCOLS):
    tcell(ntbl.cell(0,ci), h, size=11, bold=True, color=WHITE, fill=BLUE)
for ri, (n,tr,va,gap,dims,vol) in enumerate(rows_n):
    f = GREY if ri % 2 == 0 else WHITE
    gcol = GREEN if "3." in gap else (ORANGE if "4." in gap else RED)
    for ci, (v, c) in enumerate([(n,BLACK),(tr,DKGREY),(va,DKGREY),(gap,gcol),(dims,DKGREY),(vol,GREEN if vol=="Yes" else RED)]):
        tcell(ntbl.cell(ri+1, ci), v, size=11, color=c,
              align=PP_ALIGN.LEFT if ci==0 else PP_ALIGN.CENTER, fill=f)

card(sl, Inches(6.1), Inches(1.35), Inches(6.9), Inches(5.7))
tb(sl, "Interpretation", Inches(6.3), Inches(1.42), Inches(6.5), Inches(0.4),
   size=15, bold=True, color=BLUE)
bullets(sl, [
    ("✓  ", "cLVAE: val NMSE 0.188 — improvement over GN baseline (0.197). Vol activated. Gap 4.1× → 3.8×.", 14, True, GREEN),
    ("✓  ", "Vanilla LVAE: only run achieving real pruning at τ=0.05 (69/100 dims). Noise prevents catastrophic memorisation (train rec stays at 0.006 vs 0.0004 baseline).", 14, False, GREEN),
    ("~  ", "cPLVAE: rec_violated throughout (0.091 > 0.05 threshold). Vol never activated. Joint constraint too tight.", 14, False, ORANGE),
    ("✗  ", "None reached val NMSE < 0.10. Gap persists at 3–5×.", 14, False, RED),
    ("", "", 7, False, BLACK),
    ("→  ", "Noise helps but τ=0.05 limits compression. Next: combine noise with τ=0.20 (the sweet spot).", 14, True, BLUE),
], Inches(6.3), Inches(1.90), Inches(6.5), Inches(5.0), default_size=14)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 7 — Strategy 3: Val Gate (negative result)
# ══════════════════════════════════════════════════════════════════════════════
sl = slide()
header(sl, "Strategy 3 — Validation-Gated Volume Loss  [DONE — Negative Result]",
       "Gate volume on val NMSE < τ  ·  gate never opened  ·  gap increased")

card(sl, Inches(0.3), Inches(1.35), Inches(5.8), Inches(5.7), fill=RGBColor(0xFF,0xF5,0xF2))
tb(sl, "What happened", Inches(0.5), Inches(1.42), Inches(5.5), Inches(0.4),
   size=15, bold=True, color=RED)
bullets(sl, [
    ("✗  ", "val_nmse_ok = 0 for the entire run (all 3 variants). Gate never opened.", 14, True, RED),
    ("   ", "LVAE:   train 0.029 / val 0.226  gap 7.8×  dims 100/100", 13, False, BLACK),
    ("   ", "cLVAE:  train 0.029 / val 0.226  gap 7.9×  dims 100/100", 13, False, BLACK),
    ("   ", "cPLVAE: train 0.080 / val 0.317  gap 4.0×  dims 100/100", 13, False, BLACK),
    ("", "", 7, False, BLACK),
    ("✗  ", "Val NMSE always ~0.23 — the threshold 0.05 is completely unreachable when the gate is blocking compression.", 14, True, RED),
    ("✗  ", "Gap INCREASED vs GN baseline: 7.8× vs 4.1%. The val gate made things WORSE.", 14, True, RED),
], Inches(0.5), Inches(1.90), Inches(5.5), Inches(5.0), default_size=14)

card(sl, Inches(6.4), Inches(1.35), Inches(6.6), Inches(5.7))
tb(sl, "Why removing volume pressure backfires", Inches(6.6), Inches(1.42), Inches(6.2), Inches(0.4),
   size=15, bold=True, color=BLUE)
bullets(sl, [
    "Volume pressure is not only a compression mechanism — it is also a regulariser. By forcing the encoder to map designs into a compact manifold, it limits overfitting capacity.",
    "Removing volume pressure (via the gate) gives the encoder full freedom to use all 100 latent dimensions. More capacity → more memorisation → larger gap.",
    ("→  ", "Result: train rec drops to 0.029 (worse than with vol pressure!) while val NMSE climbs to 0.226.", 14, False, DKGREY),
    ("", "", 7, False, BLACK),
    ("The fix:", "Gate threshold must be reachable. With τ_gate=0.05 and val NMSE always ≥ 0.20, the gate is equivalent to permanently disabling the LVAE.", 14, True, ORANGE),
    ("", "", 7, False, BLACK),
    ("→  ", "Better approach: use τ_gate=0.25 (reachable) OR gate on a relative criterion (val/train ratio < 2×) rather than an absolute threshold.", 14, False, BLUE),
], Inches(6.6), Inches(1.90), Inches(6.2), Inches(5.0), default_size=14)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 8 — Full results table
# ══════════════════════════════════════════════════════════════════════════════
sl = slide()
header(sl, "Complete Results Table",
       "All experiments  ·  constrained LVAE unless noted  ·  ordered by val NMSE")

COLS8 = ["Method", "τ", "Noise σ", "Train NMSE", "Val NMSE", "Gap", "Active dims", "Vol", "Status"]
CW8   = [Inches(3.5), Inches(0.7), Inches(0.8), Inches(1.2), Inches(1.2),
         Inches(0.8), Inches(1.3), Inches(0.7), Inches(1.0)]

ROWS8 = [
    # method, tau, noise, train, val, gap, dims, vol, status
    ["Baseline BN (ep 83 ⚠)",        "0.05", "—",   "0.108", "0.171", "—",    "—",       "No",  "Done"],
    ["τ sweep  τ=0.20  ★ best",       "0.20", "—",   "0.088", "0.182", "—",    "97/100",  "Yes", "Done"],
    ["GN+noise cLVAE",                "0.05", "0.1", "0.050", "0.188", "3.8×", "100/100", "Yes", "Done"],
    ["τ sweep  τ=0.10",               "0.10", "—",   "0.077", "0.191", "—",    "100/100", "Yes", "Done"],
    ["GN encoder cLVAE (baseline)",   "0.05", "—",   "0.048", "0.197", "4.1×", "100/100", "No",  "Done"],
    ["τ sweep  τ=0.05",               "0.05", "—",   "0.067", "0.198", "—",    "100/100", "No",  "Done"],
    ["GN+noise vanilla LVAE",         "0.05", "0.1", "—",     "0.034*","5.3×", "69/100",  "Yes", "Done"],
    ["Val gate cLVAE",                "0.05", "—",   "0.029", "0.226", "7.9×", "100/100", "No",  "Done ✗"],
    ["Val gate vanilla LVAE",         "0.05", "—",   "0.029", "0.226", "7.8×", "100/100", "No",  "Done ✗"],
    ["τ sweep  τ=0.30",               "0.30", "—",   "0.117", "0.239", "—",    "43/100",  "Yes", "Done"],
    ["cPLVAE GN+noise",               "0.05", "0.1", "0.091†","0.311", "3.4×", "100/100", "No",  "Done"],
    ["Val gate cPLVAE",               "0.05", "—",   "0.080†","0.317", "4.0×", "100/100", "No",  "Done ✗"],
    ["τ sweep  τ=0.50",               "0.50", "—",   "0.126", "0.251", "—",    "45/100",  "Yes", "Done"],
    ["τ sweep  τ=0.70",               "0.70", "—",   "0.131", "0.317", "—",    "14/100",  "Yes", "Done"],
    ["τ=0.20 + noise  ← NEW",         "0.20", "0.1", "—",     "—",     "—",    "—",       "—",   "Running"],
]

n_rows = len(ROWS8) + 1
n_cols = len(COLS8)
tbl8 = sl.shapes.add_table(n_rows, n_cols,
                             Inches(0.15), Inches(1.3),
                             sum(CW8), Inches(6.0)).table
for ci, cw in enumerate(CW8):
    tbl8.columns[ci].width = cw
rh8 = Inches(6.0) // n_rows
for ri in range(n_rows):
    tbl8.rows[ri].height = rh8
for ci, h in enumerate(COLS8):
    tcell(tbl8.cell(0, ci), h, size=11, bold=True, color=WHITE, fill=BLUE)

for ri, row in enumerate(ROWS8):
    is_best   = "★" in row[0]
    is_new    = "NEW" in row[0]
    is_bad    = "✗" in row[8]
    fill = RGBColor(0xE8,0xFF,0xF0) if is_best else \
           RGBColor(0xE8,0xF0,0xFF) if is_new  else \
           RGBColor(0xFF,0xF0,0xF0) if is_bad  else \
           (GREY if ri % 2 == 0 else WHITE)
    for ci, val in enumerate(row):
        col = BLACK
        if ci == 4:  # val NMSE
            try:
                v = float(val.replace("*","").replace("†",""))
                col = GREEN if v < 0.185 else (ORANGE if v < 0.205 else RED)
            except: pass
        if ci == 7: col = GREEN if val=="Yes" else (RED if val=="No" else DKGREY)
        if ci == 8: col = RED if "✗" in val else (ORANGE if "Running" in val else GREEN)
        al = PP_ALIGN.LEFT if ci == 0 else PP_ALIGN.CENTER
        tcell(tbl8.cell(ri+1, ci), val, size=10,
              bold=(is_best or is_new), color=col, align=al, fill=fill)

tb(sl, "* val rec (raw) not NMSE  ·  † rec_violated  ·  ★ best val NMSE  ·  ⚠ ep 83 stopped early",
   Inches(0.15), Inches(7.22), Inches(13.0), Inches(0.27),
   size=10, color=DKGREY, italic=True)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 9 — Key findings
# ══════════════════════════════════════════════════════════════════════════════
sl = slide()
header(sl, "Key Findings",
       "What the experiments reveal about LVAE on thermoelastic2D")

card(sl, Inches(0.3), Inches(1.35), Inches(6.2), Inches(5.7))
tb(sl, "What worked", Inches(0.5), Inches(1.42), Inches(5.9), Inches(0.4),
   size=15, bold=True, color=GREEN)
bullets(sl, [
    ("✓  ", "τ = 0.20 is the sweet spot. Best val NMSE = 0.182, 97/100 active dims, vol activated. τ is more impactful than encoder architecture or noise.", 14, True, GREEN),
    ("", "", 7, False, BLACK),
    ("✓  ", "Latent noise (σ=0.1) at τ=0.05 reduces gap from 4.1× → 3.8× and gives val NMSE 0.188. Decoder robustness improves generalisation.", 14, False, GREEN),
    ("", "", 7, False, BLACK),
    ("✓  ", "Vanilla LVAE + noise: only run with real pruning at τ=0.05 (69/100 dims). Noise prevents catastrophic memorisation.", 14, False, GREEN),
    ("", "", 7, False, BLACK),
    ("✓  ", "GN + SN encoder: correct choice regardless. Eliminates BN stats mismatch and bounds Lipschitz constant.", 14, False, GREEN),
    ("", "", 7, False, BLACK),
    ("✓  ", "Sweep answered supervisor question 1: dimensionality sweet spot is ~97 dims at τ=0.20.", 14, False, GREEN),
], Inches(0.5), Inches(1.90), Inches(5.9), Inches(5.0), default_size=14)

card(sl, Inches(6.7), Inches(1.35), Inches(6.3), Inches(5.7))
tb(sl, "What did not work / key insights", Inches(6.9), Inches(1.42), Inches(6.0), Inches(0.4),
   size=15, bold=True, color=RED)
bullets(sl, [
    ("✗  ", "Val gate (absolute τ=0.05): gate never opened. Removing vol pressure increased the gap (7.8× vs 4.1×). Vol pressure IS a regulariser.", 14, True, RED),
    ("", "", 7, False, BLACK),
    ("✗  ", "cPLVAE: joint rec+perf constraint at τ=0.05 is too tight. rec_violated throughout all cPLVAE runs. Needs threshold relaxation.", 14, False, RED),
    ("", "", 7, False, BLACK),
    ("✗  ", "No method achieved val NMSE < 0.10. The 0.05 target on val remains distant.", 14, False, RED),
    ("", "", 7, False, BLACK),
    ("→  ", "Key insight: over-compression (τ≥0.30) hurts val NMSE as much as under-compression (τ≤0.03). The U-shape is the central finding.", 14, True, ORANGE),
    ("", "", 7, False, BLACK),
    ("→  ", "Best unexplored combination: τ=0.20 + noise σ=0.1. Currently running.", 14, True, BLUE),
], Inches(6.9), Inches(1.90), Inches(6.0), Inches(5.0), default_size=14)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 10 — Next steps (aligned to supervisor suggestions)
# ══════════════════════════════════════════════════════════════════════════════
sl = slide()
header(sl, "Next Steps — Aligned with Supervisor Suggestions",
       "Prioritised roadmap based on experimental findings")

steps = [
    (ORANGE, "RUNNING  ·  τ=0.20 + noise σ=0.1  (best two strategies combined)",
     "Should yield val NMSE ≤ 0.182 with more aggressive pruning. Supervisor question 1 partly answered; this validates whether the two improvements are additive."),
    (BLUE,   "Dataset complexity vs. dimensionality  (supervisor priority)",
     "Subset by weight=1.0 (structural only) vs weight=0.0 (thermal only): how many dims does each sub-problem need? Subset by volfrac range. This directly addresses 'explore LVAE on subsets' and 'relationship between GLVAE dimension and dataset complexity'."),
    (BLUE,   "Condition-aware decoder  (supervisor: 'condition-aware decoder so latent space doesn't need to double up')",
     "Concatenate conditions (volfrac, weight, BC hash) to the decoder input. Latent z encodes only topology structure — not conditions. Should reduce required active dims and improve generalisation."),
    (DKGREY, "Val gate with reachable threshold  (τ_gate = 0.20–0.25)",
     "The absolute τ=0.05 gate is permanently closed. Gate on τ_gate=0.20 (reachable) OR on relative criterion val/train ratio < 2×. Combines benefits of compression guard with actual vol pressure."),
    (DKGREY, "Visualisation study  (supervisor: 'overall visualisations of different LVAE variants')",
     "Compare LVAE variants on: interpolation quality, unconditional sampling, latent clustering by condition (weight, volfrac), placement of unseen conditions."),
]

for i, (col, title, desc) in enumerate(steps):
    y = Inches(1.35) + i * Inches(1.2)
    rect(sl, Inches(0.3), y + Inches(0.1), Inches(0.12), Inches(0.9), fill=col)
    card(sl, Inches(0.5), y, Inches(12.5), Inches(1.1), fill=GREY)
    tb(sl, title, Inches(0.68), y + Inches(0.05), Inches(12.0), Inches(0.37),
       size=14, bold=True, color=BLACK)
    tb(sl, desc, Inches(0.68), y + Inches(0.45), Inches(12.0), Inches(0.62),
       size=12, color=DKGREY)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 11 — Summary
# ══════════════════════════════════════════════════════════════════════════════
sl = slide()
header(sl, "Summary", "Progress, key numbers, and direction")

card(sl, Inches(0.3), Inches(1.35), Inches(4.1), Inches(5.7))
tb(sl, "Completed experiments", Inches(0.5), Inches(1.42), Inches(3.8), Inches(0.4),
   size=14, bold=True, color=GREEN)
bullets(sl, [
    ("✓  ", "GN + SN encoder — all 3 variants", 13, False, BLACK),
    ("✓  ", "Latent noise σ=0.1 — all 3 variants", 13, False, BLACK),
    ("✓  ", "Val gate τ=0.05 — all 3 variants", 13, False, BLACK),
    ("✓  ", "τ sweep: 8 values (0.01–0.70)", 13, False, BLACK),
    ("⟳  ", "τ=0.20 + noise — running", 13, False, ORANGE),
    ("", "", 6, False, BLACK),
    ("✓  ", "Dataset confirmed: 14.4k train / 1.8k val+test", 13, False, DKGREY),
    ("✓  ", "All tracked on WandB (spectral_norm_encoder)", 13, False, DKGREY),
], Inches(0.5), Inches(1.90), Inches(3.8), Inches(5.0), default_size=13)

card(sl, Inches(4.65), Inches(1.35), Inches(3.8), Inches(5.7))
tb(sl, "Best results", Inches(4.85), Inches(1.42), Inches(3.5), Inches(0.4),
   size=14, bold=True, color=BLUE)
bullets(sl, [
    ("★  ", "Val NMSE 0.182", 15, True, GREEN),
    ("   ", "τ=0.20 sweep / 97 active dims", 12, False, DKGREY),
    ("", "", 6, False, BLACK),
    ("   ", "Val NMSE 0.188", 14, False, GREEN),
    ("   ", "cLVAE + noise / τ=0.05", 12, False, DKGREY),
    ("", "", 6, False, BLACK),
    ("   ", "69/100 active dims", 14, False, GREEN),
    ("   ", "Vanilla LVAE + noise (only pruned run)", 12, False, DKGREY),
    ("", "", 9, False, BLACK),
    ("   ", "Baseline BN: val NMSE 0.171 (ep 83, early stopped — not a fair comparison)", 12, False, DKGREY),
    ("", "", 6, False, BLACK),
    ("   ", "Target: val NMSE < 0.05", 13, False, RED),
    ("   ", "Remaining gap: ~3.6–4×", 13, True, RED),
], Inches(4.85), Inches(1.90), Inches(3.5), Inches(5.0), default_size=13)

card(sl, Inches(8.7), Inches(1.35), Inches(4.3), Inches(5.7))
tb(sl, "Conclusions", Inches(8.9), Inches(1.42), Inches(4.0), Inches(0.4),
   size=14, bold=True, color=BLUE)
bullets(sl, [
    "τ is the dominant hyperparameter — more impactful than encoder type or noise.",
    "Volume pressure is both a compression mechanism AND a regulariser. Disabling it (val gate) increases overfitting.",
    "The U-shape (unreachable → sweet spot → over-compress) is the central finding. It directly answers the supervisor's 'dimensionality sweet spot' question.",
    "Noise injection and τ tuning are complementary and unexplored in combination — that is the running experiment.",
    "Next frontier: dataset subsets by condition (weight, volfrac) to understand how dataset complexity drives the required latent dimensionality.",
], Inches(8.9), Inches(1.90), Inches(4.0), Inches(5.0), default_size=13)


# ══════════════════════════════════════════════════════════════════════════════
OUT = "/cluster/home/tcasartelli/projects/EngiOpt/engiopt/vanilla_thomas_thermo2D/spectral_norm_encoder_presentation.pptx"
prs.save(OUT)
print(f"Saved: {OUT}  ({len(prs.slides)} slides)")
