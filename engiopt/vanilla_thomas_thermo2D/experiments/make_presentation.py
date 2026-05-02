from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
import copy

prs = Presentation()
prs.slide_width  = Inches(13.33)
prs.slide_height = Inches(7.5)

# ── colour palette ──────────────────────────────────────────────────────────
DARK_BG   = RGBColor(0x1E, 0x1E, 0x2E)
ACCENT    = RGBColor(0x89, 0xB4, 0xFA)   # blue
ACCENT2   = RGBColor(0xA6, 0xE3, 0xA1)   # green
ACCENT3   = RGBColor(0xF3, 0x8B, 0xA8)   # pink/red
WHITE     = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_GRAY= RGBColor(0xCC, 0xC0, 0xDE)
YELLOW    = RGBColor(0xF9, 0xE2, 0xAF)

blank_layout = prs.slide_layouts[6]   # completely blank

# ── helpers ─────────────────────────────────────────────────────────────────
def bg(slide, color=DARK_BG):
    from pptx.util import Emu
    shape = slide.shapes.add_shape(1, 0, 0, prs.slide_width, prs.slide_height)
    shape.fill.solid(); shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    shape.zorder = 0

def box(slide, text, l, t, w, h, fontsize=18, bold=False, color=WHITE,
        bg_color=None, align=PP_ALIGN.LEFT, italic=False):
    txb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    if bg_color:
        txb.fill.solid(); txb.fill.fore_color.rgb = bg_color
    tf = txb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.alignment = align
    run = p.add_run(); run.text = text
    run.font.size = Pt(fontsize); run.font.bold = bold
    run.font.color.rgb = color; run.font.italic = italic
    return txb

def hline(slide, t, color=ACCENT):
    from pptx.util import Pt as UPt
    line = slide.shapes.add_shape(1, Inches(0.5), Inches(t), Inches(12.33), Inches(0.03))
    line.fill.solid(); line.fill.fore_color.rgb = color
    line.line.fill.background()

def bullet_box(slide, items, l, t, w, h, fontsize=16, color=WHITE, indent=False):
    txb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = txb.text_frame; tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        run = p.add_run()
        prefix = "    ◦ " if indent else "• "
        run.text = prefix + item
        run.font.size = Pt(fontsize); run.font.color.rgb = color

def title_box(slide, title, subtitle=None):
    box(slide, title, 0.5, 0.25, 12.33, 0.9, fontsize=36, bold=True, color=ACCENT, align=PP_ALIGN.LEFT)
    if subtitle:
        box(slide, subtitle, 0.5, 1.1, 12.33, 0.5, fontsize=18, color=LIGHT_GRAY, align=PP_ALIGN.LEFT, italic=True)
    hline(slide, 1.65)

def colored_rect(slide, l, t, w, h, color):
    shape = slide.shapes.add_shape(1, Inches(l), Inches(t), Inches(w), Inches(h))
    shape.fill.solid(); shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    return shape

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 1 – Title
# ════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout); bg(s)
colored_rect(s, 0, 2.8, 13.33, 1.9, RGBColor(0x31, 0x31, 0x4E))
box(s, "Constrained LVAE for Thermoelastic2D", 0.7, 0.5, 12, 1.1,
    fontsize=40, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)
box(s, "NMSE Threshold Sweep — Theory, Experiments & Next Steps",
    0.7, 1.6, 12, 0.7, fontsize=22, color=WHITE, align=PP_ALIGN.CENTER)
hline(s, 2.55)
box(s, "Thomas Casartelli  ·  EngiOpt Project  ·  April 2026",
    0.7, 2.85, 12, 0.6, fontsize=17, color=LIGHT_GRAY, align=PP_ALIGN.CENTER)
box(s, "Thermoelastic2D  |  64×64 designs  |  RTX 4090",
    0.7, 3.45, 12, 0.5, fontsize=15, color=LIGHT_GRAY, align=PP_ALIGN.CENTER, italic=True)

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 2 – What is LVAE?
# ════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout); bg(s)
title_box(s, "What is LVAE?", "Least-Volume Autoencoder with Dynamic Pruning")

