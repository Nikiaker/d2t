# EVOLVE-BLOCK-START
"""Function minimization example for OpenEvolve"""
import numpy as np


def search_algorithm(iterations=1000, bounds=(-5, 5)):
    """
    An improved random search algorithm with simulated annealing and genetic algorithm to escape local minima.

    Args:
        iterations: Number of iterations to run
        bounds: Bounds for the search space (min, max)

    Returns:
        Tuple of (best_x, best_y, best_value)
    """
    population_size = 100
    population = np.random.uniform(bounds[0], bounds[1], size=(population_size, 2))
    best_x, best_y = population[0]
    best_value = evaluate_function(best_x, best_y)
    temperature = 1.0
    cooling_rate = 0.99
    mutation_rate = 0.1

    for _ in range(iterations):
        # Evaluate population
        values = np.array([evaluate_function(x, y) for x, y in population])

        # Select parents
        parents = np.array([population[np.argmin(values)]])
        while len(parents) < population_size // 2:
            idx = np.argmin(values)
            parents = np.vstack((parents, population[idx]))
            values[idx] = np.inf

        # Crossover
        offspring = np.zeros_like(population)
        for i in range(population_size):
            if i < population_size // 2:
                offspring[i] = parents[i % len(parents)]
            else:
                parent1, parent2 = parents[np.random.choice(len(parents), size=2, replace=False)]
                offspring[i] = (parent1 + parent2) / 2

        # Mutate
        for i in range(population_size):
            if np.random.rand() < mutation_rate:
                offspring[i] += np.random.uniform(-1, 1, size=2)

        # Ensure bounds are respected
        offspring = np.clip(offspring, bounds[0], bounds[1])

        # Evaluate offspring
        values = np.array([evaluate_function(x, y) for x, y in offspring])

        # Select best
        idx = np.argmin(values)
        if values[idx] < best_value:
            best_value = values[idx]
            best_x, best_y = offspring[idx]

        # Replace population
        population = offspring

        # Cool down temperature
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