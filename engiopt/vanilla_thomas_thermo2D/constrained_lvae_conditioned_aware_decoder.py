"""Constrained LVAE with condition-aware decoder for 2D thermoelastic designs.

Extends the baseline constrained LVAE by concatenating scalar design conditions
(weight, volume_fraction_target) directly to the decoder input alongside z. This
forces z to encode only topology — the latent space should be cleaner and need
fewer active dims compared to the unconditional baseline.

Key difference from baseline: TrueSNDecoder2D is built with cond_dim > 0,
and conditions are passed through the training/validation/visualisation loops.

For more information on LVAE, see: https://arxiv.org/abs/2404.17773
"""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import product
import os
import random
import time

from engibench.utils.all_problems import BUILTIN_PROBLEMS
import matplotlib.pyplot as plt
import numpy as np
from sklearn.preprocessing import RobustScaler
import torch as th
from torch.optim import Adam
from torch.utils.data import DataLoader
from torch.utils.data import TensorDataset
import tqdm
import tyro

from engiopt.vanilla_lvae.aes import ConstrainedLeastVolumeAE_DP
from engiopt.vanilla_lvae.components import Encoder2D
from engiopt.vanilla_lvae.components import TrueSNDecoder2D
from engiopt.vanilla_lvae.utils import filter_dataset_by_condition
import wandb


# ---------------------------------------------------------------------------
# Condition-aware LVAE: decoder receives z || cond at each forward pass
# ---------------------------------------------------------------------------

class ConditionedConstrainedLVAE(ConstrainedLeastVolumeAE_DP):
    """ConstrainedLeastVolumeAE_DP where the decoder is condition-aware.

    The only change vs the parent is that decode() and loss() accept and
    forward a condition tensor to the underlying TrueSNDecoder2D.
    """

    def decode(self, z: th.Tensor, cond: th.Tensor | None = None) -> th.Tensor:
        """Decode with pruned dimensions frozen; passes cond to decoder."""
        z = z.clone()
        z[:, self._p] = self._z[self._p]
        return self.decoder(z, cond=cond)

    def loss(self, batch: tuple[th.Tensor, th.Tensor]) -> th.Tensor:
        """Compute NMSE-gated volume loss with condition-aware reconstruction.

        Args:
            batch: Tuple of (x, cond) — design and scaled condition vectors.

        Returns:
            Scalar loss for backpropagation.
        """
        x, c = batch
        z = self.encode(x)
        self._update_moving_mean(z)
        x_hat = self.decode(self._maybe_add_noise(z), cond=c)

        rec_loss = self.loss_rec(x, x_hat)

        s = self._frozen_std.clone()
        if (~self._p).any():
            s[~self._p] = z[:, ~self._p].std(0)
        vol_loss = th.exp(th.log(s).mean())

        nmse = rec_loss / self._data_var
        self._current_nmse = nmse.item()
        self._current_rec_loss = rec_loss.item()
        self._current_vol_loss = vol_loss.item()

        if nmse > self.nmse_threshold or not self._val_nmse_ok:
            self._vol_active = False
            return rec_loss
        self._vol_active = True
        return vol_loss + rec_loss


# ---------------------------------------------------------------------------
# Arguments
# ---------------------------------------------------------------------------

