# EVOLVE-BLOCK-START
"""Function minimization example for OpenEvolve"""
import numpy as np


def search_algorithm(iterations=1000, bounds=(-5, 5)):
    """
    A simple random search algorithm that often gets stuck in local minima.

    Args:
        iterations: Number of iterations to run
        bounds: Bounds for the search space (min, max)

    Returns:
        Tuple of (best_x, best_y, best_value)
    """
    # Initialize with a random point
    best_x = np.random.uniform(bounds[0], bounds[1])
    best_y = np.random.uniform(bounds[0], bounds[1])
    best_value = evaluate_function(best_x, best_y)
    temperature = 1.0
    # Adaptive cooling schedule
    cooling_rate = 0.95 + 0.05 * np.random.uniform(0, 1)
    # Alternatively, use an exponential cooling schedule
    # cooling_schedule = lambda t: 0.95 ** t

    for _ in range(iterations):
        # With a certain probability, perturb the current best solution
        if np.random.uniform(0, 1) < 0.1:
            x = best_x + np.random.uniform(-0.1, 0.1)
            y = best_y + np.random.uniform(-0.1, 0.1)
            # Ensure the perturbed point is within the bounds
            x = max(bounds[0], min(x, bounds[1]))
            y = max(bounds[0], min(y, bounds[1]))
        else:
            # Generate a new random point within the bounds
            x = np.random.uniform(bounds[0], bounds[1])
            y = np.random.uniform(bounds[0], bounds[1])
        value = evaluate_function(x, y)

        # Calculate the difference in value
        delta = value - best_value

        # If the new point is better, update the best point
        if delta < 0:
            best_value = value
            best_x, best_y = x, y
        # If the new point is worse, update the best point with a certain probability
        elif np.exp(-delta / temperature) > np.random.uniform(0, 1):
            best_value = value
            best_x, best_y = x, y

        # Decrease the temperature
        temperature *= cooling_rate

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
