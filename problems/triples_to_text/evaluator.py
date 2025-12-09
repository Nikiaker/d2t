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
from tests.benchmark_reader.benchmark_reader import Benchmark
from tests.benchmark_reader.benchmark_reader import select_files
from nltk.translate.bleu_score import sentence_bleu

b = Benchmark()
files = select_files("/home/inf151915/d2t/problems/triples_to_text/tests/webnlg/release_v3.0/en/train")
b.fill_benchmark(files)
validation_set = [(e.get_triples_tuple_list()[0], e.get_lexs_list()) for e in b.entries if e.category == "Airport" and e.shape == "(X (X))"]
validation_set = [(Triple(*t[0]), t[1]) for t in validation_set]

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

        scores = []
        success_count = 0
        best_bleu = 0.0
        best_triple = Triple("", "", "")
        best_generated = ""
        best_actual = ""

        for triple, test_texts in validation_set:
            try:
                # Run with timeout
                result = run_with_timeout(program.predict, args=(triple,), timeout_seconds=5)

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
                reference = [test_text.lower().split() for test_text in test_texts]
                predictions = generated_text.lower().split()

                # Calculate BLEU score with weights
                score = sentence_bleu(reference, predictions, weights=weights)
                scores.append(score)

                if score > best_bleu:
                    best_bleu = score
                    best_triple = triple
                    best_generated = generated_text
                    best_actual = test_texts

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

        # Add artifacts for successful runs
        artifacts = {
            "best_score": f"Best BLEU score: {best_bleu:.4f}",
            "best_triple": f"({best_triple.subject}, {best_triple.predicate}, {best_triple.object})",
            "best_generated_text": f"{best_generated}",
            "best_actual_text": f"{best_actual}",
        }

        return EvaluationResult(
            metrics={
                "combined_score": combined_score,
            },
            artifacts=artifacts
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
    