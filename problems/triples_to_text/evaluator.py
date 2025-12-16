"""
Evaluator for the function minimization example
"""

import importlib.util
import numpy as np
import time
import concurrent.futures
import traceback
import signal
from openevolve.evaluation_result import EvaluationResult
from initial_program import Triple
from tests.benchmark_reader.benchmark_reader import Benchmark, Entry
from tests.benchmark_reader.benchmark_reader import select_files, select_test_file
from nltk.translate.bleu_score import sentence_bleu
import inspect
from dataclasses import dataclass
import os

@dataclass
class TestTriple:
    subject: str
    predicate: str
    object: str

    def __str__(self):
        return f"({self.subject} | {self.predicate} | {self.object})"

@dataclass
class TestSentence:
    triples: list[TestTriple]
    example_texts: list[str]

@dataclass
class PredicateData:
    predicate: str
    sentences: list[TestSentence]

WEBNLG_BASE_PATH = os.getenv(
    "WEBNLG_BASE_PATH",
    "./",
)
if not WEBNLG_BASE_PATH.endswith("/"):
    WEBNLG_BASE_PATH += "/"

train_files = select_files(WEBNLG_BASE_PATH + "train")
dev_files = select_files(WEBNLG_BASE_PATH + "dev")
test_dir = WEBNLG_BASE_PATH + "test"
test_file = select_test_file(test_dir, "rdf-to-text-generation-test-data-with-refs-en.xml")

train_benchmark = Benchmark()
dev_benchmark = Benchmark()
test_benchmark = Benchmark()
train_benchmark.fill_benchmark(train_files)
dev_benchmark.fill_benchmark(dev_files)
test_benchmark.fill_benchmark(test_file)

entries: list[Entry] = []
entries.extend(train_benchmark.entries)
entries.extend(dev_benchmark.entries)
entries.extend(test_benchmark.entries)

airport_entries  = [e for e in entries if e.category == "Airport"]
airport_test_sentences = [TestSentence([TestTriple(*triple) for triple in e.get_triples_tuple_list()], e.get_lexs_list()) for e in airport_entries]

