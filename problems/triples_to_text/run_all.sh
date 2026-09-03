WRITTENWORK=$(sbatch $D2TPATH/problems/triples_to_text/outputs/3_sm1ifenp_500/WrittenWork_output/WrittenWork.sh)
BUILDING=$(sbatch $D2TPATH/problems/triples_to_text/outputs/3_sm1ifenp_500/Building_output/Building.sh)
FOOD=$(sbatch $D2TPATH/problems/triples_to_text/outputs/3_sm1ifenp_500/Food_output/Food.sh)

sbatch --dependency="afterok:$WRITTENWORK:$BUILDING:$FOOD" $D2TPATH/problems/triples_to_text/batch_evaluate_all_plgrid.sh