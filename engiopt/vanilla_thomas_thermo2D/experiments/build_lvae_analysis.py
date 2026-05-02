"""Build thermoelastic2d_lvae_analysis.pptx — vanilla LVAE comparison."""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# ── colours ────────────────────────────────────────────────────────────────────
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
BLACK  = RGBColor(0x1A, 0x1A, 0x2E)
BLUE   = RGBColor(0x1F, 0x6F, 0xEB)
LBLUE  = RGBColor(0xD6, 0xE8, 0xFF)
GREEN  = RGBColor(0x0A, 0x7D, 0x57)
ORANGE = RGBColor(0xE8, 0x7D, 0x14)
RED    = RGBColor(0xC0, 0x39, 0x2B)
GREY   = RGBColor(0xF2, 0xF4, 0xF7)
DKGREY = RGBColor(0x55, 0x65, 0x7A)
YELLOW = RGBColor(0xFF, 0xD6, 0x00)

W = Inches(13.33)
H = Inches(7.5)

prs = Presentation()
prs.slide_width  = W
prs.slide_height = H
BLANK = prs.slide_layouts[6]

# ── helpers ────────────────────────────────────────────────────────────────────

def add_slide():
    sl = prs.slides.add_slide(BLANK)
    bg = sl.background.fill
    bg.solid()
    bg.fore_color.rgb = WHITE
    return sl

def tb(slide, text, l, t, w, h,
       size=16, bold=False, color=BLACK, align=PP_ALIGN.LEFT, italic=False):
    txb = slide.shapes.add_textbox(l, t, w, h)
    txb.word_wrap = True
    tf = txb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    return txb

def header_bar(slide, title, subtitle=None):
    bar = slide.shapes.add_shape(1, Inches(0), Inches(0), W, Inches(1.15))
    bar.fill.solid()
    bar.fill.fore_color.rgb = BLUE
    bar.line.fill.background()
    tf = bar.text_frame
    tf.word_wrap = False
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    r = p.add_run()
    r.text = title
    r.font.size = Pt(28)
    r.font.bold = True
    r.font.color.rgb = WHITE
    if subtitle:
        p2 = tf.add_paragraph()
        p2.alignment = PP_ALIGN.LEFT
        r2 = p2.add_run()
        r2.text = subtitle
        r2.font.size = Pt(14)
        r2.font.color.rgb = RGBColor(0xCC, 0xDD, 0xFF)

def rect(slide, l, t, w, h, fill=GREY, border=None):
    shp = slide.shapes.add_shape(1, l, t, w, h)
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    if border:
        shp.line.color.rgb = border
        shp.line.width = Pt(1.5)
    else:
        shp.line.fill.background()
    return shp

def card(slide, l, t, w, h, fill=GREY):
    return rect(slide, l, t, w, h, fill=fill, border=BLUE)

def bullets(slide, items, l, t, w, h, default_size=14):
    txb = slide.shapes.add_textbox(l, t, w, h)
    txb.word_wrap = True
    tf = txb.text_frame
    tf.word_wrap = True
    first = True
    for item in items:
        if isinstance(item, tuple):
            prefix, text, size, bold, color = item
        else:
            prefix, text, size, bold, color = "•  ", item, default_size, False, BLACK
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.alignment = PP_ALIGN.LEFT
        r = p.add_run()
        r.text = prefix + text
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.color.rgb = color

def table_cell(cell, text, size=12, bold=False, color=BLACK,
               align=PP_ALIGN.CENTER, fill=None):
    if fill:
        cell.fill.solid()
        cell.fill.fore_color.rgb = fill
    tf = cell.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    runs = p.runs
    r = runs[0] if runs else p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = color


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 1 — Title
# ══════════════════════════════════════════════════════════════════════════════
sl = add_slide()
tb(sl, "Vanilla LVAE on Thermoelastic 2D",
   Inches(1.0), Inches(1.8), Inches(11.3), Inches(1.4),
   size=36, bold=True, color=BLACK, align=PP_ALIGN.CENTER)
