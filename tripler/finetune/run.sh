# finetune
sbatch $D2TPATH/tripler/finetune/scripts/batch_finetune_gsmarena.sh
sbatch $D2TPATH/tripler/finetune/scripts/batch_finetune_openweather.sh
sbatch $D2TPATH/tripler/finetune/scripts/batch_finetune_owid.sh
sbatch $D2TPATH/tripler/finetune/scripts/batch_finetune_wikidata.sh

# evaluate
sbatch $D2TPATH/tripler/finetune/scripts/batch_eval_gsmarena.sh
sbatch $D2TPATH/tripler/finetune/scripts/batch_eval_openweather.sh
sbatch $D2TPATH/tripler/finetune/scripts/batch_eval_owid.sh
sbatch $D2TPATH/tripler/finetune/scripts/batch_eval_wikidata.sh