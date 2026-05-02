"""Generate thermoelastic2d_lvae_analysis.pdf — viewable in VS Code."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

PDF_PATH = "/cluster/home/tcasartelli/projects/EngiOpt/engiopt/vanilla_thomas_thermo2D/thermoelastic2d_lvae_analysis.pdf"

# ── palette ─────────────────────────────────────────────────────────────────
C_BLUE   = "#1F6FEB"
C_LBLUE  = "#D6E8FF"
C_GREEN  = "#0A7D57"
C_ORANGE = "#E87D14"
C_RED    = "#C0392B"
C_GREY   = "#F2F4F7"
C_DKGREY = "#55657A"
C_BLACK  = "#1A1A2E"
C_WHITE  = "#FFFFFF"

W, H = 16, 9   # inches (widescreen)

def new_fig():
    fig, ax = plt.subplots(figsize=(W, H))
    ax.set_xlim(0, W); ax.set_ylim(0, H)
    ax.axis("off")
    fig.patch.set_facecolor(C_WHITE)
    return fig, ax

def header(ax, title, subtitle=""):
    ax.add_patch(plt.Rectangle((0, H - 1.3), W, 1.3,
                                color=C_BLUE, zorder=2))
    ax.text(0.35, H - 0.55, title,
            fontsize=22, fontweight="bold", color="white",
            va="center", zorder=3)
    if subtitle:
        ax.text(0.35, H - 1.05, subtitle,
                fontsize=12, color="#CCDDFF", va="center", zorder=3)

def card(ax, x, y, w, h, color=C_GREY, fill=None, edge=C_BLUE, lw=1.5, zorder=1):
    facecolor = fill if fill is not None else color
    ax.add_patch(FancyBboxPatch((x, y), w, h,
        boxstyle="round,pad=0.05", facecolor=facecolor,
        edgecolor=edge, linewidth=lw, zorder=zorder))

def txt(ax, s, x, y, size=12, color=C_BLACK, bold=False, italic=False,
        ha="left", va="top", wrap=True, zorder=4, alpha=1.0):
    weight = "bold" if bold else "normal"
    style  = "italic" if italic else "normal"
    ax.text(x, y, s, fontsize=size, color=color,
            fontweight=weight, fontstyle=style,
            ha=ha, va=va, zorder=zorder, alpha=alpha,
            wrap=wrap)

def badge(ax, x, y, w, h, label, color, textcol="white", size=11):
    ax.add_patch(plt.Rectangle((x, y), w, h, color=color, zorder=5))
    ax.text(x + w/2, y + h/2, label,
            fontsize=size, color=textcol, fontweight="bold",
            ha="center", va="center", zorder=6)

def bullet_lines(ax, items, x, y_start, col_width=6.5, line_h=0.38, size=11):
    y = y_start
    for item in items:
        if isinstance(item, tuple):
            pre, text, sz, bold, col = item
        else:
            pre, text, sz, bold, col = "•  ", item, size, False, C_BLACK
        if not text:
            y -= line_h * 0.5
            continue
        ax.text(x, y, pre + text, fontsize=sz, color=col,
                fontweight="bold" if bold else "normal",
                ha="left", va="top", zorder=4,
                wrap=True)
        # rough line count
        chars_per_line = int(col_width / (sz * 0.011))
        n_lines = max(1, len(pre + text) // chars_per_line + 1)
        y -= line_h * n_lines
    return y


# ════════════════════════════════════════════════════════════════════════════
# Page 1 — Title
# ════════════════════════════════════════════════════════════════════════════
with PdfPages(PDF_PATH) as pdf:

    fig, ax = new_fig()
    ax.add_patch(plt.Rectangle((0, 0), W, H, color=C_WHITE))
    ax.add_patch(plt.Rectangle((0, 0), W, 0.7, color=C_BLUE))
    ax.add_patch(plt.Rectangle((0, H - 0.5), W, 0.5, color=C_BLUE))
    txt(ax, "Vanilla LVAE on Thermoelastic 2D",
        W/2, H/2 + 1.5, size=28, bold=True, color=C_BLACK, ha="center", va="center")
    txt(ax, "Ablation study:  Baseline BN  →  GN encoder  →  GN + Latent Noise",
        W/2, H/2 + 0.5, size=16, color=C_DKGREY, ha="center", va="center")
    txt(ax, "What changed, why it matters, and what the numbers say",
        W/2, H/2 - 0.1, size=13, color=C_DKGREY, italic=True, ha="center", va="center")
    txt(ax, "EngiOpt  ·  ETH Zürich  ·  April 2026",
        W/2, 0.35, size=12, color=C_WHITE, ha="center", va="center")
    ax.axhline(H/2 + 1.85, xmin=0.15, xmax=0.85, color=C_BLUE, lw=2)
    pdf.savefig(fig, bbox_inches="tight"); plt.close()


    # ════════════════════════════════════════════════════════════════════════
    # Page 2 — Comparison Table
    # ════════════════════════════════════════════════════════════════════════
    fig, ax = new_fig()
    header(ax, "Three Runs at a Glance",
           "Vanilla LVAE  ·  thermoelastic2D  ·  seed 1  ·  latent_dim = 100")

    col_x = [0.3, 3.6, 7.1, 11.0]
    col_w = [3.2, 3.3, 3.7, 4.5]
    headers = ["Metric", "Baseline BN\n(ep 9 999)", "GN encoder\n(ep 57  ⚠)", "GN + Noise  σ=0.1\n(ep 1 033, running)"]
    rows = [
        ("Encoder",          "BatchNorm",          "GroupNorm + SN",   "GroupNorm + SN"),
        ("Latent noise σ",   "—",                  "—",                "0.1"),
        ("Early stopping",   "patience 10 / ep 0", "patience 10 / ep 0","patience 50 / ep 2000"),
        ("Train rec",        "0.000410",            "0.02939",          "0.008553"),
        ("Val rec",          "0.03309",             "0.03246",          "0.03121  ✓"),
        ("Gap  (val/train)", "80×  ✗",              "1.10×  ⚠*",        "3.65×"),
        ("Active dims",      "65 / 100",            "100 / 100",        "69 / 100"),
        ("Vol active?",      "Yes (late)",          "No",               "Yes"),
        ("Status",           "Done",                "Stopped early",    "Running"),
    ]

    # header row
    row_h   = 0.52
    tbl_top = H - 1.5
    hdr_y   = tbl_top - row_h

    for ci, (cx, cw, hdr) in enumerate(zip(col_x, col_w, headers)):
        ax.add_patch(plt.Rectangle((cx, hdr_y), cw - 0.05, row_h,
                                    color=C_BLUE))
        ax.text(cx + (cw - 0.05)/2, hdr_y + row_h/2, hdr,
                fontsize=10, color="white", fontweight="bold",
                ha="center", va="center", multialignment="center")

    val_colors = {
        ("Val rec",          2): C_GREEN,
        ("Gap  (val/train)", 0): C_RED,
        ("Gap  (val/train)", 1): C_ORANGE,
        ("Status",           0): C_GREEN,
        ("Status",           1): C_RED,
        ("Status",           2): C_ORANGE,
    }
    for ri, row in enumerate(rows):
        ry = hdr_y - (ri + 1) * row_h
        fill = C_GREY if ri % 2 == 0 else C_WHITE
        for ci, (cx, cw) in enumerate(zip(col_x, col_w)):
            ax.add_patch(plt.Rectangle((cx, ry), cw - 0.05, row_h,
                                        facecolor=fill, edgecolor="#DDDDDD", lw=0.5))
            val = row[0] if ci == 0 else row[ci]
            col = val_colors.get((row[0], ci - 1), C_BLACK)
            ha  = "left" if ci == 0 else "center"
            xpos = cx + 0.1 if ci == 0 else cx + (cw - 0.05)/2
            ax.text(xpos, ry + row_h/2, val, fontsize=10, color=col,
                    ha=ha, va="center",
                    fontweight="bold" if ci > 0 and (row[0] in ["Val rec","Gap  (val/train)","Status"]) else "normal")

    txt(ax, "* GN gap 1.10× is misleading — both train and val high because model hadn't converged at ep 57.",
        0.3, 0.25, size=10, color=C_DKGREY, italic=True)
    pdf.savefig(fig, bbox_inches="tight"); plt.close()


    # ════════════════════════════════════════════════════════════════════════
    # Page 3 — Baseline deep dive
    # ════════════════════════════════════════════════════════════════════════
    fig, ax = new_fig()
    header(ax, "Run 1 — Baseline: BatchNorm Encoder",
           "Full training (10 000 epochs)  ·  the overfitting benchmark")

    card(ax, 0.3, 0.3, 7.5, 7.0)
    txt(ax, "What happened", 0.55, H - 1.55, size=14, bold=True, color=C_BLUE)
    bullet_lines(ax, [
        "The model trained to completion (epoch 9 999) and memorised the training set.",
        "Train rec collapsed to 0.000410 — essentially zero error on training samples.",
        "Val rec stayed at 0.03309. The encoder learned to compress training samples perfectly but generalised only weakly.",
        ("✗  ", "Gap of 80× — extreme overfitting. Encoder memorised, not generalised.", 11, True, C_RED),
        "Volume did activate (65/100 active dims) — but only because train rec was far below threshold, not because the model truly converged.",
        ("→  ", "BatchNorm running stats cause a small eval-time distribution shift, but the dominant effect is capacity-driven memorisation.", 11, False, C_DKGREY),
    ], 0.55, H - 1.95, col_width=7.0, size=11)

    card(ax, 8.1, 0.3, 7.5, 7.0)
    txt(ax, "Key numbers", 8.35, H - 1.55, size=14, bold=True, color=C_BLUE)
    metrics = [
        ("Train rec",    "0.000410", C_RED,    "Memorised training data"),
        ("Val rec",      "0.03309",  C_BLACK,  "Generalisation limited"),
        ("Gap",          "80×",      C_RED,    "Catastrophic overfitting"),
        ("Active dims",  "65 / 100", C_BLACK,  "35 dims pruned by vol"),
        ("Vol active",   "Yes",      C_GREEN,  "Activated late in training"),
        ("Epoch",        "9 999",    C_BLACK,  "Fully trained"),
    ]
    y0 = H - 2.0
    for label, val, vcol, note in metrics:
        ax.add_patch(plt.Rectangle((8.3, y0 - 0.75), 7.2, 0.75,
                                    facecolor=C_GREY, edgecolor="#DDDDDD", lw=0.5))
        ax.text(8.45, y0 - 0.2, label, fontsize=11, color=C_DKGREY, va="center")
        ax.text(12.5, y0 - 0.2, val,   fontsize=13, color=vcol,
                fontweight="bold", ha="center", va="center")
        ax.text(8.45, y0 - 0.55, note, fontsize=10, color=C_DKGREY,
                style="italic", va="center")
        y0 -= 0.82
    pdf.savefig(fig, bbox_inches="tight"); plt.close()


    # ════════════════════════════════════════════════════════════════════════
    # Page 4 — GN encoder (stopped early)
    # ════════════════════════════════════════════════════════════════════════
    fig, ax = new_fig()
    header(ax, "Run 2 — GN + SN Encoder (no noise)",
           "Stopped at epoch 57  ·  aggressive early stopping prevented convergence")

    card(ax, 0.3, 0.3, 7.5, 7.0)
    txt(ax, "What happened", 0.55, H - 1.55, size=14, bold=True, color=C_BLUE)
    bullet_lines(ax, [
        ("⚠  ", "patience=10 from epoch 0: most aggressive early stopping possible.", 12, True, C_ORANGE),
        "At epoch 57, both train rec (0.029) and val rec (0.032) are still high — model had not entered the low-loss regime.",
        "Early stopping triggered because val rec did not improve for 10 epochs in the very early, noisy phase of training.",
        ("⚠  ", "Gap of 1.10× is NOT a sign of good generalisation — both sets failed equally (underfitting).", 11, True, C_ORANGE),
        "Volume never activated (pruning epoch=500 not yet reached). Active dims = 100/100.",
        ("✗  ", "This run is not usable as an ablation. A proper GN-only run needs patience≥50 from epoch≥2000.", 12, True, C_RED),
    ], 0.55, H - 1.95, col_width=7.0, size=11)

    card(ax, 8.1, 0.3, 7.5, 7.0)
    txt(ax, "Key numbers", 8.35, H - 1.55, size=14, bold=True, color=C_BLUE)
    metrics = [
        ("Train rec",    "0.02939",  C_ORANGE, "Model not converged"),
        ("Val rec",      "0.03246",  C_ORANGE, "Both high — underfitting"),
        ("Gap",          "1.10×",    C_ORANGE, "Misleading: both losses high"),
        ("Active dims",  "100 / 100",C_BLACK,  "Pruning epoch not reached"),
        ("Vol active",   "No",       C_BLACK,  ""),
        ("Epoch",        "57",       C_RED,    "Stopped far too early"),
    ]
    y0 = H - 2.0
    for label, val, vcol, note in metrics:
        ax.add_patch(plt.Rectangle((8.3, y0 - 0.75), 7.2, 0.75,
                                    facecolor=C_GREY, edgecolor="#DDDDDD", lw=0.5))
        ax.text(8.45, y0 - 0.2, label, fontsize=11, color=C_DKGREY, va="center")
        ax.text(12.5, y0 - 0.2, val,   fontsize=13, color=vcol,
                fontweight="bold", ha="center", va="center")
        ax.text(8.45, y0 - 0.55, note, fontsize=10, color=C_DKGREY,
                style="italic", va="center")
        y0 -= 0.82

    # action box
    ax.add_patch(plt.Rectangle((8.3, 0.35), 7.2, 0.8,
                                facecolor="#FFF0F0", edgecolor=C_RED, lw=2))
    ax.text(11.9, 0.75, "ACTION: Re-run with patience=50, start_epoch=2000,\nlatent_noise_sigma=0.0 to get a fair ablation.",
            fontsize=11, color=C_RED, fontweight="bold", ha="center", va="center",
            multialignment="center")
    pdf.savefig(fig, bbox_inches="tight"); plt.close()


    # ════════════════════════════════════════════════════════════════════════
    # Page 5 — GN + Latent Noise
    # ════════════════════════════════════════════════════════════════════════
    fig, ax = new_fig()
    header(ax, "Run 3 — GN + SN Encoder + Latent Noise  (σ = 0.1)",
           "Epoch 1033 / 10 000  ·  still running  ·  early stopping from epoch 2000")

    card(ax, 0.3, 0.3, 7.5, 7.0)
    txt(ax, "What's happening so far", 0.55, H - 1.55, size=14, bold=True, color=C_BLUE)
    bullet_lines(ax, [
        ("✓  ", "Train rec = 0.008553. Learning well, but regularised — noise prevents near-zero memorisation.", 12, True, C_GREEN),
        ("✓  ", "Val rec = 0.03121 — already BETTER than the fully-trained baseline (0.03309).", 12, True, C_GREEN),
        "Gap = 3.65×. Still large, but massively better than baseline's 80×. Noise forces the decoder to handle imprecise codes.",
        ("✓  ", "Active dims = 69/100. Volume activated and 31 dims already pruned — at epoch 1033 vs baseline's 65 dims at epoch 9999.", 12, True, C_GREEN),
        "Early stopping not active yet (starts epoch 2000). ~7000 more epochs. Expect further pruning and convergence.",
        ("→  ", "Risk: if gap stays at 3.65× till ep 2000, encoder still overfits and we need stronger regularisation.", 11, False, C_ORANGE),
    ], 0.55, H - 1.95, col_width=7.0, size=11)

    card(ax, 8.1, 0.3, 7.5, 7.0)
    txt(ax, "Key numbers", 8.35, H - 1.55, size=14, bold=True, color=C_BLUE)
    metrics = [
        ("Train rec",    "0.008553",       C_BLACK,  "Regularised by noise"),
        ("Val rec",      "0.03121  ✓",     C_GREEN,  "Better than fully-trained baseline"),
        ("Gap",          "3.65×",          C_ORANGE, "Down from 80× — noise works"),
        ("Active dims",  "69 / 100",       C_GREEN,  "31 dims pruned at ep 1033"),
        ("Vol active",   "Yes",            C_GREEN,  "Compression running"),
        ("Epoch",        "1 033 / 10 000", C_ORANGE, "Still running"),
    ]
    y0 = H - 2.0
    for label, val, vcol, note in metrics:
        ax.add_patch(plt.Rectangle((8.3, y0 - 0.75), 7.2, 0.75,
                                    facecolor=C_GREY, edgecolor="#DDDDDD", lw=0.5))
        ax.text(8.45, y0 - 0.2, label, fontsize=11, color=C_DKGREY, va="center")
        ax.text(12.5, y0 - 0.2, val,   fontsize=13, color=vcol,
                fontweight="bold", ha="center", va="center")
        ax.text(8.45, y0 - 0.55, note, fontsize=10, color=C_DKGREY,
                style="italic", va="center")
        y0 -= 0.82
    pdf.savefig(fig, bbox_inches="tight"); plt.close()


    # ════════════════════════════════════════════════════════════════════════
    # Page 6 — Why noise helps (mechanism)
    # ════════════════════════════════════════════════════════════════════════
    fig, ax = new_fig()
    header(ax, "Analysis — Why Latent Noise Helps",
           "Mechanistic explanation and interpretation of the gap reduction")

    # left: without noise
    card(ax, 0.3, 0.35, 7.5, 3.1, edge=C_RED)
    txt(ax, "Without noise (baseline BN)", 0.55, H - 1.55, size=13, bold=True, color=C_RED)
    bullet_lines(ax, [
        "The encoder maps each training sample to a precise, tight latent code.",
        "The decoder memorises the mapping: exact code → exact design.",
        "For a val sample, the encoder outputs a slightly different code (distribution shift from BN + genuine overfitting). The decoder, trained only on tight codes, produces large errors.",
        ("→  ", "Train rec → 0, val rec stays at 0.033.  Gap = 80×.", 11, True, C_RED),
    ], 0.55, H - 1.95, col_width=7.0, size=11)

    # left lower: with noise
    card(ax, 0.3, 0.2, 7.5, 3.0, edge=C_GREEN)
    txt(ax, "With noise  σ = 0.1", 0.55, 3.05, size=13, bold=True, color=C_GREEN)
    bullet_lines(ax, [
        "Gaussian noise is added to z before decoding. The decoder never sees the same code twice for the same sample.",
        "The decoder learns neighbourhood robustness: 'any code near the encoder output → reconstruct this design.'",
        "Train rec stays at ~0.009 (can't memorise noisy codes). Val rec improves because decoder handles imprecise val codes.",
        ("→  ", "Val rec = 0.031 (better than baseline 0.033).  Gap = 3.65×.", 11, True, C_GREEN),
    ], 0.55, 2.7, col_width=7.0, size=11)

    # right: design choices
    card(ax, 8.1, 0.2, 7.5, 7.15)
    txt(ax, "Design choices", 8.35, H - 1.55, size=13, bold=True, color=C_BLUE)
    bullet_lines(ax, [
        ("σ = 0.1  ", "Conservative. 10% of typical latent std. Too large → destabilises training.", 11, False, C_BLACK),
        ("Noise only on active dims  ", "Pruned dims frozen at mean — no noise added.", 11, False, C_BLACK),
        ("Clean z for volume + pruning  ", "EMA stats and vol loss use noiseless z, so compression is driven by the true distribution.", 11, False, C_BLACK),
        ("Noise off at eval  ", "Val/test always use clean encoder output → fair measurement.", 11, False, C_BLACK),
        ("Analogy  ", "Dropout in the latent space. Prevents decoder from relying on exact codes.", 11, False, C_DKGREY),
    ], 8.35, H - 1.95, col_width=7.0, size=11)
    pdf.savefig(fig, bbox_inches="tight"); plt.close()


    # ════════════════════════════════════════════════════════════════════════
    # Page 7 — Bar chart
    # ════════════════════════════════════════════════════════════════════════
    fig, ax = new_fig()
    header(ax, "Val vs Train Reconstruction Error",
           "All three runs  ·  val rec is the primary generalisation metric")

    # embed a proper matplotlib bar chart as an inset
    inset = fig.add_axes([0.06, 0.12, 0.88, 0.72])

    runs = ["Baseline BN\n(ep 9999)", "GN enc\n(ep 57  ⚠)", "GN + Noise\n(ep 1033)"]
    train_vals = [0.000410, 0.02939, 0.008553]
    val_vals   = [0.03309,  0.03246, 0.03121]

    x = np.arange(len(runs))
    bw = 0.35

    bars_t = inset.bar(x - bw/2, train_vals, bw, label="Train rec",
                       color=[C_RED, C_ORANGE, C_BLACK], edgecolor="white", linewidth=1.5)
    bars_v = inset.bar(x + bw/2, val_vals,   bw, label="Val rec",
                       color=[C_DKGREY, C_DKGREY, C_GREEN], edgecolor="white", linewidth=1.5,
                       alpha=0.85)

    for bar, v in zip(bars_t, train_vals):
        inset.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.0005,
                   f"{v:.4f}", ha="center", va="bottom", fontsize=10, fontweight="bold")
    for bar, v in zip(bars_v, val_vals):
        inset.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.0005,
                   f"{v:.4f}", ha="center", va="bottom", fontsize=10, fontweight="bold",
                   color=C_GREEN if v < 0.032 else C_BLACK)

    # gap annotations
    for i, (tv, vv) in enumerate(zip(train_vals, val_vals)):
        gap = vv / tv if tv > 0 else 0
        label = f"gap = {gap:.0f}×" if gap >= 2 else f"gap ≈ {gap:.1f}×"
        color = C_RED if gap > 10 else (C_ORANGE if gap > 2 else C_GREEN)
        inset.annotate(label, xy=(i, vv + 0.001), ha="center", fontsize=11,
                       color=color, fontweight="bold")

    inset.set_xticks(x)
    inset.set_xticklabels(runs, fontsize=12)
    inset.set_ylabel("Reconstruction loss", fontsize=12)
    inset.set_ylim(0, 0.046)
    inset.set_facecolor(C_GREY)
    inset.spines["top"].set_visible(False)
    inset.spines["right"].set_visible(False)
    inset.legend(fontsize=12, loc="upper right")
    inset.axhline(0.03309, color=C_DKGREY, linestyle="--", lw=1, alpha=0.5,
                  label="baseline val rec")
    inset.text(2.55, 0.03309 + 0.0005, "baseline val rec", fontsize=9,
               color=C_DKGREY, ha="right")

    ax.text(W/2, 0.18, "* GN encoder ep-57 bars show underfitting — both values high, model had not converged.",
            fontsize=11, color=C_DKGREY, style="italic", ha="center", va="center",
            transform=ax.transData)

    pdf.savefig(fig, bbox_inches="tight"); plt.close()


    # ════════════════════════════════════════════════════════════════════════
    # Page 8 — Projections
    # ════════════════════════════════════════════════════════════════════════
    fig, ax = new_fig()
    header(ax, "Projections — What to Expect When the Run Completes",
           "GN + Noise  ·  ep 1033 / 10 000  ·  early stopping from ep 2000")

    card(ax, 0.3, 0.3, 7.5, 7.0)
    txt(ax, "Likely trajectory", 0.55, H - 1.55, size=14, bold=True, color=C_BLUE)
    bullet_lines(ax, [
        "Train rec will keep decreasing slowly (noise prevents zero, but model continues improving).",
        "Val rec may decrease further or plateau. Current 0.031 is already the best observed.",
        "Active dims will keep decreasing as vol pressure prunes more. If val rec stays low, pruning could reach <60 dims.",
        "Early stopping from ep 2000 (patience 50) will stop once val rec plateaus — the right termination criterion.",
        ("✓  ", "If val rec < 0.030 with ≤60 active dims at termination: strictly better than baseline in both quality and compactness.", 11, True, C_GREEN),
        ("→  ", "If gap stays at 3.65× until end: encoder still overfits. Try orthogonality regularisation + val gate combined.", 11, False, C_ORANGE),
    ], 0.55, H - 1.95, col_width=7.0, size=11)

    card(ax, 8.1, 0.3, 7.5, 7.0)
    txt(ax, "Missing ablation: GN alone", 8.35, H - 1.55, size=14, bold=True, color=C_BLUE)
    bullet_lines(ax, [
        ("⚠  ", "GN run stopped at ep 57 — too early to be useful.", 12, True, C_ORANGE),
        "We cannot yet separate the effect of GN encoder vs. the noise σ=0.1.",
        ("→  ", "Proposed re-run:", 11, True, C_BLUE),
        ("    ", "• early_stopping_start_epoch = 2000", 11, False, C_DKGREY),
        ("    ", "• patience = 50", 11, False, C_DKGREY),
        ("    ", "• latent_noise_sigma = 0.0  (no noise)", 11, False, C_DKGREY),
        ("    ", "• all other params identical to noise run", 11, False, C_DKGREY),
        "",
        ("→  ", "Fair comparison we have NOW:", 11, True, C_BLUE),
        ("    ", "Baseline BN (ep 9999, full)  vs  GN+Noise (ep 1033, running)", 11, False, C_BLACK),
        ("    ", "Val rec:  0.033  →  0.031   ✓", 11, True, C_GREEN),
        ("    ", "Gap:      80×    →  3.65×   ✓", 11, True, C_GREEN),
    ], 8.35, H - 1.95, col_width=7.0, size=11)
    pdf.savefig(fig, bbox_inches="tight"); plt.close()


    # ════════════════════════════════════════════════════════════════════════
    # Page 9 — Next steps
    # ════════════════════════════════════════════════════════════════════════
    fig, ax = new_fig()
    header(ax, "Next Steps", "In priority order")

    steps = [
        (C_GREEN,  "1.  Wait for GN + Noise run to complete (ep 2000+)",
         "Run is at ep 1033. Early stopping from ep 2000 determines final val rec and active dim count. Most important data point — wait before drawing conclusions."),
        (C_ORANGE, "2.  Re-run GN encoder WITHOUT noise (proper early stopping)",
         "Use early_stopping_start_epoch=2000, patience=50, latent_noise_sigma=0.0. Gives the missing ablation point to isolate GN vs noise effects."),
        (C_ORANGE, "3.  If val gap persists (>2×): test GN + Noise + Val-Gate combined",
         "Val-gate variants are also running. If val gate alone helps, the combination (noise + val gate) may be the strongest regulariser."),
        (C_BLUE,   "4.  Analyse active dim count at full convergence",
         "Baseline: 65/100 at ep 9999. If noise run converges at <60 dims with better val rec → more compact AND generalisable — a double win."),
        (C_DKGREY, "5.  Extend analysis to constrained LVAE and PLVAE",
         "Constrained and PLVAE noise runs are also running in parallel. Check if the benefit of noise is consistent across all three architectures."),
    ]

    y0 = H - 1.6
    for col, title, desc in steps:
        ax.add_patch(plt.Rectangle((0.3, y0 - 1.05), 0.12, 0.9, color=col))
        card(ax, 0.5, y0 - 1.08, 15.4, 0.98, fill=C_GREY)
        ax.text(0.7, y0 - 0.38, title, fontsize=13, fontweight="bold", color=C_BLACK, va="center")
        ax.text(0.7, y0 - 0.75, desc,  fontsize=11, color=C_DKGREY, va="center")
        y0 -= 1.18

    pdf.savefig(fig, bbox_inches="tight"); plt.close()

print(f"Saved: {PDF_PATH}")
print("9 slides — open in VS Code with any PDF viewer extension.")
