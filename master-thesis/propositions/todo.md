[v] define what are "raw structured instances"
[v] add footnote that I do not use JSON schema definition but simplified structure with placeholders for readability reasons
[v] add the full prompt in appendix and reference it wherever there are mentions of prompts
[v] what is a Union-Find structure? It is not definied anywhere in the text
[v] what is a singleton class?
[v] "previously seen round signature" not sure what it means
[v] "{equivalent, confidence, reason}" is undeifned and ambiguous
[v] the problem with rules iterative refinment and naming them rules is that in the ML/NLP world rules are very strict "if" statements. Whereas in this case the rules are more like "guidelines". Change the naming "rules" to something different
[v] what are the "previous values for any empty field". In step 1 no previous values were mentioned
[v] "{possible, reason, rule_gaps}" is undefined.
[v] "the four-field rules schema" not sure what schema it is
[v] the prompt names could be highlighted using a verbatim

[] describe what is quintd
[] describe the datasets (gsmarena, openweather, owid, wikidata)
[] maybe move the definition of raw structured instances to overview where I explain quintd
[] describe the general overview and ideas of the methods we will use to convert the data to triples

[] in 3.2 explain the general idea of the pipeline (raw data to text references then to triples)
[] in 3.2 explain that we use vLLM for model inference, and that we use gemma4 31b

[] in 3.3.1 when explaining LORA, explain what are the variables: d, k, alfa, r, k, R, h
[] some reference to base supervised fine tuning is needed
[] "a quantization datatype that is information-theoretically optimal for normally distributed weights" where did you get that information? some reference?
[] add an appendix for the prompts mentioned in 3.3.2
[] in 3.3.3 present the qlora parameters in a more graphical way. e.g use a list or a table
[] don't mention that we use a merge_and_unload operation, because the reader knows nothing what it is. Instead explain what that operation does.