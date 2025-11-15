# EVOLVE-BLOCK-START
"""Function minimization example for OpenEvolve"""
import numpy as np
import random
from scipy.optimize import differential_evolution

def evaluate_function(x):
    """The complex function we're trying to minimize"""
    return np.sin(x[0]) * np.cos(x[1]) + np.sin(x[0] * x[1]) + (x[0]**2 + x[1]**2) / 20


def search_algorithm(bounds=((-5, 5), (-5, 5)), iterations=1000):
    """
    A differential evolution algorithm to find the global minimum.

    Args:
        bounds: Bounds for the search space (min, max)
        iterations: Number of iterations to run

    Returns:
        Tuple of (best_x, best_y, best_value)
    """
    # Run the differential evolution algorithm with multiple restarts
    # to improve the chances of finding the global minimum
    num_restarts = 5
    results = []
    for _ in range(num_restarts):
        result = differential_evolution(evaluate_function, bounds, maxiter=iterations)
        results.append(result)

    # Combine the results and select the best one
    best_result = min(results, key=lambda result: result.fun)
    best_x, best_y = best_result.x
    best_value = best_result.fun

    return best_x, best_y, best_value


# EVOLVE-BLOCK-END


# This part remains fixed (not evolved)
def run_search():
    x, y, value = search_algorithm()
    return x, y, value


if __name__ == "__main__":
    # Run the search
    x, y, value = run_search()

    # Print the result
    print(f"Found minimum at ({x}, {y}) with value {value}")