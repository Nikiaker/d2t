#!/bin/bash
#SBATCH -w hgx2
#SBATCH -p hgx
#SBATCH --gres=gpu:1
#SBATCH -n1
nvidia-smi