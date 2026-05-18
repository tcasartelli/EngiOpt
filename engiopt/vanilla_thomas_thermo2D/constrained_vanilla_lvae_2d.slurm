#!/bin/bash
#SBATCH --job-name=constrained_vanilla_lvae_2d #questo indica 
#SBATCH --time=24:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=8G
#SBATCH --gpus=rtx_4090:1
#SBATCH --output=/cluster/scratch/tcasartelli/constrained_vanilla_lvae_2d/logs/constrained_vanilla_lvae_2d_%j.out
#SBATCH --error=/cluster/scratch/tcasartelli/constrained_vanilla_lvae_2d/logs/constrained_vanilla_lvae_2d_%j.err
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=tcasartelli@ethz.ch

# Create output directories on $SCRATCH
mkdir -p /cluster/scratch/tcasartelli/constrained_vanilla_lvae_2d/logs
mkdir -p /cluster/scratch/tcasartelli/constrained_vanilla_lvae_2d/images
mkdir -p /cluster/scratch/tcasartelli/constrained_vanilla_lvae_2d/checkpoints

# Load modules
module purge
module load stack/2024-06
module load gcc/12.2.0
module load python_cuda/3.11.6
module load cuda/12.8.0
module load eth_proxy

# Activate virtual environment
VENV_DIR="/cluster/home/tcasartelli/venv/engibench"
source "$VENV_DIR/bin/activate"

# W&B credentials
export no_proxy=$(echo "$no_proxy" | sed 's/api\.wandb\.ai,\?//g; s/,$//')
export NO_PROXY=$(echo "$NO_PROXY" | sed 's/api\.wandb\.ai,\?//g; s/,$//')
source ~/.secrets/ml_env.sh
export WANDB_MODE=online
export WANDB_DIR=/cluster/scratch/tcasartelli/constrained_vanilla_lvae_2d
export WANDB_HTTP_TIMEOUT=120
export WANDB_INIT_TIMEOUT=120

python /cluster/home/tcasartelli/projects/EngiOpt/engiopt/vanilla_thomas_thermo2D/constrained_vanilla_lvae_2d.py \
    --problem_id thermoelastic2d \
    --seed 1 \
    --n_epochs 10000 \
    --batch_size 128 \
    --lr 1e-4 \
    --latent_dim 300 \
    --resize_dimensions 100 100 \
    --nmse_threshold 0.25 \
    --pruning_epoch 500 \
    --pruning_threshold 0.05 \
    --pruning_strategy plummet \
    --images_dir /cluster/scratch/tcasartelli/constrained_vanilla_lvae_2d/images \
    --checkpoint_dir /cluster/scratch/tcasartelli/constrained_vanilla_lvae_2d/checkpoints \
    --save_model \
    --track \
    --wandb_project thermoelastic2d_dfull_dataset_augmentation \
    --wandb_run_name no_aug_latent300_nmse_0.25_constrained_vanilla_lvae_2d