tb(sl, "Ablation study: Baseline BN  →  GN encoder  →  GN + Latent Noise",
   Inches(1.0), Inches(3.3), Inches(11.3), Inches(0.7),
   size=20, color=DKGREY, align=PP_ALIGN.CENTER)
tb(sl, "What changed, why it matters, and what the numbers say",
   Inches(1.0), Inches(4.1), Inches(11.3), Inches(0.5),
   size=16, color=DKGREY, align=PP_ALIGN.CENTER, italic=True)
rect(sl, Inches(0), Inches(6.9), W, Inches(0.6), fill=BLUE)
tb(sl, "EngiOpt  ·  ETH Zürich  ·  April 2026",
   Inches(0.3), Inches(6.95), Inches(6), Inches(0.5), size=13, color=WHITE)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 2 — The three runs at a glance (summary table)
# ══════════════════════════════════════════════════════════════════════════════
sl = add_slide()
header_bar(sl, "Three Runs at a Glance",
           "Vanilla LVAE  ·  thermoelastic2D  ·  seed 1  ·  latent_dim = 100")

# ── table ──────────────────────────────────────────────────────────────────
COLS = ["", "Baseline BN", "GN encoder\n(no noise)", "GN + Latent Noise\n(σ = 0.1)"]
COL_W = [Inches(2.8), Inches(3.0), Inches(3.0), Inches(3.7)]
ROWS = [
    ("Encoder",         "BatchNorm",    "GroupNorm (8g)\n+ Spectral Norm",  "GroupNorm (8g)\n+ Spectral Norm"),
    ("Latent noise σ",  "—",            "—",                                "0.1"),
    ("Early stopping",  "patience 10\nfrom ep. 0",
                        "patience 10\nfrom ep. 0",
                        "patience 50\nfrom ep. 2000"),
    ("Last epoch",      "9 999  (full)", "57  ⚠ premature",                "1 033  (running)"),
    ("Train rec",       "0.000410",     "0.02939",                          "0.008553"),
    ("Val rec",         "0.03309",      "0.03246",                          "0.03121  ✓"),
    ("Gap  (val/train)","80×  ✗",       "1.10×  ⚠*",                        "3.65×"),
    ("Active dims",     "65 / 100",     "100 / 100",                        "69 / 100"),
    ("Vol active?",     "Yes (late)",   "No",                               "Yes"),
    ("Status",          "Done",         "Stopped early",                    "Running"),
]

n_rows = len(ROWS) + 1
n_cols = len(COLS)
tbl = sl.shapes.add_table(
    n_rows, n_cols,
    Inches(0.25), Inches(1.3),
    sum(COL_W), Inches(5.95),
).table
for ci, cw in enumerate(COL_W):
    tbl.columns[ci].width = cw
for ri in range(n_rows):
    tbl.rows[ri].height = Inches(5.95 / n_rows)

# header
for ci, col in enumerate(COLS):
    c = tbl.cell(0, ci)
    table_cell(c, col, size=13, bold=True, color=WHITE, fill=BLUE)

# data
row_fills = [
    GREY, WHITE,
    GREY, WHITE,
    GREY, WHITE,
    GREY, WHITE,
    GREY, WHITE,
]
highlight = {
    # (row_idx, col_idx): color
    (5, 3): GREEN,   # val rec GN+noise best
    (6, 1): RED,     # gap baseline
    (6, 2): ORANGE,  # gap GN (premature)
    (9, 1): GREEN,   # status Done
    (9, 2): ORANGE,  # stopped early
    (9, 3): ORANGE,  # running
}
for ri, row in enumerate(ROWS):
    f = row_fills[ri % len(row_fills)]
    for ci, val in enumerate(row):
        c = tbl.cell(ri + 1, ci)
        col = highlight.get((ri + 1, ci), BLACK)
        al = PP_ALIGN.LEFT if ci == 0 else PP_ALIGN.CENTER
        table_cell(c, val, size=12, color=col, align=al, fill=f)

