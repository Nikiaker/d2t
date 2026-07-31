Abstract - about generating triples from data downloaded using quintd, using those triples in AlphaEvolve (OpenEvolve) and WebNLG to create programs. Saying what the results are.

Table of contents

1. Introduction
1.1 Motivation
1.2 Thesis structure

2. Data-to-Text Generation
2.1 Problem definition
2.2 Methods
2.2 Interpretable D2T Approaches
2.3 Performance Evaluation

3. Building interpretable meaning representations from complex data
3.1 Method Overview
3.2 Data conversion with LLMs - We use quintd to get data from the internet in the form of structured json and xml. We then used different "pipelines" to convert these data to RDF triples.
3.3 Fine-tuned model for data conversion

4. Surface realization - evolving programs using AlphaEvolve
4.1 Modern approaches for writing complex programs(AlphaEvolve, OpenEvolve)
4.2 Methods overview
4.2 OpenEvolve
4.3 Program database
4.4 Prompt and selection
4.5 Evaluation

5. Experiments
5.1 Meaning representation
5.2 Surface realization
5.3 Whole system evaluation

6. Discussion

7. Summary