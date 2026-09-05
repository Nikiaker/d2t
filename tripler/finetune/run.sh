# finetune
GSM_ARENA_JOB=$(sbatch --parsable "$D2TPATH/tripler/finetune/scripts/batch_finetune_gsmarena.sh")
OPENWEATHER_JOB=$(sbatch --parsable "$D2TPATH/tripler/finetune/scripts/batch_finetune_openweather.sh")
OWID_JOB=$(sbatch --parsable "$D2TPATH/tripler/finetune/scripts/batch_finetune_owid.sh")
WIKIDATA_JOB=$(sbatch --parsable "$D2TPATH/tripler/finetune/scripts/batch_finetune_wikidata.sh")

# evaluate
sbatch --dependency="afterok:$GSM_ARENA_JOB" "$D2TPATH/tripler/finetune/scripts/batch_eval_gsmarena.sh"
sbatch --dependency="afterok:$OPENWEATHER_JOB" "$D2TPATH/tripler/finetune/scripts/batch_eval_openweather.sh"
sbatch --dependency="afterok:$OWID_JOB" "$D2TPATH/tripler/finetune/scripts/batch_eval_owid.sh"
sbatch --dependency="afterok:$WIKIDATA_JOB" "$D2TPATH/tripler/finetune/scripts/batch_eval_wikidata.sh"

# evaluate (no depenedency)
sbatch "$D2TPATH/tripler/finetune/scripts/batch_eval_gsmarena.sh"
sbatch "$D2TPATH/tripler/finetune/scripts/batch_eval_openweather.sh"
sbatch "$D2TPATH/tripler/finetune/scripts/batch_eval_owid.sh"
sbatch "$D2TPATH/tripler/finetune/scripts/batch_eval_wikidata.sh"