tb(sl, "* GN encoder gap 1.10× is misleading — both train and val are high because the run stopped at epoch 57 (model had not converged).",
   Inches(0.25), Inches(7.1), Inches(12.8), Inches(0.35),
   size=11, color=DKGREY, italic=True)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 3 — Baseline BN deep-dive
# ══════════════════════════════════════════════════════════════════════════════
sl = add_slide()
header_bar(sl, "Run 1 — Baseline: BatchNorm Encoder",
           "Full training (10 000 epochs)  ·  the overfitting benchmark")

card(sl, Inches(0.3), Inches(1.35), Inches(5.9), Inches(5.7))
tb(sl, "What happened", Inches(0.5), Inches(1.42), Inches(5.7), Inches(0.35),
   size=15, bold=True, color=BLUE)
bullets(sl, [
    ("•  ", "The model trained to completion (epoch 9999) and strongly memorised the training set.", 14, False, BLACK),
    ("    ", "", 6, False, BLACK),
    ("•  ", "Train rec collapsed to 0.000410 — essentially zero reconstruction error on training samples.", 14, False, BLACK),
    ("    ", "", 6, False, BLACK),
    ("•  ", "Val rec stayed at 0.03309. The model learned to compress training samples perfectly but generalised only weakly.", 14, False, BLACK),
    ("    ", "", 6, False, BLACK),
    ("•  ", "Gap of 80× — the most extreme overfitting signal. The encoder memorised, not generalised.", 14, False, RED),
    ("    ", "", 6, False, BLACK),
    ("•  ", "Volume did activate (latent space was compressed to 65/100 dims), but only because train rec was far below threshold.", 14, False, BLACK),
    ("    ", "", 6, False, BLACK),
    ("•  ", "BatchNorm running statistics computed on training data cause a small distribution shift at eval time, but the dominant effect here is capacity-driven memorisation.", 14, False, DKGREY),
], Inches(0.5), Inches(1.85), Inches(5.7), Inches(5.1), default_size=14)

card(sl, Inches(6.4), Inches(1.35), Inches(6.6), Inches(5.7))
tb(sl, "Key numbers", Inches(6.6), Inches(1.42), Inches(6.3), Inches(0.35),
   size=15, bold=True, color=BLUE)

metrics = [
    ("Train rec", "0.000410", RED,   "Model memorised training data"),
    ("Val rec",   "0.03309",  BLACK, "Generalisation unchanged"),
    ("Gap",       "80×",      RED,   "Catastrophic overfitting"),
    ("Active dims","65 / 100",BLACK, "35 dims pruned by vol pressure"),
    ("Vol active", "Yes",     GREEN, "Activated late in training"),
    ("Epoch",     "9 999",    BLACK, "Fully trained"),
]
y0 = Inches(1.85)
for label, val, vcol, note in metrics:
    rect(sl, Inches(6.6), y0, Inches(6.2), Inches(0.72), fill=GREY)
    tb(sl, label, Inches(6.75), y0 + Inches(0.04), Inches(2.0), Inches(0.32),
       size=13, color=DKGREY)
    tb(sl, val, Inches(8.8), y0 + Inches(0.04), Inches(1.8), Inches(0.32),
       size=14, bold=True, color=vcol, align=PP_ALIGN.CENTER)
    tb(sl, note, Inches(6.75), y0 + Inches(0.38), Inches(6.0), Inches(0.28),
       size=11, color=DKGREY, italic=True)
    y0 += Inches(0.78)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 4 — GN encoder without noise
# ══════════════════════════════════════════════════════════════════════════════
sl = add_slide()
header_bar(sl, "Run 2 — GN + SN Encoder (no noise)",
           "Stopped at epoch 57  ·  aggressive early stopping prevented convergence")

card(sl, Inches(0.3), Inches(1.35), Inches(5.9), Inches(5.7))
tb(sl, "What happened", Inches(0.5), Inches(1.42), Inches(5.7), Inches(0.35),
   size=15, bold=True, color=BLUE)
