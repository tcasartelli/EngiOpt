"""Evaluation script: reconstruction quality and latent space visualization.

Usage (single checkpoint):
    python evaluate_reconstructions.py \
        --checkpoint /path/to/checkpoint.pth \
        --output_dir ./eval_plots \
        --latent_space

Usage (compare all three weight subsets):
    python evaluate_reconstructions.py \
        --checkpoint_weight_1 /path/weight_1/checkpoints/thermoelastic2d_constrained_lvae.pth \
        --checkpoint_weight_0 /path/weight_0/checkpoints/thermoelastic2d_constrained_lvae.pth \
        --checkpoint_mixed   /path/weight_mixed/checkpoints/thermoelastic2d_constrained_lvae.pth \
        --output_dir ./eval_plots \
        --compare
"""

from __future__ import annotations

import argparse
import os

from engibench.utils.all_problems import BUILTIN_PROBLEMS
import matplotlib.pyplot as plt
import numpy as np
import torch as th
from torch.optim import Adam

from engiopt.vanilla_lvae.aes import ConstrainedLeastVolumeAE_DP
from engiopt.vanilla_lvae.components import Encoder2D
from engiopt.vanilla_lvae.components import TrueSNDecoder2D
from engiopt.vanilla_lvae.utils import filter_dataset_by_condition


# ── Model loading ─────────────────────────────────────────────────────────────

def load_model_and_data(ckpt_path: str, device: th.device):
    ckpt = th.load(ckpt_path, map_location=device)
    a = argparse.Namespace(**ckpt["args"])

    # Restore tuple types that JSON-round-trips as lists
    if isinstance(a.resize_dimensions, list):
        a.resize_dimensions = tuple(a.resize_dimensions)
    if isinstance(a.condition_filter_range, list):
        a.condition_filter_range = tuple(a.condition_filter_range)

    problem = BUILTIN_PROBLEMS[a.problem_id]()
    problem.reset(seed=a.seed)
    design_shape = problem.design_space.shape

    enc = Encoder2D(a.latent_dim, design_shape, a.resize_dimensions)
    dec = TrueSNDecoder2D(a.latent_dim, design_shape, lipschitz_scale=a.decoder_lipschitz_scale)
    lvae = ConstrainedLeastVolumeAE_DP(
        encoder=enc,
        decoder=dec,
        optimizer=Adam(list(enc.parameters()) + list(dec.parameters()), lr=a.lr),
        latent_dim=a.latent_dim,
        nmse_threshold=a.nmse_threshold,
        pruning_epoch=a.pruning_epoch,
        pruning_threshold=a.pruning_threshold,
        pruning_strategy=a.pruning_strategy,
        alpha=a.alpha,
    ).to(device)

    lvae.encoder.load_state_dict(ckpt["encoder"])
    lvae.decoder.load_state_dict(ckpt["decoder"])
    lvae._p = ckpt["pruning_mask"].to(device)
    lvae._z = ckpt["pruning_frozen_z"].to(device)
    lvae.eval()

    # Load dataset with same filtering as training
    raw_train = problem.dataset["train"]
    raw_val   = problem.dataset["val"]
    if a.condition_filter_key is not None:
        raw_train = filter_dataset_by_condition(
            raw_train, a.condition_filter_key,
            value=a.condition_filter_value,
            value_range=a.condition_filter_range,
            tolerance=a.condition_filter_tolerance,
        )
        raw_val = filter_dataset_by_condition(
            raw_val, a.condition_filter_key,
            value=a.condition_filter_value,
            value_range=a.condition_filter_range,
            tolerance=a.condition_filter_tolerance,
        )

    x_train = th.tensor(np.array(raw_train["optimal_design"])).float().unsqueeze(1)
    x_val   = th.tensor(np.array(raw_val["optimal_design"])).float().unsqueeze(1)

    return lvae, a, design_shape, x_train, x_val, raw_train, raw_val


# ── Plot helpers ──────────────────────────────────────────────────────────────

