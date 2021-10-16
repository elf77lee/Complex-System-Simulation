# Class that looks for clusters and determines the number of clusters and the clustersize
# Plots average cluster size and number of clusters as a function of probability
# Reads large files and reconstructs them, take a few minutes to load.

from circulargrid import CircularGrid
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class Clusters(object):
    """ 
    Class that clusters features. Code based on Trackpy library code
    """

    @classmethod
    def from_grid(cls, grid, length, min_age) -> list:

        clusters = cls(range(length))
        for ring in grid.rings:
            for cell in ring.children:
                if cell.current_age < min_age:
                    continue
                neighbours = grid.get_neighbours(cell)
                for neighbour in neighbours:
                    if neighbour.current_age >= min_age:
                        clusters.add(cell.unique_id, neighbour.unique_id)
                        clusters.count_bonds(cell.unique_id, neighbour.unique_id)

        return clusters

    def __init__(self, indices):
        self.clusters = {i: {i} for i in indices}
        self.bonds = np.zeros(len(indices), dtype=int)
        self.pos_ids = list(indices)

    def __iter__(self):
        return (list(self.clusters[k]) for k in self.clusters)

    def add(self, a, b) -> None:
        """
        Adds links between cells for a cluster
        :param a: First cell
        :param b: Second cell
        :return: None
        """
        i1 = self.pos_ids[a]
        i2 = self.pos_ids[b]
        if i1 != i2:  # if a and b are already clustered, do nothing
            self.clusters[i1] = self.clusters[i1].union(self.clusters[i2])
            for f in self.clusters[i2]:
                self.pos_ids[f] = i1
            del self.clusters[i2]

    def count_bonds(self, a, b) -> None:
        """
        Adds bonds to a and b
        """
        self.bonds[a] += 1
        self.bonds[b] += 1

    @property
    def cluster_size(self):
        """
        Cluster size property
        """
        result = [None] * len(self.pos_ids)
        for cluster in self:
            for f in cluster:
                result[f] = len(cluster)
        return result


# Requires a datafile produced in varying_prob.py, these are the original files but they take a very long time to load
# original_filenames = [
#     "prob_0.1.csv",
#     "prob_0.2.csv",
#     "prob_0.3.csv",
#     "prob_0.4.csv",
#     "prob_0.5.csv",
#     "prob_0.6.csv",
# ]

# These are dummy files which take faster to load, but these are not good results
filenames = [
    "prob2_0.1.csv",
    "prob2_0.2.csv",
    "prob2_0.3.csv",
    "prob2_0.4.csv",
    "prob2_0.5.csv",
    "prob2_0.6.csv",
]

means = []
sizes = []

# Loops through all files defined above
for filename in filenames:

    datafile = filename
    df = pd.read_csv(datafile)
    max_id = 0
    cells_per_ring = len(df[df["parent_ring"] == 0])
    num_of_rings = df["parent_ring"].max() + 1
    grid = CircularGrid(num_of_rings, cells_per_ring)

    for index, row in df.iterrows():
        ring = grid.rings[int(row["parent_ring"])]
        cell = ring.children[int(row["id"])]
        cell.current_age = row["age"]
        cell.theta1 = row["theta1"]
        cell.theta2 = row["theta2"]

        if cell.unique_id > max_id:
            max_id = cell.unique_id

    clusters = Clusters.from_grid(grid, max_id + 1, 1)
    cluster_data = np.array(clusters.cluster_size)
    cluster_data = np.array([x for x in cluster_data if x != 1])
    df = pd.DataFrame(cluster_data)
    df.to_csv(f"clusters4_{filename}")

    mean = cluster_data.mean()
    cluster_number = len(cluster_data)

    print("mean = ", mean, "clusters = ", cluster_number)
    means.append(mean)
    sizes.append(cluster_number)

print("means: ", means)
print("sizes: ", sizes)

plt.plot([0.1, 0.2, 0.3, 0.4, 0.5, 0.6], means)
plt.plot([0.1, 0.2, 0.3, 0.4, 0.5, 0.6], means, "ro")

plt.xlabel("P", fontsize=25)
plt.ylabel("Average cluster size", fontsize=25)
plt.xscale("log")
plt.yscale("log")
plt.show()

plt.plot([0.1, 0.2, 0.3, 0.4, 0.5, 0.6], sizes)
plt.plot([0.1, 0.2, 0.3, 0.4, 0.5, 0.6], sizes, "ro")
plt.xlabel("P", fontsize=25)
plt.ylabel("Number of clusters", fontsize=25)
plt.xscale("log")
plt.yscale("log")
plt.show()