bullets(sl, [
    ("⚠  ", "This run was configured with patience=10 from epoch 0 — the most aggressive early stopping possible.", 14, True, ORANGE),
    ("    ", "", 6, False, BLACK),
    ("•  ", "At epoch 57, both train rec (0.029) and val rec (0.032) are still high. The model had not yet entered the low-loss regime.", 14, False, BLACK),
    ("    ", "", 6, False, BLACK),
    ("•  ", "Early stopping triggered because val rec did not improve for 10 consecutive epochs in the very early noisy phase of training.", 14, False, BLACK),
    ("    ", "", 6, False, BLACK),
    ("•  ", "The apparent gap of 1.10× is not a sign of good generalisation — it simply means the model equally failed on both sets (underfitting).", 14, False, ORANGE),
    ("    ", "", 6, False, BLACK),
    ("•  ", "Volume never activated (pruning_epoch=500 not yet reached). Active dims = 100/100.", 14, False, BLACK),
    ("    ", "", 6, False, BLACK),
    ("•  ", "Conclusion: this run is not usable for ablation. A properly converged GN-only run needs patience≥50 from epoch≥2000.", 14, True, RED),
], Inches(0.5), Inches(1.85), Inches(5.7), Inches(5.1), default_size=14)

card(sl, Inches(6.4), Inches(1.35), Inches(6.6), Inches(5.7))
tb(sl, "Key numbers", Inches(6.6), Inches(1.42), Inches(6.3), Inches(0.35),
   size=15, bold=True, color=BLUE)

metrics = [
    ("Train rec",  "0.02939",  ORANGE, "Model has not converged yet"),
    ("Val rec",    "0.03246",  ORANGE, "Both high — underfitting"),
    ("Gap",        "1.10×",    ORANGE, "Misleading: both losses high"),
    ("Active dims","100 / 100",BLACK,  "Pruning not reached (ep < 500)"),
    ("Vol active", "No",       BLACK,  ""),
    ("Epoch",      "57",       RED,    "Stopped far too early"),
]
y0 = Inches(1.85)
for label, val, vcol, note in metrics:
    rect(sl, Inches(6.6), y0, Inches(6.2), Inches(0.72), fill=GREY)
    tb(sl, label, Inches(6.75), y0 + Inches(0.04), Inches(2.0), Inches(0.32),
       size=13, color=DKGREY)
    tb(sl, val, Inches(8.8), y0 + Inches(0.04), Inches(1.8), Inches(0.32),
       size=14, bold=True, color=vcol, align=PP_ALIGN.CENTER)
    tb(sl, note, Inches(6.75), y0 + Inches(0.38), Inches(6.0), Inches(0.28),
       size=11, color=DKGREY, italic=True)
    y0 += Inches(0.78)

tb(sl, "ACTION NEEDED: Re-run GN encoder without noise with early_stopping_start_epoch=2000, patience=50 to get a fair ablation point.",
   Inches(6.45), Inches(6.45), Inches(6.5), Inches(0.6),
   size=12, bold=True, color=RED)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 5 — GN + Latent Noise
# ══════════════════════════════════════════════════════════════════════════════
sl = add_slide()
header_bar(sl, "Run 3 — GN + SN Encoder + Latent Noise (σ = 0.1)",
           "Epoch 1033 / 10 000  ·  still running  ·  early stopping from epoch 2000")

card(sl, Inches(0.3), Inches(1.35), Inches(5.9), Inches(5.7))
tb(sl, "What's happening so far", Inches(0.5), Inches(1.42), Inches(5.7), Inches(0.35),
   size=15, bold=True, color=BLUE)