box(s, "Core Idea", 0.5, 1.8, 5.8, 0.45, fontsize=18, bold=True, color=ACCENT)
bullet_box(s, [
    "Autoencoder that compresses designs into a latent space",
    "Simultaneously minimises latent dimensionality (volume loss)",
    "Encoder maps design → z  |  Decoder maps z → design",
    "Dimensions that carry no information are pruned away",
], 0.5, 2.25, 5.8, 2.8, fontsize=15)

box(s, "Loss Function", 6.8, 1.8, 5.8, 0.45, fontsize=18, bold=True, color=ACCENT2)
box(s, "L  =  L_rec  +  λ · L_vol", 6.8, 2.25, 5.8, 0.55,
    fontsize=20, bold=True, color=YELLOW, align=PP_ALIGN.CENTER,
    bg_color=RGBColor(0x31, 0x31, 0x4E))
bullet_box(s, [
    "L_rec  =  reconstruction quality (MSE)",
    "L_vol  =  sum of latent std deviations (volume)",
    "λ  =  weight balancing the two objectives",
    "Dynamic Pruning: dimensions with std → 0 are removed",
], 6.8, 2.85, 5.8, 2.4, fontsize=15)

hline(s, 6.1, LIGHT_GRAY)
box(s, "Goal: find the smallest latent space that still reconstructs designs accurately",
    0.5, 6.15, 12.33, 0.5, fontsize=15, color=YELLOW, italic=True, align=PP_ALIGN.CENTER)

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 3 – Constrained LVAE
# ════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout); bg(s)
title_box(s, "Constrained LVAE", "Replacing the fixed λ with an adaptive NMSE constraint")

box(s, "The Problem with Fixed λ", 0.5, 1.8, 5.8, 0.45, fontsize=18, bold=True, color=ACCENT3)
bullet_box(s, [
    "Hard to tune λ manually",
    "No guarantee on reconstruction quality",
    "λ too high → over-compressed, poor reconstruction",
    "λ too low → no compression, wasted dimensions",
], 0.5, 2.25, 5.8, 2.4, fontsize=15)

box(s, "The Constrained Approach", 6.8, 1.8, 5.8, 0.45, fontsize=18, bold=True, color=ACCENT2)
bullet_box(s, [
    "Set an explicit reconstruction quality target: NMSE ≤ τ",
    "Volume loss activates ONLY when constraint is satisfied",
    "Model compresses as much as possible while staying",
    "within the quality budget τ",
], 6.8, 2.25, 5.8, 2.0, fontsize=15)

box(s, "One-Sided Mode (used here)", 6.8, 4.3, 5.8, 0.4, fontsize=16, bold=True, color=YELLOW)
bullet_box(s, [
    "If NMSE > τ  →  vol_active = OFF  →  focus on reconstruction",
    "If NMSE ≤ τ  →  vol_active = ON   →  start compressing",
], 6.8, 4.7, 5.8, 1.0, fontsize=14, color=YELLOW)

colored_rect(s, 0.5, 4.2, 5.8, 1.6, RGBColor(0x2A, 0x2A, 0x45))
box(s, "NMSE  =  MSE / Var(data)", 0.7, 4.35, 5.4, 0.5,
    fontsize=20, bold=True, color=YELLOW, align=PP_ALIGN.CENTER)
box(s, "Normalised MSE — scale-free measure of reconstruction quality.\n"
       "NMSE = 0 → perfect  |  NMSE = 1 → predicting the mean",
    0.7, 4.85, 5.4, 0.85, fontsize=13, color=LIGHT_GRAY, align=PP_ALIGN.CENTER)

hline(s, 6.1, LIGHT_GRAY)
box(s, "τ  (nmse_threshold) is the key hyperparameter — it defines the quality budget",
    0.5, 6.15, 12.33, 0.5, fontsize=15, color=ACCENT, italic=True, align=PP_ALIGN.CENTER)

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 4 – The NMSE Threshold Role
# ════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout); bg(s)
title_box(s, "Role of the NMSE Threshold τ", "The dial between reconstruction quality and compression")

