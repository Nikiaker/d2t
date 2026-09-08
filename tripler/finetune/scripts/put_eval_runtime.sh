#!/bin/bash

# Runtime setup for PUT/HGX evaluation jobs. Conda is intentionally used via
# `conda run`: batch shells do not need (and should not use) `conda activate`.
put_eval_setup() {
    local job_id="${SLURM_JOB_ID:-$$}"
    export PUT_EVAL_ROOT="${PUT_EVAL_ROOT:-/raid/${USER}/d2t-eval-${job_id}}"

    mkdir -p "$PUT_EVAL_ROOT/tmp" "$PUT_EVAL_ROOT/cache" "$PUT_EVAL_ROOT/models" \
        "$PUT_EVAL_ROOT/logs" || {
        echo "ERROR: cannot create PUT runtime directory: $PUT_EVAL_ROOT" >&2
        return 1
    }

    export TMPDIR="${PUT_EVAL_TMPDIR:-$PUT_EVAL_ROOT/tmp}"
    export XDG_CACHE_HOME="${PUT_EVAL_CACHE:-$PUT_EVAL_ROOT/cache}"
    export VLLM_CACHE_ROOT="$PUT_EVAL_ROOT/cache/vllm"
    export CUDA_CACHE_PATH="$PUT_EVAL_ROOT/cache/cuda"
    export TRITON_CACHE_DIR="$PUT_EVAL_ROOT/cache/triton"
    export TORCHINDUCTOR_CACHE_DIR="$PUT_EVAL_ROOT/cache/torchinductor"
    mkdir -p "$XDG_CACHE_HOME" "$VLLM_CACHE_ROOT" "$CUDA_CACHE_PATH" \
        "$TRITON_CACHE_DIR" "$TORCHINDUCTOR_CACHE_DIR"
}

put_conda_run() {
    local attempt=1
    local retries="${PUT_CONDA_RETRIES:-3}"
    local delay="${PUT_CONDA_RETRY_DELAY:-10}"

    while true; do
        conda run "$@" && return 0
        if [ "$attempt" -ge "$retries" ]; then
            return 1
        fi
        echo "WARNING: conda run failed (attempt $attempt/$retries); retrying in ${delay}s" >&2
        sleep "$delay"
        attempt=$((attempt + 1))
    done
}

put_vllm_run() {
    if [ -z "${PUT_VLLM_ENV_PREFIX:-}" ]; then
        echo "ERROR: PUT_VLLM_ENV_PREFIX is not initialized" >&2
        return 1
    fi
    put_conda_run -n vllm-env env \
        "LD_LIBRARY_PATH=$PUT_VLLM_ENV_PREFIX/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" "$@"
}

put_finetune_setup() {
    local job_id="${SLURM_JOB_ID:-$$}"
    export PUT_FINETUNE_ROOT="${PUT_FINETUNE_ROOT:-/raid/${USER}/d2t-finetune-${job_id}}"

    mkdir -p "$PUT_FINETUNE_ROOT/tmp" "$PUT_FINETUNE_ROOT/cache" \
        "$PUT_FINETUNE_ROOT/datasets" "$PUT_FINETUNE_ROOT/runs" \
        "$PUT_FINETUNE_ROOT/models" || {
        echo "ERROR: cannot create PUT finetune directory: $PUT_FINETUNE_ROOT" >&2
        return 1
    }

    export TMPDIR="${PUT_FINETUNE_TMPDIR:-$PUT_FINETUNE_ROOT/tmp}"
    export XDG_CACHE_HOME="${PUT_FINETUNE_CACHE:-$PUT_FINETUNE_ROOT/cache}"
    export HF_HOME="${PUT_FINETUNE_HF_HOME:-$PUT_FINETUNE_ROOT/cache/huggingface}"
    export TRANSFORMERS_CACHE="$HF_HOME"
    export TORCH_HOME="$PUT_FINETUNE_ROOT/cache/torch"
    export CUDA_CACHE_PATH="$PUT_FINETUNE_ROOT/cache/cuda"
    export TRITON_CACHE_DIR="$PUT_FINETUNE_ROOT/cache/triton"
    export TORCHINDUCTOR_CACHE_DIR="$PUT_FINETUNE_ROOT/cache/torchinductor"
    mkdir -p "$XDG_CACHE_HOME" "$HF_HOME" "$TORCH_HOME" "$CUDA_CACHE_PATH" \
        "$TRITON_CACHE_DIR" "$TORCHINDUCTOR_CACHE_DIR"
}

put_finetune_run() {
    if [ -z "${PUT_FINETUNE_ENV_PREFIX:-}" ]; then
        echo "ERROR: PUT_FINETUNE_ENV_PREFIX is not initialized" >&2
        return 1
    fi
    put_conda_run -n finetune-env env \
        "LD_LIBRARY_PATH=$PUT_FINETUNE_ENV_PREFIX/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" "$@"
}