bullets(sl, [
    ("✓  ", "Train rec = 0.008553. The model is learning but regularised: noise prevents collapsing train rec to near-zero.", 14, False, GREEN),
    ("    ", "", 6, False, BLACK),
    ("✓  ", "Val rec = 0.03121 — already better than the fully-trained baseline (0.03309). The decoder generalises more robustly with noise.", 14, True, GREEN),
    ("    ", "", 6, False, BLACK),
    ("•  ", "Gap = 3.65×. Still large, but massively better than the baseline's 80×. The noise forces the decoder to handle imprecise latent codes.", 14, False, BLACK),
    ("    ", "", 6, False, BLACK),
    ("•  ", "Active dims = 69/100. Volume has activated and already pruned 31 dimensions — at only epoch 1033 vs the baseline's 65 dims at epoch 9999.", 14, False, BLACK),
    ("    ", "", 6, False, BLACK),
    ("•  ", "Train NMSE is near the 0.05 threshold — volume pressure is gated and working. Model is being compressed while generalising.", 14, False, BLACK),
    ("    ", "", 6, False, BLACK),
    ("•  ", "Early stopping not yet active (starts epoch 2000). The run has ~7000 more epochs. Expect further pruning and convergence.", 14, False, DKGREY),
], Inches(0.5), Inches(1.85), Inches(5.7), Inches(5.1), default_size=14)

card(sl, Inches(6.4), Inches(1.35), Inches(6.6), Inches(5.7))
tb(sl, "Key numbers", Inches(6.6), Inches(1.42), Inches(6.3), Inches(0.35),
   size=15, bold=True, color=BLUE)

metrics = [
    ("Train rec",  "0.008553",  BLACK, "Regularised — noise prevents memorising"),
    ("Val rec",    "0.03121",   GREEN, "Better than fully-trained baseline!"),
    ("Gap",        "3.65×",     ORANGE,"Reduced from 80× — noise works"),
    ("Active dims","69 / 100",  GREEN, "31 dims pruned at only ep 1033"),
    ("Vol active", "Yes",       GREEN, "Compression is happening"),
    ("Epoch",      "1 033 / 10 000", ORANGE, "Still running — results will improve"),
]
y0 = Inches(1.85)
for label, val, vcol, note in metrics:
    rect(sl, Inches(6.6), y0, Inches(6.2), Inches(0.72), fill=GREY)
    tb(sl, label, Inches(6.75), y0 + Inches(0.04), Inches(2.0), Inches(0.32),
       size=13, color=DKGREY)
    tb(sl, val, Inches(8.8), y0 + Inches(0.04), Inches(2.1), Inches(0.32),
       size=14, bold=True, color=vcol, align=PP_ALIGN.CENTER)
    tb(sl, note, Inches(6.75), y0 + Inches(0.38), Inches(6.0), Inches(0.28),
       size=11, color=DKGREY, italic=True)
    y0 += Inches(0.78)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 6 — Side-by-side analysis: what the noise actually does
# ══════════════════════════════════════════════════════════════════════════════
sl = add_slide()
header_bar(sl, "Analysis — Why Latent Noise Helps",
           "Mechanistic explanation and interpretation of the gap reduction")

card(sl, Inches(0.3), Inches(1.35), Inches(6.2), Inches(2.65))
tb(sl, "Without noise (baseline BN)", Inches(0.5), Inches(1.42), Inches(5.9), Inches(0.35),
   size=15, bold=True, color=RED)
bullets(sl, [
    "The encoder maps each training sample to a precise, tight latent code. The decoder memorises the mapping from these exact codes → designs.",
    "For a val sample, the encoder outputs a slightly different code (distribution shift). The decoder, trained only on tight codes, produces large errors.",
    "Result: train rec → 0, val rec stays at 0.033. The 80× gap is the encoder memorising, not learning a generalisable representation.",
], Inches(0.5), Inches(1.85), Inches(5.9), Inches(2.1), default_size=14)

card(sl, Inches(0.3), Inches(4.15), Inches(6.2), Inches(2.75))
tb(sl, "With noise (σ = 0.1)", Inches(0.5), Inches(4.22), Inches(5.9), Inches(0.35),
   size=15, bold=True, color=GREEN)
bullets(sl, [
    "At every training step, Gaussian noise is added to z before decoding. The decoder never sees the same code twice for the same sample.",
    "The decoder is forced to learn: 'any code near the encoder output should reconstruct this design.' This is neighbourhood robustness.",
    "Result: train rec stays at 0.0086 (decoder can't memorise exact codes). Val rec improves to 0.031 because the decoder handles imprecise codes gracefully.",
    "The gap drops from 80× → 3.65×. Volume activates at epoch 1033 with 69 active dims already pruned.",
], Inches(0.5), Inches(4.65), Inches(5.9), Inches(2.15), default_size=14)