# three columns
for col, (xl, label, body, col_color) in enumerate([
    (0.4, "τ too low", [
        "Model cannot achieve τ on training data",
        "vol_active never turns ON",
        "No compression pressure applied",
        "All latent dims remain active",
        "Model memorises training set → overfits",
        "val_NMSE stays high",
    ], ACCENT3),
    (4.7, "τ sweet spot", [
        "τ is achievable on training data",
        "vol_active turns ON regularly",
        "Compression pressure applied",
        "Unnecessary dims pruned away",
        "Compression acts as regulariser",
        "Best val_NMSE achieved",
    ], ACCENT2),
    (9.0, "τ too high", [
        "τ is trivially satisfied immediately",
        "Very strong volume pressure",
        "Aggressive over-compression",
        "Important dims may be pruned",
        "Reconstruction quality degrades",
        "val_NMSE worsens again",
    ], YELLOW),
]):
    colored_rect(s, xl, 1.75, 3.7, 0.5, col_color)
    box(s, label, xl + 0.1, 1.78, 3.5, 0.45, fontsize=18, bold=True, color=DARK_BG, align=PP_ALIGN.CENTER)
    colored_rect(s, xl, 2.25, 3.7, 3.8, RGBColor(0x2A, 0x2A, 0x45))
    bullet_box(s, body, xl + 0.15, 2.3, 3.4, 3.7, fontsize=13, color=WHITE)

hline(s, 6.25, LIGHT_GRAY)
box(s, "Finding τ* is the goal of this sweep — the point where compression maximally helps generalisation",
    0.5, 6.3, 12.33, 0.5, fontsize=15, color=YELLOW, italic=True, align=PP_ALIGN.CENTER)

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 5 – Experiment Setup
# ════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout); bg(s)
title_box(s, "Experiment Setup", "W&B Grid Sweep over nmse_threshold")

box(s, "Research Question", 0.5, 1.8, 12.33, 0.4, fontsize=18, bold=True, color=ACCENT)
box(s, '"When does volume pressure over-compress on the training data, leading to significantly poorer validation reconstruction?"',
    0.5, 2.2, 12.33, 0.65, fontsize=16, color=YELLOW, italic=True)

hline(s, 2.95, LIGHT_GRAY)

box(s, "Fixed hyperparameters", 0.5, 3.1, 5.8, 0.4, fontsize=16, bold=True, color=ACCENT2)
bullet_box(s, [
    "Problem: thermoelastic2d  (64×64 designs)",
    "Latent dim: 100  |  Batch size: 128",
    "Learning rate: 1e-4  |  Seed: 1",
    "Pruning epoch: 500  |  Pruning strategy: plummet",
    "Pruning threshold: 0.05  |  Constraint mode: one_sided",
    "Early stopping start: epoch 1000  |  Patience: 50",
], 0.5, 3.5, 5.8, 2.8, fontsize=14)

box(s, "Swept parameter", 6.8, 3.1, 5.8, 0.4, fontsize=16, bold=True, color=ACCENT2)
colored_rect(s, 6.8, 3.5, 5.8, 0.6, RGBColor(0x31, 0x31, 0x4E))
box(s, "nmse_threshold  ∈  { 0.01, 0.03, 0.05, 0.10, 0.20 }",
    6.9, 3.55, 5.6, 0.5, fontsize=16, bold=True, color=YELLOW, align=PP_ALIGN.CENTER)
bullet_box(s, [
    "5 jobs submitted via SLURM on RTX 4090",
    "Each job runs 1 sweep agent (W&B grid search)",
    "Max epochs: 10,000  |  ~18 epochs/minute",
    "Early stopping monitors val_nmse after epoch 1000",
], 6.8, 4.15, 5.8, 2.2, fontsize=14)

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 6 – Results Table
# ════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout); bg(s)
title_box(s, "Sweep Results — Both Sweeps Combined", "8 values of nmse_threshold · τ ∈ {0.01 … 0.70}")