def plot_reconstruction(lvae, x, design_shape, device, n=25, title="", save_path=None):
    """N rows × 2 cols: Original | Reconstructed."""
    with th.no_grad():
        x_in  = x[:n].to(device)
        x_rec = lvae.decode(lvae.encode(x_in)).cpu().numpy()
    x_orig = x[:n].squeeze(1).numpy()

    fig, axs = plt.subplots(n, 2, figsize=(4, n * 1.8))
    axs[0, 0].set_title("Original",       fontsize=9)
    axs[0, 1].set_title("Reconstructed",  fontsize=9)
    for i in range(n):
        for col, img in enumerate([x_orig[i], x_rec[i].squeeze()]):
            axs[i, col].imshow(img.reshape(design_shape), cmap="viridis")
            axs[i, col].axis("off")
    fig.suptitle(title, fontsize=11, y=1.002)
    fig.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=100, bbox_inches="tight")
        plt.close()
        print(f"  Saved: {save_path}")
    return fig


def plot_latent_top2(lvae, x, weights, device, title="", save_path=None):
    """Plot the 2 most important active latent dimensions (by variance), colored by weight."""
    with th.no_grad():
        z_full = lvae.encode(x.to(device)).cpu()

    active_mask = ~lvae._p.cpu()
    z_active = z_full[:, active_mask]
    stds = z_active.std(dim=0)

    top2 = stds.argsort(descending=True)[:2]
    active_indices = th.where(active_mask)[0]
    dim0 = active_indices[top2[0]].item()
    dim1 = active_indices[top2[1]].item()

    x_vals = z_full[:, dim0].numpy()
    y_vals = z_full[:, dim1].numpy()

    fig, ax = plt.subplots(figsize=(7, 5))
    sc = ax.scatter(x_vals, y_vals, c=weights, cmap="coolwarm", alpha=0.5, s=8)
    plt.colorbar(sc, ax=ax, label="weight")
    ax.set_xlabel(f"z[{dim0}]  (std={stds[top2[0]]:.3f})")
    ax.set_ylabel(f"z[{dim1}]  (std={stds[top2[1]]:.3f})")
    ax.set_title(title)
    fig.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"  Saved: {save_path}")
    return fig