card(sl, Inches(6.7), Inches(1.35), Inches(6.3), Inches(5.55))
tb(sl, "Design choices — why these values?", Inches(6.9), Inches(1.42), Inches(6.0), Inches(0.35),
   size=15, bold=True, color=BLUE)
bullets(sl, [
    ("•  ", "σ = 0.1  — conservative. Large σ can destabilise training; small σ has no effect. 0.1 ≈ 10% of a typical latent std.", 14, False, BLACK),
    ("    ", "", 6, False, BLACK),
    ("•  ", "Noise only on active dims — pruned dimensions are frozen at their mean. Adding noise to already-zeroed dims would interfere with the pruning signal.", 14, False, BLACK),
    ("    ", "", 6, False, BLACK),
    ("•  ", "Clean z for volume + pruning — the volume loss and EMA statistics use the noiseless z, so compression is driven by the true latent distribution, not an artificially noisy one.", 14, False, BLACK),
    ("    ", "", 6, False, BLACK),
    ("•  ", "Noise off at eval — val and test always use the clean encoder output, so val rec is a fair measure of generalisation.", 14, False, BLACK),
    ("    ", "", 6, False, BLACK),
    ("•  ", "Analogy: Dropout in the latent space. Just as dropout prevents co-adaptation of neurons, latent noise prevents the decoder from relying on exact codes.", 14, False, DKGREY),
], Inches(6.9), Inches(1.85), Inches(6.0), Inches(4.95), default_size=14)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 7 — Visual gap comparison (bar chart as shapes)
# ══════════════════════════════════════════════════════════════════════════════
sl = add_slide()
header_bar(sl, "Val vs Train Reconstruction Error — Visual Comparison",
           "All three runs  ·  same scale  ·  val rec is the primary generalisation metric")

# Draw simple bar chart using shapes
# Normalize: max val = baseline train_rec is smallest, baseline val rec ≈ 0.033
# Let's show both train_rec and val_rec per run

runs = [
    ("Baseline\nBN (ep 9999)", 0.000410, 0.03309),
    ("GN encoder\n(ep 57 ⚠)", 0.02939,  0.03246),
    ("GN + Noise\n(ep 1033)", 0.008553, 0.03121),
]

MAX_VAL = 0.040
CHART_TOP  = Inches(1.6)
CHART_H    = Inches(4.0)
CHART_LEFT = Inches(1.5)
CHART_W    = Inches(10.8)
BAR_W      = Inches(1.3)

# axis background
rect(sl, CHART_LEFT - Inches(0.05), CHART_TOP, CHART_W + Inches(0.1), CHART_H + Inches(0.05),
     fill=GREY)

# y-axis grid lines and labels
for yval, label in [(0.0, "0"), (0.01, "0.010"), (0.02, "0.020"), (0.03, "0.030"), (0.040, "0.040")]:
    y = CHART_TOP + CHART_H - (yval / MAX_VAL) * CHART_H
    rect(sl, CHART_LEFT, y, CHART_W, Pt(1), fill=WHITE)
    tb(sl, label, CHART_LEFT - Inches(0.95), y - Inches(0.14), Inches(0.88), Inches(0.3),
       size=11, color=DKGREY, align=PP_ALIGN.RIGHT)