def run_with_timeout(func, args=(), kwargs={}, timeout_seconds=5):
    """
    Run a function with a timeout using concurrent.futures

    Args:
        func: Function to run
        args: Arguments to pass to the function
        kwargs: Keyword arguments to pass to the function
        timeout_seconds: Timeout in seconds

    Returns:
        Result of the function or raises TimeoutError
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func, *args, **kwargs)
        try:
            result = future.result(timeout=timeout_seconds)
            return result
        except concurrent.futures.TimeoutError:
            raise TimeoutError(f"Function timed out after {timeout_seconds} seconds")


def safe_float(value):
    """Convert a value to float safely"""
    try:
        return float(value)
    except (TypeError, ValueError):
        print(f"Warning: Could not convert {value} of type {type(value)} to float")
        return 0.0


def evaluate(program_path):
    """
    Evaluate the program by running it multiple times and checking how close
    it gets to the known global minimum.

    Args:
        program_path: Path to the program file

    Returns:
        Dictionary of metrics
    """
    try:
        # Load the program
        spec = importlib.util.spec_from_file_location("program", program_path)
        program = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(program)

        # Check if the required function exists
        if not hasattr(program, "predict"):
            print(f"Error: program does not have 'predict' function")
            
            error_artifacts = {
                "error_type": "MissingFunction",
                "error_message": "Program is missing required 'predict' function",
                "suggestion": "Make sure your program includes a function named 'predict' that takes a Triple and returns a string"
            }
            
            return EvaluationResult(
                metrics={
                    "combined_score": 0.0,
                    "error": "Missing predict function",
                },
                artifacts=error_artifacts
            )

        # Check function signature and return type
        predict_sig = inspect.signature(program.predict)
        params = list(predict_sig.parameters.values())

        # Check if it accepts exactly one parameter (the Triple)
        if len(params) != 1:
            error_artifacts = {
                "error_type": "InvalidSignature",
                "error_message": "predict function must accept exactly one argument (list[Triple])",
                "suggestion": "Define predict as: def predict(triples: list[Triple]) -> str:"
            }
            return EvaluationResult(
                metrics={
                    "combined_score": 0.0,
                    "error": "Invalid function signature",
                },
                artifacts=error_artifacts
            )

        # Test with a sample triple to check return type
        try:
            test_triples = [Triple("test_subject", "test_predicate", "test_object")]
            test_result = run_with_timeout(program.predict, args=(test_triples,), timeout_seconds=2)
            if not isinstance(test_result, str):
                error_artifacts = {
                    "error_type": "InvalidReturnType",
                    "error_message": f"predict function must return str, but returned {type(test_result).__name__}",
                    "suggestion": "Make sure predict returns a string"
                }
                return EvaluationResult(
                    metrics={
                        "combined_score": 0.0,
                        "error": "Invalid return type",
                    },
                    artifacts=error_artifacts
                )
        except Exception as e:
            error_artifacts = {
                "error_type": "FunctionTestFailed",
                "error_message": f"Failed to test predict function: {str(e)}",
                "suggestion": "Ensure predict can handle a list[Triple] object as input"
            }
            return EvaluationResult(
                metrics={
                    "combined_score": 0.0,
                    "error": "Function test failed",
                },
                artifacts=error_artifacts
            )

        scores = []
        success_count = 0

        for test_sentence in airport_test_sentences:
            try:
                triples = [Triple(test_triple.subject, test_triple.predicate, test_triple.object) for test_triple in test_sentence.triples]

                # Run with timeout
                result = run_with_timeout(program.predict, args=(triples,), timeout_seconds=5)

                # Handle different result formats
                if isinstance(result, str):
                    generated_text = result
                else:
                    print(
                        f"Invalid result format, expected str but got {type(result)}"
                    )
                    continue

                # Define your desired weights (example: higher weight for bi-grams)
                weights = (0.25, 0.25)  # Weights for uni-gram, bi-gram, tri-gram, and 4-gram

                # Reference and predicted texts (same as before)
                references = [test_text.lower().split() for test_text in test_sentence.example_texts]
                prediction = generated_text.lower().split()

                # Calculate BLEU score with weights
                score = sentence_bleu(references, prediction, weights=weights)
                scores.append(score)

                success_count += 1

            except TimeoutError as e:
                print(f"Trial: {str(e)}")
                continue
            except IndexError as e:
                # Specifically handle IndexError which often happens with early termination checks
                print(f"Trial: IndexError - {str(e)}")
                print(
                    "This is likely due to a list index check before the list is fully populated."
                )
                continue
            except Exception as e:
                print(f"Trial: Error - {str(e)}")
                print(traceback.format_exc())
                continue

        # If all trials failed, return zero scores
        if success_count == 0:
            error_artifacts = {
                "error_type": "AllTrialsFailed",
                "error_message": f"All trials failed - common issues: timeouts, crashes, or invalid return values",
                "suggestion": "Check for infinite loops, ensure function returns a str"
            }
            
            return EvaluationResult(
                metrics={
                    "combined_score": 0.0,
                    "error": "All trials failed",
                },
                artifacts=error_artifacts
            )

        # Calculate metrics
        avg_value = float(np.mean(scores))
        combined_score = avg_value

        return EvaluationResult(
            metrics={
                "combined_score": combined_score,
            },
        )
    except Exception as e:
        print(f"Evaluation failed completely: {str(e)}")
        print(traceback.format_exc())
        
        # Create error artifacts
        error_artifacts = {
            "error_type": type(e).__name__,
            "error_message": str(e),
            "full_traceback": traceback.format_exc(),
            "suggestion": "Check for syntax errors or missing imports in the generated code"
        }
        
        return EvaluationResult(
            metrics={
                "value_score": 0.0,
                "distance_score": 0.0,
                "reliability_score": 0.0,
                "combined_score": 0.0,
                "error": str(e),
            },
            artifacts=error_artifacts
        )
    