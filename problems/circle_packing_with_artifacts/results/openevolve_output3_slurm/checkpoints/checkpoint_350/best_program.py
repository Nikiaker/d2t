# EVOLVE-BLOCK-START
"""Constructor-based circle packing for n=26 circles"""
import numpy as np


def construct_packing():
    """
    Construct a specific arrangement of 26 circles in a unit square
    that attempts to maximize the sum of their radii.

    Returns:
        Tuple of (centers, radii, sum_of_radii)
        centers: np.array of shape (26, 2) with (x, y) coordinates
        radii: np.array of shape (26) with radius of each circle
        sum_of_radii: Sum of all radii
    """
    n = 26
    centers = np.zeros((n, 2))
    radii = np.zeros(n)

    # Initial placement - more structured, aiming for density
    rows = 5
    cols = 6  # Adjusted to get closer to 26
    for i in range(n):
        row = i // cols
        col = i % cols
        x = (col + 0.5) / cols
        y = (row + 0.5) / rows
        centers[i] = [x, y]

    # Add some random perturbation to initial positions, scaled by distance from center
    perturbation = 0.03
    for i in range(n):
        dist_from_center = np.sqrt((centers[i][0] - 0.5)**2 + (centers[i][1] - 0.5)**2)
        centers[i] += (perturbation * dist_from_center * np.random.rand(2) - perturbation * dist_from_center / 2)
    centers = np.clip(centers, 0.01, 0.99)

    # Compute radii based on distance to other circles and boundaries
    radii = compute_max_radii(centers)

    sum_radii = np.sum(radii)

    return centers, radii, sum_radii


def compute_max_radii(centers):
    """
    Compute the maximum possible radii for each circle position
    such that they don't overlap and stay within the unit square.
    """
    n = centers.shape[0]
    radii = np.ones(n) * 0.03  # Initialize with a small radius

    # Limit by distance to square borders
    for i in range(n):
        x, y = centers[i]
        radii[i] = min(x, y, 1 - x, 1 - y)

    # Iterative refinement with more iterations and a smaller buffer
    for _ in range(250):
        for i in range(n):
            for j in range(i + 1, n):
                dist = np.sqrt(np.sum((centers[i] - centers[j]) ** 2))
                if radii[i] + radii[j] > dist:
                    # Adjust radii proportionally
                    scale = (dist - 0.000001) / (radii[i] + radii[j])  # Smaller buffer
                    if scale > 0:
                        radii[i] *= scale
                        radii[j] *= scale

    # Further refinement: try to increase radii slightly if possible
    for i in range(n):
        max_radius = radii[i]
        x, y = centers[i]
        max_radius = min(max_radius, x, y, 1 - x, 1 - y)

        for j in range(n):
            if i != j:
                dist = np.sqrt(np.sum((centers[i] - centers[j]) ** 2))
                max_radius = min(max_radius, (dist - radii[j]))

        radii[i] = max_radius

    # Additional refinement: increase radii if possible without violating constraints
    for i in range(n):
        increase = 0.0003
        while True:
            new_radius = radii[i] + increase
            valid = True
            if new_radius > min(centers[i][0], centers[i][1], 1 - centers[i][0], 1 - centers[i][1]):
                valid = False
            for j in range(n):
                if i != j:
                    dist = np.sqrt(np.sum((centers[i] - centers[j]) ** 2))
                    if new_radius + radii[j] > dist:
                        valid = False
                        break
            if valid:
                radii[i] = new_radius
                increase *= 1.04
            else:
                break

    #Final refinement: try to increase radii based on average radius
    avg_radius = np.mean(radii)
    for i in range(n):
        increase = 0.00015
        while True:
            new_radius = radii[i] + increase
            valid = True
            if new_radius > min(centers[i][0], centers[i][1], 1 - centers[i][0], 1 - centers[i][1]):
                valid = False
            for j in range(n):
                if i != j:
                    dist = np.sqrt(np.sum((centers[i] - centers[j]) ** 2))
                    if new_radius + radii[j] > dist:
                        valid = False
                        break
            if valid and new_radius < avg_radius * 1.1:
                radii[i] = new_radius
                increase *= 1.03
            else:
                break
    
    # Attempt to further refine by increasing radii based on a smaller increase factor
    for i in range(n):
        increase = 0.0001
        while True:
            new_radius = radii[i] + increase
            valid = True
            if new_radius > min(centers[i][0], centers[i][1], 1 - centers[i][0], 1 - centers[i][1]):
                valid = False
            for j in range(n):
                if i != j:
                    dist = np.sqrt(np.sum((centers[i] - centers[j]) ** 2))
                    if new_radius + radii[j] > dist:
                        valid = False
                        break
            if valid:
                radii[i] = new_radius
                increase *= 1.02  # Smaller increase factor
            else:
                break

    return radii


# EVOLVE-BLOCK-END


# This part remains fixed (not evolved)
def run_packing():
    """Run the circle packing constructor for n=26"""
    centers, radii, sum_radii = construct_packing()
    return centers, radii, sum_radii


def visualize(centers, radii):
    """
    Visualize the circle packing

    Args:
        centers: np.array of shape (n, 2) with (x, y) coordinates
        radii: np.array of shape (n) with radius of each circle
    """
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle

    fig, ax = plt.subplots(figsize=(8, 8))

    # Draw unit square
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("equal")
    ax.grid(True)

    # Draw circles
    for i, (center, radius) in enumerate(zip(centers, radii)):
        circle = Circle(center, radius, alpha=0.5)
        ax.add_patch(circle)
        ax.text(center[0], center[1], str(i), ha="center", va="center")

    plt.title(f"Circle Packing (n={len(centers)}, sum={sum(radii):.6f})")
    plt.show()


if __name__ == "__main__":
    centers, radii, sum_radii = run_packing()
    print(f"Sum of radii: {sum_radii}")
    # AlphaEvolve improved this to 2.635

    # Uncomment to visualize:
    visualize(centers, radii)