headers = ["τ", "Train NMSE", "Val NMSE", "Active dims", "vol_active", "Regime"]
rows = [
    ["0.01", "0.035", "0.211", "100/100", "✗", "Unreachable"],
    ["0.03", "0.035", "0.211", "100/100", "✗", "Unreachable"],
    ["0.05", "0.067", "0.198", "100/100", "✗", "Borderline"],
    ["0.10", "0.077", "0.191", "100/100", "✓", "Compression"],
    ["0.20", "0.088", "0.182",  "97/100", "✓", "★ SWEET SPOT"],
    ["0.30", "0.117", "0.239",  "43/100", "✓", "Over-compress"],
    ["0.50", "0.126", "0.251",  "45/100", "✓", "Over-compress"],
    ["0.70", "0.131", "0.317",  "14/100", "✓", "Over-compress"],
]
# color per row: 0=red,1=red,2=yellow,3=green,4=BEST green,5=orange,6=orange,7=orange
row_colors = [
    (RGBColor(0x3A,0x28,0x28), ACCENT3),
    (RGBColor(0x3A,0x28,0x28), ACCENT3),
    (RGBColor(0x3A,0x38,0x28), YELLOW),
    (RGBColor(0x28,0x38,0x28), ACCENT2),
    (RGBColor(0x1A,0x40,0x1A), ACCENT2),
    (RGBColor(0x3A,0x30,0x20), YELLOW),
    (RGBColor(0x3A,0x30,0x20), YELLOW),
    (RGBColor(0x3A,0x28,0x28), ACCENT3),
]

col_w = [0.9, 1.5, 1.5, 1.5, 1.4, 2.2]
col_x = [0.35]
for w in col_w[:-1]: col_x.append(col_x[-1] + w)

for j, (h, x, w) in enumerate(zip(headers, col_x, col_w)):
    colored_rect(s, x, 1.75, w - 0.05, 0.38, ACCENT)
    box(s, h, x + 0.05, 1.77, w - 0.1, 0.34, fontsize=12, bold=True,
        color=DARK_BG, align=PP_ALIGN.CENTER)

for i, (row, (rbg, rc)) in enumerate(zip(rows, row_colors)):
    row_y = 2.13 + i * 0.58
    for j, (cell, x, w) in enumerate(zip(row, col_x, col_w)):
        colored_rect(s, x, row_y, w - 0.05, 0.52, rbg)
        fc = rc if j in [2, 5] else WHITE
        bold = (i == 4)
        box(s, cell, x + 0.05, row_y + 0.03, w - 0.1, 0.46,
            fontsize=12, color=fc, align=PP_ALIGN.CENTER, bold=bold)

hline(s, 6.9, LIGHT_GRAY)
box(s, "★ τ = 0.20 is the sweet spot  |  τ ≥ 0.30 causes over-compression — val_NMSE worsens despite more pruning",
    0.35, 6.95, 12.33, 0.4, fontsize=13, color=YELLOW, italic=True, align=PP_ALIGN.CENTER)

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 7 – Key Findings
# ════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout); bg(s)
title_box(s, "Key Findings", "Four regimes identified across both sweeps")

for xi, (label, items, c) in enumerate([
    ("Regime 1  —  τ ≤ 0.03\n(Threshold unreachable)", [
        "Train NMSE floor ≈ 0.035 > τ",
        "vol_active = OFF at all times",
        "No compression pressure",
        "Model memorises training → overfits",
        "val_NMSE ≈ 0.211  (worst)",
    ], ACCENT3),
    ("Regime 2  —  τ = 0.05\n(Borderline)", [
        "Train NMSE barely above τ",
        "vol_active oscillates near threshold",
        "Slight implicit regularisation",
        "val_NMSE = 0.198  (slightly better)",
        "Transition point",
    ], YELLOW),
    ("Regime 3  —  τ = 0.10–0.20\n(★ Sweet Spot)", [
        "vol_active = ON consistently",
        "Compression acts as regulariser",
        "Train NMSE rises — quality traded off",
        "val_NMSE = 0.191 → 0.182  (BEST)",
        "τ=0.20: optimal balance found",
    ], ACCENT2),
    ("Regime 4  —  τ ≥ 0.30\n(Over-compression)", [
        "Very strong volume pressure",
        "Aggressive pruning: 43→14 active dims",
        "Important dims may be removed",
        "val_NMSE = 0.239 → 0.317  (worsens!)",
        "τ > 0.20 not meaningful for this task",
    ], ACCENT3),
]):
    xl = 0.25 + xi * 3.25
    colored_rect(s, xl, 1.75, 3.1, 0.6, c)
    box(s, label, xl + 0.07, 1.78, 2.96, 0.55, fontsize=12, bold=True,
        color=DARK_BG, align=PP_ALIGN.CENTER)
    colored_rect(s, xl, 2.35, 3.1, 3.7, RGBColor(0x26, 0x26, 0x40))
    bullet_box(s, items, xl + 0.1, 2.4, 2.9, 3.6, fontsize=12)