# bars
group_w = CHART_W / len(runs)
for i, (name, train_rec, val_rec) in enumerate(runs):
    cx = CHART_LEFT + i * group_w + group_w / 2

    # train bar (left of centre)
    bh_t = (train_rec / MAX_VAL) * CHART_H
    bx_t = cx - BAR_W - Inches(0.08)
    by_t = CHART_TOP + CHART_H - bh_t
    bar_fill = GREEN if train_rec < 0.002 else (ORANGE if train_rec < 0.015 else BLACK)
    rect(sl, bx_t, by_t, BAR_W, bh_t, fill=bar_fill)
    tb(sl, f"{train_rec:.4f}", bx_t, by_t - Inches(0.28), BAR_W, Inches(0.28),
       size=10, bold=True, color=bar_fill, align=PP_ALIGN.CENTER)

    # val bar (right of centre)
    bh_v = (val_rec / MAX_VAL) * CHART_H
    bx_v = cx + Inches(0.08)
    by_v = CHART_TOP + CHART_H - bh_v
    vfill = GREEN if val_rec < 0.032 else (ORANGE if val_rec < 0.035 else RED)
    rect(sl, bx_v, by_v, BAR_W, bh_v, fill=vfill)
    tb(sl, f"{val_rec:.4f}", bx_v, by_v - Inches(0.28), BAR_W, Inches(0.28),
       size=10, bold=True, color=vfill, align=PP_ALIGN.CENTER)

    # run label
    tb(sl, name, cx - group_w / 2 + Inches(0.1), CHART_TOP + CHART_H + Inches(0.08),
       group_w - Inches(0.2), Inches(0.6),
       size=12, color=BLACK, align=PP_ALIGN.CENTER)

# legend
legend_y = Inches(5.9)
rect(sl, Inches(4.5), legend_y, Inches(0.35), Inches(0.25), fill=BLUE)
tb(sl, "Train rec", Inches(4.9), legend_y, Inches(1.5), Inches(0.25), size=12, color=BLACK)
rect(sl, Inches(6.5), legend_y, Inches(0.35), Inches(0.25), fill=RED)
tb(sl, "Val rec", Inches(6.9), legend_y, Inches(1.5), Inches(0.25), size=12, color=BLACK)

tb(sl, "Note: GN encoder (ep 57) bars show underfitting, not generalisation — both values high because training stopped before convergence.",
   Inches(0.3), Inches(6.8), Inches(12.7), Inches(0.35), size=11, color=DKGREY, italic=True)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 8 — What to expect when the noise run finishes
# ══════════════════════════════════════════════════════════════════════════════
sl = add_slide()
header_bar(sl, "Projections — What to Expect When the Run Completes",
           "GN + Noise run  ·  currently ep 1033 / 10 000  ·  early stopping from ep 2000")

card(sl, Inches(0.3), Inches(1.35), Inches(6.2), Inches(5.7))
tb(sl, "Likely trajectory", Inches(0.5), Inches(1.42), Inches(5.9), Inches(0.35),
   size=15, bold=True, color=BLUE)
bullets(sl, [
    ("1. ", "Train rec will keep decreasing slowly (noise prevents zero, but the model continues to improve).", 14, False, BLACK),
    ("   ", "", 6, False, BLACK),
    ("2. ", "Val rec may decrease further or plateau. The current 0.031 is already the best observed — if it drops below 0.025 that would be a strong result.", 14, False, BLACK),
    ("   ", "", 6, False, BLACK),
    ("3. ", "Active dims will continue decreasing as vol pressure prunes more dimensions. If val rec stays low, pruning should be more aggressive than the baseline (65 dims).", 14, False, BLACK),
    ("   ", "", 6, False, BLACK),
    ("4. ", "Early stopping (from ep 2000, patience 50) will stop the run once val rec stops improving. This is the right termination criterion.", 14, False, BLACK),
    ("   ", "", 6, False, BLACK),
    ("5. ", "If val rec stops improving around 0.030–0.032 with 50–70 active dims, the noise run is strictly better than the baseline in terms of generalisation quality.", 14, False, GREEN),
    ("   ", "", 6, False, BLACK),
    ("6. ", "Risk: if the gap remains at 3.65× until the end, it means the encoder still overfits and we need stronger regularisation (orthogonality + val gate combined).", 14, False, ORANGE),
], Inches(0.5), Inches(1.85), Inches(5.9), Inches(5.1), default_size=14)

