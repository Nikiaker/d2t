#!/bin/bash
set -euo pipefail

: "${D2TPATH:?D2TPATH must point to the repository root}"

OUTPUT_ROOT="${OUTPUT_ROOT:-$D2TPATH/tripler/outputs/webnlg_seed_2994}"
WEBNLG_ROOT="${WEBNLG_ROOT:-$OUTPUT_ROOT/webnlg/release_v3.0/en}"
MODEL_DIR="${MODEL_DIR:-}"

sbatch --export="ALL,OUTPUT_ROOT=$OUTPUT_ROOT,WEBNLG_ROOT=$WEBNLG_ROOT,MODEL_DIR=$MODEL_DIR" \
    "$D2TPATH/tripler/finetune/scripts/batch_generate_webnlg_seed_2994.sh"
