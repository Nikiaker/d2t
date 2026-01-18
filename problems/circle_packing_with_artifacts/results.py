import json
import os
from pathlib import Path
import matplotlib.pyplot as plt

# Define the path to the all_programs folder
programs_dir = Path(__file__).parent / "all_programs"

# Load all JSON files
programs = []

for json_file in programs_dir.glob("*.json"):
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
            programs.append(data)
    except json.JSONDecodeError as e:
        print(f"Error loading {json_file.name}: {e}")
    except Exception as e:
        print(f"Error reading {json_file.name}: {e}")

print(f"Successfully loaded {len(programs)} JSON files")

# Optional: Print a summary
#for program in programs[:5]:  # Print first 5 as example
#    print(f"- ID: {program['id']} Island: {program['metadata']['island']} Iteration: {program['iteration_found']}")

islands = []
for i in range(4):
    island_i_programs = [p for p in programs if p['metadata']['island'] == i].copy()
    print(f"Number of programs from island {i}: {len(island_i_programs)}")
    island_i_programs.sort(key=lambda p: p['iteration_found'])

    unique_iterations = {}
    for p in island_i_programs:
        iteration = p['iteration_found']
        if iteration not in unique_iterations or p['metrics']['combined_score'] > unique_iterations[iteration]['metrics']['combined_score']:
            unique_iterations[iteration] = p

    island_i_programs = list(unique_iterations.values())[1:]
    islands.append(island_i_programs)
    #for p in island_i_programs:
    #    print(f"  - ID: {p['id']} Iteration: {p['iteration_found']} Score: {p['metrics']['sum_radii']:.4f}")

# Plot the linear graph for 4 islands
plt.figure(figsize=(10, 6))
colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red']

for i, island in enumerate(islands):
    if not island:
        continue
    island_sorted = sorted(island, key=lambda p: p['iteration_found'])
    x = [p['iteration_found'] for p in island_sorted]
    y = [p['metrics']['sum_radii'] for p in island_sorted]
    plt.plot(x, y, label=f'Island {i}', color=colors[i % len(colors)], marker='o', linewidth=1.5)

plt.xlabel('Iteracja')
plt.ylabel('Suma promieni')
plt.title('Suma promieni w kolejnych iteracjach dla wysp')
plt.grid(True, linestyle='--', alpha=0.4)
plt.legend()
plt.tight_layout()

out_path = Path(__file__).parent / 'islands_sum_radii.png'
plt.savefig(out_path)
print(f"Saved plot to {out_path}")
# plt.show()  # Uncomment to display interactively

best_islands = []
for i in range(4):
    island_i_programs = [p for p in programs if p['metadata']['island'] == i].copy()
    print(f"Number of programs from island {i}: {len(island_i_programs)}")
    island_i_programs.sort(key=lambda p: p['iteration_found'])
    island_i_programs = island_i_programs[1:]

    unique_iterations = {}
    for p in island_i_programs:
        iteration = p['iteration_found']
        if iteration not in unique_iterations or p['metrics']['combined_score'] > unique_iterations[iteration]['metrics']['combined_score']:
            unique_iterations[iteration] = p

    island_i_programs = list(unique_iterations.values())[1:]

    best_score_radii = -float('inf')
    for p in island_i_programs:
        if p['metrics']['sum_radii'] > best_score_radii:
            best_score_radii = p['metrics']['sum_radii']
        else:
            p['metrics']['sum_radii'] = best_score_radii

    best_islands.append(island_i_programs)

# Second graph using best_islands
plt.figure(figsize=(10, 6))

for i, island in enumerate(best_islands):
    if not island:
        continue
    island_sorted = sorted(island, key=lambda p: p['iteration_found'])
    x = [p['iteration_found'] for p in island_sorted]
    y = [p['metrics']['sum_radii'] for p in island_sorted]
    plt.plot(x, y, label=f'Island {i}', color=colors[i % len(colors)], marker='o', linewidth=1.5)

plt.xlabel('Iteracja')
plt.ylabel('Suma promieni')
plt.title('Najlepsza suma promieni w kolejnych iteracjach dla wysp')
plt.grid(True, linestyle='--', alpha=0.4)
plt.legend()
plt.tight_layout()

out_path_best = Path(__file__).parent / 'best_islands_sum_radii.png'
plt.savefig(out_path_best)
print(f"Saved plot to {out_path_best}")
plt.show()