card(sl, Inches(6.7), Inches(1.35), Inches(6.3), Inches(5.7))
tb(sl, "Missing ablation: GN alone", Inches(6.9), Inches(1.42), Inches(6.0), Inches(0.35),
   size=15, bold=True, color=BLUE)
bullets(sl, [
    ("⚠  ", "The GN encoder run (without noise) stopped at epoch 57 — too early to be useful.", 14, True, ORANGE),
    ("   ", "", 6, False, BLACK),
    ("   ", "To properly isolate the effect of latent noise, we need a GN-only run that converges with the same early stopping settings.", 14, False, BLACK),
    ("   ", "", 6, False, BLACK),
    ("   ", "Proposed re-run config:", 14, True, BLUE),
    ("   ", "• early_stopping_start_epoch = 2000", 13, False, DKGREY),
    ("   ", "• patience = 50", 13, False, DKGREY),
    ("   ", "• latent_noise_sigma = 0.0  (no noise)", 13, False, DKGREY),
    ("   ", "• all other params identical to noise run", 13, False, DKGREY),
    ("   ", "", 6, False, BLACK),
    ("   ", "This would let us answer: how much of the improvement is GN vs. how much is the noise?", 14, False, BLACK),
    ("   ", "", 6, False, BLACK),
    ("   ", "For now, the fair comparison is:", 14, True, BLUE),
    ("   ", "Baseline BN (fully trained) vs GN+Noise (ep 1033, running)", 13, False, DKGREY),
    ("   ", "→ Val rec 0.033 → 0.031  ·  Gap 80× → 3.65×", 13, True, GREEN),
], Inches(6.9), Inches(1.85), Inches(6.0), Inches(5.1), default_size=14)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 9 — Next steps
# ══════════════════════════════════════════════════════════════════════════════
sl = add_slide()
header_bar(sl, "Next Steps for the Vanilla LVAE Ablation",
           "In priority order")

steps = [
    (GREEN,  "Wait for GN + Noise run to complete (ep 2000+)",
     "The run is at epoch 1033. Early stopping from epoch 2000 will determine the final val rec and active dim count. This is the most important data point — wait before drawing conclusions."),
    (ORANGE, "Re-run GN encoder WITHOUT noise with correct early stopping",
     "Use early_stopping_start_epoch=2000, patience=50, latent_noise_sigma=0.0. This gives the missing ablation point to isolate the effect of noise vs. the GN encoder change."),
    (ORANGE, "If val gap persists (>2×): add val-gate to noise run",
     "The val-gate variants are also running. If the val gate alone closes the gap further, the combination (GN + noise + val gate) may be the strongest regulariser."),
    (BLUE,   "Analyse active dim count at convergence",
     "The baseline compressed to 65/100 dims. If the noise run converges at <60 dims with better val rec, it means the model learned a more compact AND generalisable representation — a double win."),
    (DKGREY, "Extend analysis to constrained LVAE and PLVAE",
     "These ablations are for the vanilla LVAE. The constrained and PLVAE variants have their own noise runs running in parallel. Compare results across all three architectures to see if the benefit of noise is consistent."),
]

for i, (col, title, desc) in enumerate(steps):
    y = Inches(1.35) + i * Inches(1.18)
    rect(sl, Inches(0.3), y + Inches(0.1), Inches(0.12), Inches(0.9), fill=col)
    card(sl, Inches(0.5), y, Inches(12.5), Inches(1.1), fill=GREY)
    tb(sl, f"{i+1}.  {title}", Inches(0.68), y + Inches(0.06), Inches(12.0), Inches(0.38),
       size=14, bold=True, color=BLACK)
    tb(sl, desc, Inches(0.68), y + Inches(0.47), Inches(12.0), Inches(0.6),
       size=13, color=DKGREY)


# ══════════════════════════════════════════════════════════════════════════════
OUT = "/cluster/home/tcasartelli/projects/EngiOpt/engiopt/vanilla_thomas_thermo2D/thermoelastic2d_lvae_analysis.pptx"
prs.save(OUT)
print(f"Saved: {OUT}")
print(f"Slides: {len(prs.slides)}")
