# LLM Agents Implement an NLG System from Scratch: Building Interpretable Rule-Based RDF-to-Text Generators

This is the code repository for our EMNLP 2025 paper:
  
    @inproceedings{lango-dusek-2025-llm,
        title = "{LLM} Agents Implement an {NLG} System from Scratch: Building Interpretable Rule-Based {RDF}-to-Text Generators",
        author = "Lango, Mateusz  and
          Dusek, Ondrej",
        editor = "Potdar, Saloni  and
          Rojas-Barahona, Lina  and
          Montella, Sebastien",
        booktitle = "Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing: Industry Track",
        month = nov,
        year = "2025",
        address = "Suzhou (China)",
        publisher = "Association for Computational Linguistics",
        url = "https://aclanthology.org/2025.emnlp-industry.142/",
        doi = "10.18653/v1/2025.emnlp-industry.142",
        pages = "2025--2040",
        ISBN = "979-8-89176-333-3",
        abstract = "We present a novel neurosymbolic framework for RDF-to-text generation, in which the model is ``trained'' through collaborative interactions among multiple LLM agents rather than traditional backpropagation. The LLM agents produce rule-based Python code for a generator for the given domain, based on RDF triples only, with no in-domain human reference texts. The resulting system is fully interpretable, requires no supervised training data, and generates text nearly instantaneously using only a single CPU. Our experiments on the WebNLG and OpenDialKG data show that outputs produced by our approach reduce hallucination, with only slight fluency penalties compared to finetuned or prompted language models."
    }

## Content
The training checkpoints of NLG systems can be found in `chpt-programs/`. The checkpoints for each dataset and LLM are placed in separate directories. The code is available in `src/`. The main file is `idea_trainer.py`, which contains the main training pipeline. The `evaluate_program.py` file contains the implementation of the metrics used in our experiments, and `test_eng.py` contains the implementation of Test Engineer.

### Inference 
See notebook `src/showcase.ipynb` for the code to run our NLG systems


## Acknowledgements
This work was co-funded by the European Union (ERC, NG-NLG, 101039303).

<img src="LOGO_ERC-FLAG_FP.png" alt="erc-logo" height="150"/>
