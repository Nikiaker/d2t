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
    # Run the differential evolution algorithm
    result = differential_evolution(evaluate_function, bounds, maxiter=iterations)
    best_x, best_y = result.x
    best_value = result.fun

    return best_x, best_y, best_value


def run_search():
    x, y, value = search_algorithm()
    return x, y, value


if __name__ == "__main__":
    # Run the search multiple times and keep the best result
    best_x, best_y, best_value = None, None, float('inf')
    for _ in range(10):
        x, y, value = search_algorithm()
        if value < best_value:
            best_value = value
            best_x, best_y = x, y

    # Use a more robust random number generator
    random.seed(42)

    # Increase the number of iterations
    iterations = 2000

    # Print the result
    print(f"Found minimum at ({best_x}, {best_y}) with value {best_value}")