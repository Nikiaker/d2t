#!/bin/bash
#SBATCH -w hgx2
#SBATCH -p hgx
#SBATCH -n1
cd ~/d2t/problems/function_minimization
conda run -n openevolve-env python ../../openevolve/openevolve-run.py initial_program.py evaluator.py --config config.yaml