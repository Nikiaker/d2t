# Meaning representation

## Pipelines

When looking at the transformation from data to text, an LLM as a judged has given almost perfect scores with an average of 4.966 for text summary and 4.974 for faithfulness. However when looking at human evaluation the scores are more strict with an average of 4.5 for text summary and 4.2 for text faithfulness. A visible loss is visible for the domains GSMArena and Weather forecast, where both of them recived the score of 3.6 in faitfulness. That means that according to the human evaluator, there is one major or a few minor hallucinations, fabrications, contradictions or misinterpretations in the summarized text.
Now when looking at correlations it can be seen that for the task of transforming data to text no correlations could be calculated, because of the constant values of 5 given by the LLM as a judge. So for this task we can only rely on the differences seen between the means of the LLM as a judge and the human evaluator.

Now when looking at the scores given by gemma in the task of transforming text to triples using the three methods, the best working pipeline method is Text-First Extraction with Normalization with additions and omissions getting near perfect score of an average across domains of 4.994 and 4.992 accordingly. The second best is Evolving Catalog which has scores 4.896 and 4.336 for additions and ommitions and the worst method Blueprint-Iterative Refinement has an average of 4.654 for additions and 4.056 for omissions. Notably we can see more omissions for the domain ice hockey domain and the owid domain for the Evolving Catalog pipeline with scores of 3.92 and 3.85. For Blueprint-Iterative Refinement it is ice hockey and weather forecast that get worse scores for omissions because it is 3.38 and 3.84. Additionaly ice hockey get a additions score of 3.58. The conlusion is that the Text-First Extraction with Normalization pipeline works the best and if we look at the number of unique predicates we can see why. This method has an average of 201.2 unique predicates, which gives a lot of flexibilty when construting the semantic triples. In comparison the other two methods use just 22 uqnique predicates and 44.6 which is 4 times less than the winning pipeline.
When compared with the scores of the human evaluator, we can come to the same conclusion that Text-First Extraction with Normalization is the best method, Evolving Catalog is the second best method and Rules-Iterative Refinement is the worst method. Text-First Extraction with Normalization recives almost a perfect score as well, being given 4.95 and 4.875 for additions and omissions. Evolving Catalog is also being critized for omissions with a score of 3.9. The worst domains are owid and weather forcast with scores 2.2 and 3.7. Rules-Iterative Refinement has more ommisions because it is the score of 3.825.
Again, the correlations for Text-First Extraction with Normalization could not be caluclated because both LLM as a judge and the human evalator have given perfect scores. But for Evolving Catalog we can look at the omissions and we can see a correlation score of 0.67 for Pearson, Spearman and Kendall. As for Rules-Iterative Refinement only GSMArena has calculated correlations for additions with the result being negatively correlated with the score of -0.5 for Pearson, Spearman and Kendall. The rest of the domains have scores for omissions ranging from 0.51 to 0.67.

The overall conlusion is that the best method is Text-First Extraction with Normalization and the correlation proves that the LLM as a judge scores can be generally trusted.

## Fine-tuned LLM

Starting with the base Gemma model it does very poorly in the task of creating triples+references from raw data. The f1 scores is 0.0205. The baseline with just one epoch already improves the model by raising the f1 score to 0.1209. Increasing it to 3 epochs gets the f1 score to 0.2340. The regularized capacity setup which increases the hyperparameters warmup r α Dropout Weight decay gets f1 of 0.2239, which is slightly worse than the 3 epochs method, but improves blue and memetor.

One best fine-tuned model cannot be objectively selected, because they work better or worse for different domains.

# Surface realization

From the initial test it can be seen that easiest method is Written Work and that the worst method is Food. (write why that ma be. the domain is difficult maybe?). Then acording to BLUE and BLEURT scores the best method is the method with BLUE score evaluation and no inspirations that use gemma4 31B. However when we look at the LLM as a judge evaluations the best methods would be the ones using LLM as a judge for evaluation. They also make no additions and omissions.

The conclusion is that using no inspirations improves the BLUE and BLEURT metrics. Using LLM as a judge improves the judges scores and reduces additions and omittions.

Compared with the baseline methods the advantage is that we get the interpretability that the Fine-tuned BART and LLM prompt don't have and we get better scores than the Rule-based generator. We also get 0 additions and omission when compared with Rule-based generator and Fine-tuned BART. However a zero-shot LLM prompt still remains superior when it comes to scores. The simplicity of just making a prompt also outweighs the complexity and cost of the methods used to create the surface realization. However these this system has allowed us to create an interpretable program that can be inspected and changed.

# Full system evaluation

(still awaiting results)