def plot_comparison_grid(models: dict, design_shape, device, split="val", n=10, save_path=None):
    """One column per model, rows = samples. Odd cols = original, even = reconstructed."""
    labels = list(models.keys())
    k      = len(labels)

    fig, axs = plt.subplots(n, k * 2, figsize=(k * 4, n * 2))
    for col, label in enumerate(labels):
        lvae, x = models[label]
        with th.no_grad():
            x_in  = x[:n].to(device)
            x_rec = lvae.decode(lvae.encode(x_in)).cpu().numpy()
        x_orig = x[:n].squeeze(1).numpy()

        axs[0, col * 2].set_title(f"{label}\nOriginal",      fontsize=8)
        axs[0, col * 2 + 1].set_title(f"{label}\nRecon",     fontsize=8)
        for row in range(n):
            for offset, img in enumerate([x_orig[row], x_rec[row].squeeze()]):
                axs[row, col * 2 + offset].imshow(img.reshape(design_shape), cmap="viridis")
                axs[row, col * 2 + offset].axis("off")

    fig.suptitle(f"Reconstruction comparison — {split}", fontsize=12)
    fig.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=100, bbox_inches="tight")
        plt.close()
        print(f"  Saved: {save_path}")
    return fig


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # Single-checkpoint mode
    parser.add_argument("--checkpoint",  type=str, default=None)

    # Compare mode (all three weight subsets)
    parser.add_argument("--checkpoint_weight_1", type=str, default=None)
    parser.add_argument("--checkpoint_weight_0", type=str, default=None)
    parser.add_argument("--checkpoint_mixed",    type=str, default=None)
    parser.add_argument("--compare", action="store_true",
                        help="Generate side-by-side comparison across all three subsets")

    parser.add_argument("--output_dir",  type=str, default="./eval_plots")
    parser.add_argument("--n_samples",   type=int, default=25,
                        help="Number of samples for reconstruction plots")
    parser.add_argument("--latent_space", action="store_true",
                        help="Generate top-2 latent dimension plots (colored by weight)")
    args = parser.parse_args()

    device = th.device("cuda" if th.cuda.is_available() else "cpu")
    os.makedirs(args.output_dir, exist_ok=True)
    print(f"Device: {device}")

    # ── Single checkpoint ──────────────────────────────────────────────────
    if args.checkpoint:
        print(f"\nLoading {args.checkpoint}")
        lvae, a, design_shape, x_train, x_val, raw_train, raw_val = \
            load_model_and_data(args.checkpoint, device)
        label = a.wandb_run_name or "model"
        print(f"  active_dims={lvae.dim}  train={len(x_train)}  val={len(x_val)}")

        plot_reconstruction(lvae, x_train, design_shape, device,
                            n=args.n_samples, title=f"Train reconstruction — {label}",
                            save_path=os.path.join(args.output_dir, f"{label}_train_recon.png"))
        plot_reconstruction(lvae, x_val, design_shape, device,
                            n=args.n_samples, title=f"Val reconstruction — {label}",
                            save_path=os.path.join(args.output_dir, f"{label}_val_recon.png"))

        if args.latent_space:
            w_train = np.array(raw_train["weight"])
            w_val   = np.array(raw_val["weight"])
            plot_latent_top2(lvae, x_train, w_train, device,
                             title=f"Top-2 latent dims (train) — {label}",
                             save_path=os.path.join(args.output_dir, f"{label}_latent_top2_train.png"))
            plot_latent_top2(lvae, x_val, w_val, device,
                             title=f"Top-2 latent dims (val) — {label}",
                             save_path=os.path.join(args.output_dir, f"{label}_latent_top2_val.png"))

    # ── Compare mode ───────────────────────────────────────────────────────
    if args.compare:
        ckpts = {
            "weight_1": args.checkpoint_weight_1,
            "weight_0": args.checkpoint_weight_0,
            "mixed":    args.checkpoint_mixed,
        }
        loaded = {}
        design_shape = None
        for name, path in ckpts.items():
            if path is None:
                print(f"  Skipping {name} (no checkpoint provided)")
                continue
            print(f"\nLoading {name}: {path}")
            lvae, a, design_shape, x_train, x_val, raw_train, raw_val = \
                load_model_and_data(path, device)
            print(f"  active_dims={lvae.dim}  train={len(x_train)}  val={len(x_val)}")
            loaded[name] = {"lvae": lvae, "x_train": x_train, "x_val": x_val,
                            "raw_train": raw_train, "raw_val": raw_val}

        # Side-by-side comparison (train)
        plot_comparison_grid(
            {k: (v["lvae"], v["x_train"]) for k, v in loaded.items()},
            design_shape, device, split="train", n=args.n_samples,
            save_path=os.path.join(args.output_dir, "compare_train_recon.png"),
        )
        # Side-by-side comparison (val)
        plot_comparison_grid(
            {k: (v["lvae"], v["x_val"]) for k, v in loaded.items()},
            design_shape, device, split="val", n=args.n_samples,
            save_path=os.path.join(args.output_dir, "compare_val_recon.png"),
        )

        # Individual train+val per model
        for name, data in loaded.items():
            plot_reconstruction(data["lvae"], data["x_train"], design_shape, device,
                                n=args.n_samples, title=f"Train reconstruction — {name}",
                                save_path=os.path.join(args.output_dir, f"{name}_train_recon.png"))
            plot_reconstruction(data["lvae"], data["x_val"], design_shape, device,
                                n=args.n_samples, title=f"Val reconstruction — {name}",
                                save_path=os.path.join(args.output_dir, f"{name}_val_recon.png"))

        # Latent space for each model colored by weight
        if args.latent_space:
            for name, data in loaded.items():
                w_train = np.array(data["raw_train"]["weight"])
                w_val   = np.array(data["raw_val"]["weight"])
                plot_latent_top2(data["lvae"], data["x_train"], w_train, device,
                                 title=f"Top-2 latent dims (train) — {name}",
                                 save_path=os.path.join(args.output_dir, f"{name}_latent_top2_train.png"))
                plot_latent_top2(data["lvae"], data["x_val"], w_val, device,
                                 title=f"Top-2 latent dims (val) — {name}",
                                 save_path=os.path.join(args.output_dir, f"{name}_latent_top2_val.png"))

    print("\nDone.")
