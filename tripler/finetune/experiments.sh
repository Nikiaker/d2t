#!/bin/bash

# Set the training knobs shared by all domain batch scripts.
configure_experiment() {
    local experiment="$1"

    case "$experiment" in
        baseline)
            TRAIN_EPOCHS=3
            TRAIN_LR=1e-4
            TRAIN_WARMUP_RATIO=0.03
            TRAIN_LORA_R=16
            TRAIN_LORA_ALPHA=32
            TRAIN_LORA_DROPOUT=0.05
            TRAIN_WEIGHT_DECAY=0.0
            ;;
        low_lr)
            TRAIN_EPOCHS=5
            TRAIN_LR=3e-5
            TRAIN_WARMUP_RATIO=0.05
            TRAIN_LORA_R=16
            TRAIN_LORA_ALPHA=32
            TRAIN_LORA_DROPOUT=0.05
            TRAIN_WEIGHT_DECAY=0.01
            ;;
        higher_capacity)
            TRAIN_EPOCHS=3
            TRAIN_LR=5e-5
            TRAIN_WARMUP_RATIO=0.05
            TRAIN_LORA_R=32
            TRAIN_LORA_ALPHA=64
            TRAIN_LORA_DROPOUT=0.05
            TRAIN_WEIGHT_DECAY=0.01
            ;;
        regularized_capacity)
            TRAIN_EPOCHS=5
            TRAIN_LR=3e-5
            TRAIN_WARMUP_RATIO=0.10
            TRAIN_LORA_R=32
            TRAIN_LORA_ALPHA=64
            TRAIN_LORA_DROPOUT=0.10
            TRAIN_WEIGHT_DECAY=0.01
            ;;
        baseline-1epoch)
            TRAIN_EPOCHS=1
            TRAIN_LR=1e-4
            TRAIN_WARMUP_RATIO=0.03
            TRAIN_LORA_R=16
            TRAIN_LORA_ALPHA=32
            TRAIN_LORA_DROPOUT=0.05
            TRAIN_WEIGHT_DECAY=0.0
            ;;
        *)
            echo "ERROR: unknown experiment '$experiment'" >&2
            echo "Valid experiments: baseline low_lr higher_capacity regularized_capacity" >&2
            return 1
            ;;
    esac

    export TRAIN_EPOCHS TRAIN_LR TRAIN_WARMUP_RATIO
    export TRAIN_LORA_R TRAIN_LORA_ALPHA TRAIN_LORA_DROPOUT TRAIN_WEIGHT_DECAY
}
