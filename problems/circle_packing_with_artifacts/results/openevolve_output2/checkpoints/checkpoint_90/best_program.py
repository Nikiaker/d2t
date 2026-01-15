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

    # Initial placement - hexagonal-like with some randomness and corner/edge focus
    for i in range(n):
        if i < 4:  # Focus on corners
            angle = np.random.rand() * np.pi / 2
            radius = 0.1 + 0.25 * np.random.rand()
            centers[i] = [radius * np.cos(angle), radius * np.sin(angle)]
        elif i < 8:  # Around the corners
            angle = 2 * np.pi * i / 8
            radius = 0.1 + 0.3 * np.random.rand()
            centers[i] = [0.5 + radius * np.cos(angle), 0.5 + radius * np.sin(angle)]
        else:  # More distributed
            angle = 2 * np.pi * i / n
            radius = 0.1 + 0.4 * np.random.rand()
            centers[i] = [0.5 + radius * np.cos(angle), 0.5 + radius * np.sin(angle)]

    # Clip centers to unit square
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
    radii = np.ones(n) * 0.05  # Initialize with a smaller radius

    # Limit by distance to square borders
    for i in range(n):
        x, y = centers[i]
        radii[i] = min(x, y, 1 - x, 1 - y)

    # Limit by distance to other circles - iterative refinement
    for _ in range(30):  # Increased iterations for refinement
        for i in range(n):
            for j in range(i + 1, n):
                dist = np.sqrt(np.sum((centers[i] - centers[j]) ** 2))
                if radii[i] + radii[j] > dist:
                    # Adjust radii proportionally
                    scale = (dist - 0.001) / (radii[i] + radii[j])  # Add small buffer
                    if scale > 0:
                        radii[i] *= scale
                        radii[j] *= scale

    # Additional refinement: increase radii if possible without overlap
    for i in range(n):
        max_increase = 0.007  # Limit the increase to avoid large jumps
        for _ in range(10): # refine a few times
            potential_radius = radii[i] + max_increase
            valid = True
            for j in range(n):
                if i != j:
                    dist = np.sqrt(np.sum((centers[i] - centers[j]) ** 2))
                    if potential_radius + radii[j] > dist:
                        valid = False
                        break
            if valid and potential_radius <= min(centers[i][0], centers[i][1], 1 - centers[i][0], 1 - centers[i][1]):
                radii[i] = potential_radius
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