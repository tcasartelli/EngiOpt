#!/bin/bash
#SBATCH --job-name=setup_engi_venv
#SBATCH --time=02:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=8G
#SBATCH --output=/cluster/home/tcasartelli/setup_engi_venv_%j.out
#SBATCH --error=/cluster/home/tcasartelli/setup_engi_venv_%j.err
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=tcasartelli@ethz.ch

set -e

module purge
module load stack/2024-06
module load gcc/12.2.0
module load python_cuda/3.11.6
module load cuda/12.8.0
module load eth_proxy

VENV_DIR="/cluster/scratch/tcasartelli/engi-venv"

echo "==> Removing old engi-venv..."
rm -rf "$VENV_DIR"

echo "==> Creating new venv at $VENV_DIR..."
python -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

echo "==> Upgrading pip..."
pip install --upgrade pip

echo "==> Installing engiopt project (pip install -e .)..."
cd /cluster/home/tcasartelli/projects/EngiOpt
pip install -e ".[all]"

echo "==> Verifying installation..."
python -c "import torch; print('torch:', torch.__version__, '| CUDA:', torch.cuda.is_available())"
python -c "import engiopt; print('engiopt imported OK')"

echo "==> Done! engi-venv ready."