put_finetune_check_conda() {
    if ! command -v conda >/dev/null 2>&1 && [ -x "$HOME/miniconda3/bin/conda" ]; then
        export PATH="$HOME/miniconda3/bin:$PATH"
    fi
    command -v conda >/dev/null 2>&1 || {
        echo "ERROR: conda is not available in PATH; PUT jobs use 'conda run' directly" >&2
        return 1
    }
    PUT_FINETUNE_ENV_PREFIX="$(put_conda_run -n finetune-env python -c 'import sys; print(sys.prefix)')" || {
        echo "ERROR: cannot determine finetune-env prefix; check the PUT /home filesystem" >&2
        return 1
    }
    export PUT_FINETUNE_ENV_PREFIX
    test -f "$PUT_FINETUNE_ENV_PREFIX/lib/libstdc++.so.6" || {
        echo "ERROR: finetune-env has no libstdc++.so.6 under $PUT_FINETUNE_ENV_PREFIX/lib" >&2
        return 1
    }
    put_finetune_run python -c 'import torch; print(torch.__version__)' || {
        echo "ERROR: finetune-env cannot import PyTorch with its Conda C++ runtime" >&2
        return 1
    }
    put_finetune_run python -c 'import transformers, datasets, peft, trl; print("finetune imports successfully")' || {
        echo "ERROR: finetune-env cannot import the training dependencies" >&2
        return 1
    }
}

put_publish_dir() {
    local source="$1"
    local target="$2"

    test -e "$source" || {
        echo "ERROR: artifact does not exist: $source" >&2
        return 1
    }
    mkdir -p "$(dirname "$target")" || return 1
    if [ -d "$source" ]; then
        mkdir -p "$target" || return 1
        if command -v rsync >/dev/null 2>&1; then
            rsync -a --delete "$source/" "$target/"
        else
            cp -a "$source/." "$target/"
        fi
    else
        cp -f "$source" "$target"
    fi || {
        echo "ERROR: failed to publish artifact $source to $target" >&2
        return 1
    }
}

put_finetune_cleanup() {
    if [ -n "${PUT_FINETUNE_ROOT:-}" ] && [[ "$PUT_FINETUNE_ROOT" == /raid/* ]]; then
        rm -rf -- "$PUT_FINETUNE_ROOT"
    fi
}

put_eval_check_conda() {
    if ! command -v conda >/dev/null 2>&1 && [ -x "$HOME/miniconda3/bin/conda" ]; then
        export PATH="$HOME/miniconda3/bin:$PATH"
    fi
    command -v conda >/dev/null 2>&1 || {
        echo "ERROR: conda is not available in PATH; PUT jobs use 'conda run' directly" >&2
        return 1
    }
    PUT_VLLM_ENV_PREFIX="$(put_conda_run -n vllm-env python -c 'import sys; print(sys.prefix)')" || {
        echo "ERROR: cannot determine vllm-env prefix; check the PUT /home filesystem" >&2
        return 1
    }
    export PUT_VLLM_ENV_PREFIX
    test -f "$PUT_VLLM_ENV_PREFIX/lib/libstdc++.so.6" || {
        echo "ERROR: vllm-env has no libstdc++.so.6 under $PUT_VLLM_ENV_PREFIX/lib" >&2
        return 1
    }
    put_vllm_run python -c 'import optree, vllm; print("vLLM imports successfully")' || {
        echo "ERROR: vllm-env cannot import vLLM with its Conda C++ runtime" >&2
        return 1
    }
    put_conda_run -n vllm-env python -c 'import sys; print(sys.executable)' >/dev/null || {
        echo "ERROR: vllm-env cannot start Python; check the PUT /home filesystem" >&2
        return 1
    }
    put_conda_run -n openevolve-env python -c 'import sys; print(sys.executable)' >/dev/null || {
        echo "ERROR: openevolve-env cannot start Python; check the PUT /home filesystem" >&2
        return 1
    }
}

put_stage_model() {
    local source="$1"
    local target="$PUT_EVAL_ROOT/models/$(basename "$source")"

    test -d "$source" || {
        echo "ERROR: merged model directory does not exist: $source" >&2
        return 1
    }
    mkdir -p "$target" || return 1
    if command -v rsync >/dev/null 2>&1; then
        rsync -a --delete "$source/" "$target/"
    else
        cp -a "$source/." "$target/"
    fi || {
        echo "ERROR: failed to stage $source on local /raid" >&2
        return 1
    }
    printf '%s\n' "$target"
}

put_eval_log_path() {
    printf '%s/logs/%s.log\n' "$PUT_EVAL_ROOT" "$1"
}

put_eval_cleanup() {
    if [ -n "${PUT_EVAL_ROOT:-}" ] && [[ "$PUT_EVAL_ROOT" == /raid/* ]]; then
        if [ -n "${PUT_EVAL_LOG_SOURCE:-}" ] && [ -n "${PUT_EVAL_LOG_DEST:-}" ] && \
            [ -f "$PUT_EVAL_LOG_SOURCE" ]; then
            mkdir -p "$(dirname "$PUT_EVAL_LOG_DEST")" 2>/dev/null || true
            cp "$PUT_EVAL_LOG_SOURCE" "$PUT_EVAL_LOG_DEST" 2>/dev/null || true
        fi
        rm -rf -- "$PUT_EVAL_ROOT"
    fi
}
