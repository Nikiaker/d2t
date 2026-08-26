#!/bin/bash
set -eo pipefail

EXPERIMENTS=(low_lr higher_capacity regularized_capacity)
DOMAINS=(gsmarena openweather owid wikidata)

for experiment in "${EXPERIMENTS[@]}"; do
    case "$experiment" in
        low_lr) experiment_offset=0 ;;
        higher_capacity) experiment_offset=1 ;;
        regularized_capacity) experiment_offset=2 ;;
        *) echo "ERROR: unsupported experiment '$experiment'" >&2; exit 1 ;;
    esac

    for domain in "${DOMAINS[@]}"; do
        case "$domain" in
            gsmarena) domain_port=3100 ;;
            openweather) domain_port=3110 ;;
            owid) domain_port=3120 ;;
            wikidata) domain_port=3130 ;;
            *) echo "ERROR: unsupported domain '$domain'" >&2; exit 1 ;;
        esac

        finetune_script="$D2TPATH/tripler/finetune/scripts/batch_finetune_${domain}.sh"
        eval_script="$D2TPATH/tripler/finetune/scripts/batch_eval_${domain}.sh"
        port=$((domain_port + experiment_offset))

        finetune_job=$(sbatch --parsable --export="ALL,EXPERIMENT=$experiment" "$finetune_script")
        sbatch --dependency="afterok:$finetune_job" \
            --export="ALL,EXPERIMENT=$experiment,PORT=$port" "$eval_script"
    done
done