hline(s, 6.2, LIGHT_GRAY)
box(s, "Answer to research question: τ* = 0.20 is the sweet spot — above it, over-compression degrades val_NMSE significantly",
    0.35, 6.25, 12.33, 0.4, fontsize=14, bold=True, color=YELLOW, italic=True, align=PP_ALIGN.CENTER)

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 8 – The Train/Val Gap Problem
# ════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout); bg(s)
title_box(s, "The Train / Val NMSE Gap", "A fundamental generalisation problem")

colored_rect(s, 0.5, 1.8, 12.33, 0.65, RGBColor(0x3A, 0x28, 0x28))
box(s, "Best result:  Train NMSE = 0.088   →   Val NMSE = 0.182   (2× gap)",
    0.6, 1.85, 12.1, 0.55, fontsize=18, bold=True, color=ACCENT3, align=PP_ALIGN.CENTER)

box(s, "Why does this gap exist?", 0.5, 2.6, 5.8, 0.4, fontsize=17, bold=True, color=ACCENT)
bullet_box(s, [
    "The latent space (100 dims) is still very large relative to training data",
    "With 100 active dims and no pruning, the encoder can memorise training",
    "Validation designs may have different condition distributions",
    "The natural reconstruction floor (NMSE≈0.035) is achieved by overfitting",
], 0.5, 3.05, 5.8, 2.8, fontsize=14)

box(s, "Why compression helps (τ≥0.10)", 7.0, 2.6, 5.5, 0.4, fontsize=17, bold=True, color=ACCENT2)
bullet_box(s, [
    "Volume loss forces the encoder into a bottleneck",
    "Bottleneck prevents memorisation → forces generalisation",
    "Fewer active dims = simpler representation = less overfitting",
    "But even τ=0.20 only pruned 3 dims — not enough compression yet",
], 7.0, 3.05, 5.5, 2.8, fontsize=14)

hline(s, 6.05, LIGHT_GRAY)
box(s, "The gap is NOT caused by the threshold choice — it reflects the model's capacity vs dataset size",
    0.5, 6.1, 12.33, 0.5, fontsize=14, color=YELLOW, italic=True, align=PP_ALIGN.CENTER)

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 9 – Why Pruning Didn't Happen Much
# ════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout); bg(s)
title_box(s, "Why Is Pruning So Minimal?", "97–100 active dims — almost nothing pruned")

box(s, "How Plummet Pruning Works", 0.5, 1.8, 5.8, 0.4, fontsize=17, bold=True, color=ACCENT)
bullet_box(s, [
    "Sort latent dimensions by their std (descending)",
    "Look for a sudden 'plummet' — a sharp drop in std",
    "Dimensions beyond the plummet are pruned",
    "Works well when: a few dims have high std, many have near-zero std",
], 0.5, 2.2, 5.8, 2.4, fontsize=14)

box(s, "What We Observed", 0.5, 4.7, 5.8, 0.4, fontsize=17, bold=True, color=ACCENT3)
bullet_box(s, [
    "Latent std distribution is very FLAT (0.015–0.07 across all 100 dims)",
    "No clear 'elbow' or 'plummet' — dims look equally important",
    "Plummet strategy finds nothing to prune",
    "Only 3 dims removed at τ=0.20 (and only after 1000+ epochs)",
], 0.5, 5.1, 5.8, 2.0, fontsize=14, color=ACCENT3)

box(s, "Possible Explanations", 7.0, 1.8, 5.8, 0.4, fontsize=17, bold=True, color=ACCENT2)
bullet_box(s, [
    "Training still too short — std needs more epochs to separate",
    "The thermoelastic2d dataset genuinely needs many latent dims",
    "Volume pressure (τ=0.20) is not strong enough yet",
    "Pruning threshold (0.05) too conservative — misses small drops",
    "Network architecture may be underconstrained",
], 7.0, 2.2, 5.8, 3.0, fontsize=14)

hline(s, 6.05, LIGHT_GRAY)
box(s, "Key insight: plummet pruning requires a structured latent space — more training or stronger compression pressure needed",
    0.5, 6.1, 12.33, 0.5, fontsize=13, color=YELLOW, italic=True, align=PP_ALIGN.CENTER)

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 10 – Next Steps
# ════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout); bg(s)
title_box(s, "Next Steps", "What to do based on these results")

