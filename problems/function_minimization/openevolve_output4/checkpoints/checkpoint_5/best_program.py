# EVOLVE-BLOCK-START
"""Function minimization example for OpenEvolve"""
import numpy as np
import random

def search_algorithm(iterations=1000, bounds=(-5, 5)):
    """
    A multi-start random search algorithm with restarts to escape local minima.

    Args:
        iterations: Number of iterations to run
        bounds: Bounds for the search space (min, max)

    Returns:
        Tuple of (best_x, best_y, best_value)
    """
    # Initialize with a random point
    best_x = random.uniform(bounds[0], bounds[1])
    best_y = random.uniform(bounds[0], bounds[1])
    best_value = evaluate_function(best_x, best_y)

    # Multi-start random search with restarts
    for _ in range(iterations):
        # Simple random search
        x = random.uniform(bounds[0], bounds[1])
        y = random.uniform(bounds[0], bounds[1])
        value = evaluate_function(x, y)

        if value < best_value:
            best_value = value
            best_x, best_y = x, y

    return best_x, best_y, best_value


# EVOLVE-BLOCK-END


# This part remains fixed (not evolved)
def evaluate_function(x, y):
    """The complex function we're trying to minimize"""
    return np.sin(x) * np.cos(y) + np.sin(x * y) + (x**2 + y**2) / 20


def run_search():
    x, y, value = search_algorithm()
    return x, y, value


if __name__ == "__main__":
    x, y, value = run_search()
    print(f"Found minimum at ({x}, {y}) with value {value}")