@dataclass
class Args:
    """Command-line arguments for condition-aware constrained LVAE training."""

    # Problem and tracking
    problem_id: str = "thermoelastic2d"
    """Problem ID to run. Must be one of the built-in problems in engibench."""
    algo: str = os.path.basename(__file__)[: -len(".py")]
    """Algorithm name for tracking purposes."""
    track: bool = True
    """Whether to track with Weights & Biases."""
    wandb_project: str = "engiopt"
    """WandB project name."""
    wandb_entity: str | None = None
    """WandB entity name. If None, uses the default entity."""
    seed: int = 1
    """Random seed for reproducibility."""
    save_model: bool = False
    """Whether to save the model after training."""
    sample_interval: int = 500
    """Interval for sampling designs during training."""

    # Training parameters
    n_epochs: int = 10000
    """Number of training epochs."""
    batch_size: int = 128
    """Batch size for training."""
    lr: float = 1e-4
    """Learning rate for the optimizer."""

    # LVAE-specific
    latent_dim: int = 100
    """Dimensionality of the latent space (overestimate)."""

    # Constraint parameters
    nmse_threshold: float = 0.25
    """NMSE ceiling. Training aims to stay at or below this threshold."""

    # Pruning parameters
    pruning_epoch: int = 500
    """Epoch to start pruning dimensions."""
    pruning_threshold: float = 0.05
    """Threshold for pruning (ratio for plummet, percentile for lognorm)."""
    pruning_strategy: str = "plummet"
    """Pruning strategy: 'plummet' or 'lognorm'."""
    alpha: float = 0.0
    """(lognorm only) Blending factor between reference and current distribution."""

    # Architecture
    resize_dimensions: tuple[int, int] = (100, 100)
    """Dimensions to resize input images to before encoding/decoding."""
    decoder_lipschitz_scale: float = 1.0
    """Lipschitz bound for spectrally normalized decoder."""

    # Condition keys to inject into the decoder
    condition_keys: list[str] = field(default_factory=lambda: ["weight", "volume_fraction_target"])
    """Dataset columns to use as decoder conditions. Scaled with RobustScaler before injection."""

    # Dataset filtering
    condition_filter_key: str | None = None
    """Condition key to filter dataset on (e.g., 'weight'). None = use all data."""
    condition_filter_value: float | None = None
    """Exact value to match (within tolerance). Mutually exclusive with condition_filter_range."""
    condition_filter_range: tuple[float, float] | None = None
    """Inclusive [lo, hi] range to filter on. Overrides condition_filter_value."""
    condition_filter_tolerance: float = 0.01
    """Tolerance for exact-value matching."""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    args = tyro.cli(Args)

    problem = BUILTIN_PROBLEMS[args.problem_id]()
    problem.reset(seed=args.seed)
    design_shape = problem.design_space.shape

    run_name = f"{args.problem_id}__{args.algo}__{args.seed}__{int(time.time())}"
    if args.track:
        wandb.init(
            project=args.wandb_project,
            entity=args.wandb_entity,
            config=vars(args),
            save_code=True,
            name=run_name,
        )

    th.manual_seed(args.seed)
    th.cuda.manual_seed_all(args.seed)
    rng = np.random.default_rng(args.seed)
    random.seed(args.seed)
    th.backends.cudnn.deterministic = True
    th.backends.cudnn.benchmark = False
    g = th.Generator().manual_seed(args.seed)

    os.makedirs("images", exist_ok=True)

    if th.backends.mps.is_available():
        device = th.device("mps")
    elif th.cuda.is_available():
        device = th.device("cuda")
    else:
        device = th.device("cpu")

    # ---- DataLoader ----
    raw_train = problem.dataset["train"]
    raw_val = problem.dataset["val"]

    if args.condition_filter_key is not None:
        raw_train = filter_dataset_by_condition(
            raw_train,
            args.condition_filter_key,
            value=args.condition_filter_value,
            value_range=args.condition_filter_range,
            tolerance=args.condition_filter_tolerance,
        )
        raw_val = filter_dataset_by_condition(
            raw_val,
            args.condition_filter_key,
            value=args.condition_filter_value,
            value_range=args.condition_filter_range,
            tolerance=args.condition_filter_tolerance,
        )

    # Convert to torch via numpy to avoid torchvision.io.VideoReader import bug
    # in the HuggingFace torch formatter on this cluster's torchvision version.
    x_train = th.from_numpy(np.array(raw_train["optimal_design"])).float().unsqueeze(1)
    x_val = th.from_numpy(np.array(raw_val["optimal_design"])).float().unsqueeze(1)

    # Extract and scale condition vectors with RobustScaler (fit on train only)
    n_conds = len(args.condition_keys)
    c_train_raw = th.stack([th.tensor(raw_train[k], dtype=th.float32) for k in args.condition_keys], dim=-1)
    c_val_raw = th.stack([th.tensor(raw_val[k], dtype=th.float32) for k in args.condition_keys], dim=-1)

    c_scaler = RobustScaler()
    c_train = th.from_numpy(c_scaler.fit_transform(c_train_raw.numpy())).float()
    c_val = th.from_numpy(c_scaler.transform(c_val_raw.numpy())).float()

    # ---- Build encoder and decoder ----
    enc = Encoder2D(args.latent_dim, design_shape, args.resize_dimensions)
    dec = TrueSNDecoder2D(
        args.latent_dim,
        design_shape,
        lipschitz_scale=args.decoder_lipschitz_scale,
        cond_dim=n_conds,
    )

    lvae = ConditionedConstrainedLVAE(
        encoder=enc,
        decoder=dec,
        optimizer=Adam(list(enc.parameters()) + list(dec.parameters()), lr=args.lr),
        latent_dim=args.latent_dim,
        nmse_threshold=args.nmse_threshold,
        pruning_epoch=args.pruning_epoch,
        pruning_threshold=args.pruning_threshold,
        pruning_strategy=args.pruning_strategy,
        alpha=args.alpha,
    ).to(device)

    lvae.set_data_variance(x_train)

    print(f"\n{'=' * 60}")
    print("Condition-Aware Constrained LVAE Training")
    print(f"Problem: {args.problem_id}")
    print(f"Latent dim: {args.latent_dim}")
    print(f"Condition keys: {args.condition_keys}  (cond_dim={n_conds})")
    print(f"Decoder: TrueSNDecoder2D (lipschitz_scale={args.decoder_lipschitz_scale}, cond_dim={n_conds})")
    print(f"NMSE threshold: {args.nmse_threshold} (R² = {1 - args.nmse_threshold:.2%})")
    print(f"Data variance: {lvae.data_var:.6f}")
    print(f"Pruning epoch: {args.pruning_epoch}")
    print(f"Pruning strategy: {args.pruning_strategy}")
    print(f"Pruning threshold: {args.pruning_threshold}")
    if args.pruning_strategy == "lognorm":
        print(f"Alpha (lognorm): {args.alpha}")
    print(f"{'=' * 60}\n")

    loader = DataLoader(
        TensorDataset(x_train, c_train),
        batch_size=args.batch_size,
        shuffle=True,
        generator=g,
    )
    val_loader = DataLoader(
        TensorDataset(x_val, c_val),
        batch_size=args.batch_size,
        shuffle=False,
    )

    # ---- Training loop ----
    for epoch in range(args.n_epochs):
        lvae.epoch_hook(epoch=epoch)

        bar = tqdm.tqdm(loader, desc=f"Epoch {epoch}")
        for i, batch in enumerate(bar):
            x_batch = batch[0].to(device)
            c_batch = batch[1].to(device)
            lvae.optim.zero_grad()

            loss = lvae.loss((x_batch, c_batch))
            loss.backward()
            lvae.optim.step()

            bar.set_postfix(
                {
                    "rec": f"{lvae.rec_loss:.4f}",
                    "vol": f"{lvae.vol_loss:.4f}",
                    "nmse": f"{lvae.nmse:.4f}",
                    "active": int(lvae.vol_active),
                    "dim": lvae.dim,
                }
            )

            if args.track:
                batches_done = epoch * len(bar) + i

                wandb.log({
                    "rec_loss": lvae.rec_loss,
                    "vol_loss": lvae.vol_loss,
                    "total_loss": loss.item(),
                    "nmse": lvae.nmse,
                    "nmse_threshold": args.nmse_threshold,
                    "vol_active": int(lvae.vol_active),
                    "active_dims": lvae.dim,
                    "epoch": epoch,
                })

                print(
                    f"[Epoch {epoch}/{args.n_epochs}] [Batch {i}/{len(bar)}] "
                    f"[rec: {lvae.rec_loss:.4f}] [vol: {lvae.vol_loss:.4f}] [nmse: {lvae.nmse:.4f}] "
                    f"[active: {int(lvae.vol_active)}] [dims: {lvae.dim}]"
                )

                if batches_done % args.sample_interval == 0:
                    with th.no_grad():
                        xs = x_train.to(device)
                        cs = c_train.to(device)
                        z = lvae.encode(xs)
                        z_std, idx = th.sort(z.std(0), descending=True)
                        z_mean = z.mean(0)
                        c_mean = cs.mean(0)
                        n_active = (z_std > 0).sum().item()

                        # Interpolated designs: interpolate both z and conditions
                        x_ints = []
                        for alpha in [0, 0.25, 0.5, 0.75, 1]:
                            z_ = (1 - alpha) * z[:25] + alpha * th.roll(z, -1, 0)[:25]
                            c_ = (1 - alpha) * cs[:25] + alpha * th.roll(cs, -1, 0)[:25]
                            x_ints.append(lvae.decode(z_, cond=c_).clamp(0, 1).cpu().numpy())

                        # Random designs sampled from latent space using mean condition
                        z_rand = z_mean.unsqueeze(0).repeat([25, 1])
                        z_rand[:, idx[:n_active]] += z_std[:n_active] * th.randn_like(z_rand[:, idx[:n_active]])
                        c_rand = c_mean.unsqueeze(0).repeat([25, 1])
                        x_rand = lvae.decode(z_rand, cond=c_rand).clamp(0, 1).cpu().numpy()

                        z_std_cpu = z_std.cpu().numpy()
                        xs_cpu = xs.cpu().numpy()

                    # Plot 1: latent dimension statistics
                    plt.figure(figsize=(12, 6))
                    plt.subplot(211)
                    plt.bar(np.arange(len(z_std_cpu)), z_std_cpu)
                    plt.yscale("log")
                    plt.xlabel("Latent dimension index")
                    plt.ylabel("Standard deviation")
                    plt.title(f"Number of principal components = {n_active}")
                    plt.subplot(212)
                    plt.bar(np.arange(n_active), z_std_cpu[:n_active])
                    plt.yscale("log")
                    plt.xlabel("Latent dimension index")
                    plt.ylabel("Standard deviation")
                    plt.savefig(f"images/dim_{batches_done}.png")
                    plt.close()

                    # Plot 2: interpolated designs
                    fig, axs = plt.subplots(25, 6, figsize=(12, 25))
                    for i_row, j in product(range(25), range(5)):
                        axs[i_row, j + 1].imshow(x_ints[j][i_row].reshape(design_shape))
                        axs[i_row, j + 1].axis("off")
                        axs[i_row, j + 1].set_aspect("equal")
                    for ax, alpha in zip(axs[0, 1:], [0, 0.25, 0.5, 0.75, 1]):
                        ax.set_title(rf"$\alpha$ = {alpha}")
                    for i_row in range(25):
                        axs[i_row, 0].imshow(xs_cpu[i_row].reshape(design_shape))
                        axs[i_row, 0].axis("off")
                        axs[i_row, 0].set_aspect("equal")
                    axs[0, 0].set_title("groundtruth")
                    fig.tight_layout()
                    plt.savefig(f"images/interp_{batches_done}.png")
                    plt.close()

                    # Plot 3: random designs from latent space (mean condition)
                    fig, axs = plt.subplots(5, 5, figsize=(15, 7.5))
                    for k, (i_row, j) in enumerate(product(range(5), range(5))):
                        axs[i_row, j].imshow(x_rand[k].reshape(design_shape))
                        axs[i_row, j].axis("off")
                        axs[i_row, j].set_aspect("equal")
                    fig.tight_layout()
                    plt.suptitle(f"Gaussian random designs (mean condition: {c_mean.cpu().numpy().round(2).tolist()})")
                    plt.savefig(f"images/norm_{batches_done}.png")
                    plt.close()

                    wandb.log({
                        "dim_plot": wandb.Image(f"images/dim_{batches_done}.png"),
                        "interp_plot": wandb.Image(f"images/interp_{batches_done}.png"),
                        "norm_plot": wandb.Image(f"images/norm_{batches_done}.png"),
                    })

        lvae.epoch_report(epoch=epoch, callbacks=[], batch=None, loss=loss, pbar=None)

        # ---- Validation ----
        with th.no_grad():
            lvae.eval()
            val_rec = val_vol = val_nmse = 0.0
            n = 0
            for batch_v in val_loader:
                x_v = batch_v[0].to(device)
                c_v = batch_v[1].to(device)
                _ = lvae.loss((x_v, c_v))
                bsz = x_v.size(0)
                val_rec += lvae.rec_loss * bsz
                val_vol += lvae.vol_loss * bsz
                val_nmse += lvae.nmse * bsz
                n += bsz
            val_rec /= n
            val_vol /= n
            val_nmse /= n
            lvae.train()

        if args.track:
            wandb.log({
                "epoch": epoch,
                "val_rec_loss": val_rec,
                "val_vol_loss": val_vol,
                "val_nmse": val_nmse,
            }, commit=True)

        th.cuda.empty_cache()
        lvae.train()

        if args.save_model and epoch == args.n_epochs - 1:
            ckpt_lvae = {
                "epoch": epoch,
                "encoder": lvae.encoder.state_dict(),
                "decoder": lvae.decoder.state_dict(),
                "optimizer": lvae.optim.state_dict(),
                "pruning_mask": lvae._p.cpu(),
                "pruning_frozen_z": lvae._z.cpu(),
                "condition_keys": args.condition_keys,
                "c_scaler": c_scaler,
                "args": vars(args),
            }
            th.save(ckpt_lvae, "constrained_vanilla_lvae_cond_decoder.pth")
            if args.track:
                artifact = wandb.Artifact(f"{args.problem_id}_{args.algo}", type="model")
                artifact.add_file("constrained_vanilla_lvae_cond_decoder.pth")
                alias = f"seed_{args.seed}"
                if args.condition_filter_key is not None:
                    if args.condition_filter_range is not None:
                        lo, hi = args.condition_filter_range
                        alias += f"_{args.condition_filter_key}_{lo}-{hi}"
                    elif args.condition_filter_value is not None:
                        alias += f"_{args.condition_filter_key}_{args.condition_filter_value}"
                wandb.log_artifact(artifact, aliases=[alias])

    if args.track:
        wandb.finish()