steps = [
    ("1", "Fix τ = 0.20 and study reproducibility", ACCENT,
     ["Run multiple seeds (1, 2, 3) to confirm τ*=0.20 is robust",
      "Check if val_NMSE=0.182 is stable across seeds",
      "Variance across seeds informs confidence in the result"]),
    ("2", "Investigate the train/val gap", ACCENT2,
     ["Best result: train NMSE=0.088 vs val NMSE=0.182 (2× gap)",
      "Check if validation set has different condition distribution",
      "Consider conditioning on problem parameters (weight, BC)"]),
    ("3", "Explore τ in [0.15, 0.25] finely", ACCENT3,
     ["τ* may be between 0.10 and 0.20 — current grid is coarse",
      "Test τ ∈ {0.12, 0.15, 0.18, 0.20, 0.22, 0.25}",
      "Goal: find the exact inflection point more precisely"]),
    ("4", "Compare with other model variants", YELLOW,
     ["Run same sweep on plvae, sn_enc, val_pruning variants",
      "Does τ* = 0.20 hold across architectures?",
      "Use τ=0.20 as default for all future experiments"]),
]

for i, (num, title, color, items) in enumerate(steps):
    xi = (i % 2) * 6.5 + 0.35
    yi = (i // 2) * 2.5 + 1.8
    colored_rect(s, xi, yi, 0.55, 0.55, color)
    box(s, num, xi, yi, 0.55, 0.55, fontsize=22, bold=True, color=DARK_BG, align=PP_ALIGN.CENTER)
    box(s, title, xi + 0.65, yi + 0.05, 5.5, 0.45, fontsize=16, bold=True, color=color)
    bullet_box(s, items, xi + 0.65, yi + 0.5, 5.5, 1.7, fontsize=13)

hline(s, 6.95, LIGHT_GRAY)

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 11 – Summary
# ════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout); bg(s)
title_box(s, "Summary", "Constrained LVAE — NMSE Threshold Sweep")

colored_rect(s, 0.5, 1.8, 12.33, 4.5, RGBColor(0x22, 0x22, 0x38))

takeaways = [
    ("Theory",    "Constrained LVAE uses τ to define a quality budget — compression activates only when reconstruction is good enough", ACCENT),
    ("Finding 1", "τ ≤ 0.03 unreachable — reconstruction floor ≈ 0.035 — no volume pressure, severe overfitting, val_NMSE ≈ 0.211", ACCENT3),
    ("Finding 2", "τ = 0.10–0.20: volume pressure activates, compression regularises, best val_NMSE = 0.182 at τ = 0.20", ACCENT2),
    ("Finding 3", "τ ≥ 0.30: over-compression — pruning too aggressive (43→14 dims), val_NMSE worsens to 0.239–0.317", ACCENT3),
    ("Finding 4", "★  τ* = 0.20 is the sweet spot — balanced compression, best generalisation, 97/100 dims active", YELLOW),
    ("Next",      "Investigate the persistent 2× train/val gap and study whether τ* shifts with more training data or seeds", ACCENT2),
]

for i, (label, text, color) in enumerate(takeaways):
    y = 1.9 + i * 0.68
    colored_rect(s, 0.6, y + 0.02, 1.4, 0.5, color)
    box(s, label, 0.65, y + 0.04, 1.3, 0.45, fontsize=13, bold=True,
        color=DARK_BG, align=PP_ALIGN.CENTER)
    box(s, text, 2.15, y + 0.04, 10.4, 0.5, fontsize=13, color=WHITE)

hline(s, 6.55, ACCENT)
box(s, "τ* = 0.20 confirmed across both sweeps — the sweet spot between under- and over-compression for thermoelastic2d",
    0.5, 6.6, 12.33, 0.5, fontsize=15, bold=True, color=YELLOW, align=PP_ALIGN.CENTER)

# ── save ────────────────────────────────────────────────────────────────────
out = "/cluster/home/tcasartelli/projects/EngiOpt/engiopt/vanilla_thomas_thermo2D/nmse_threshold_sweep_presentation.pptx"
prs.save(out)
print(f"Saved → {out}")
