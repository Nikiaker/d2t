# EVOLVE-BLOCK-START
"""Function minimization example for OpenEvolve"""
import numpy as np
from scipy.optimize import differential_evolution


def search_algorithm(iterations=1000, bounds=[(-5, 5), (-5, 5)]):
    """
    An improved global optimization algorithm using differential evolution to escape local minima.

    Args:
        iterations: Number of iterations to run
        bounds: Bounds for the search space (min, max)

    Returns:
        Tuple of (best_x, best_y, best_value)
    """
    result = differential_evolution(evaluate_function, bounds, x0=[1, 1], polish=True, maxiter=iterations)
    return result.x[0], result.x[1], result.fun


# EVOLVE-BLOCK-END


# This part remains fixed (not evolved)
def evaluate_function(point):
    """The complex function we're trying to minimize"""
    x, y = point
    return np.sin(x) * np.cos(y) + np.sin(x * y) + (x**2 + y**2) / 20


def run_search():
    x, y, value = search_algorithm()
    return x, y, value


if __name__ == "__main__":
    x, y, value = run_search()
    print(f"Found minimum at ({x}, {y}) with value {value}")