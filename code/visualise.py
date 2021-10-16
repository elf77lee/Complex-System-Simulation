# Class that handles the visualisation of the grid

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from tqdm import tqdm
import sys

REGEN_TIME = 20


class Visualise:
    """
    Class that visualizes a disklike grid. A bright color means the star was just born.
    """

    def __init__(self, grid):
        self.grid = grid

        # plot settings
        self.PRINT_GRID = True  # boolean to print each cell borders
        self.BG_COLOR = "lightgray"  # background color of cell borders
        self.FIG_SIZE = (15, 15)  # size of visualisation
        self.RING_RES = 0.001  # stepsize in radians of plot
        self.MAX_COLOR_VALUE = None

        # basic pyplot settins
        self.fig = plt.figure(figsize=self.FIG_SIZE)
        self.ax = self.fig.add_subplot(projection="polar")
        self.ax.grid(False)  # don't plot default grid lines
        plt.axis("off")
        self.ax.set_ylim([0, grid.NUM_OF_RINGS])
        self.df = None
        # usefull variables that are used multiple times
        self.rads = np.arange(0, (2 * np.pi), self.RING_RES)
        self.constant = np.ones(len(self.rads))
        self.cmap = plt.get_cmap("Blues")

    def update(self, timestep) -> None:
        """
        Updates the grid every timestep to plot depending on age
        :param timestep: all t=timestep time slices
        :return: None
        """
        self.ax.clear()
        self.ax.set_ylim([0, self.grid.NUM_OF_RINGS])
        for index, row in self.df[
            (self.df.t == timestep) & (self.df.age > 0)
        ].iterrows():
            age = row["age"]
            log_age = np.log(1 + age / self.MAX_COLOR_VALUE)
            color = self.cmap(log_age)
            self.fill_cell(row["theta1"], row["theta2"], row["parent_ring"], color="b")

    def animate(self, df, probability) -> None:
        """
        Animates the dataframe for all timesteps in the dataframe df
        :param df: dataframe to animate
        :return: None
        """
        self.df = df
        frames = df["t"].max()
        self.MAX_COLOR_VALUE = df["age"].max()
        print("Rendering animation output...")
        ani = FuncAnimation(
            self.fig, self.update, frames=tqdm(range(frames), file=sys.stdout)
        )
        ani.save(f"animation_{probability}.gif", writer="PillowWriter", fps=10)

    def print_grid(self) -> None:
        """
        Shows the grid on the screen
        """
        # print out custom grid lines if enabled
        for i in range(self.grid.NUM_OF_RINGS + 2):
            self.ax.plot(self.rads, i * self.constant, self.BG_COLOR)

            # plot cell dividers, except for the last ring
            if i == self.grid.NUM_OF_RINGS + 1:
                continue

            for j in range(i * self.grid.CELLS_PER_RING):
                theta = j * 2 * np.pi / (i * self.grid.CELLS_PER_RING)
                self.ax.plot([theta, theta], [i, i + 1], self.BG_COLOR)

    def fill_cell(self, theta1, theta2, r, color) -> None:
        """
        Fills a cell with polar coordinates theta1, theta2 and r, depending on color
        :param theta1: The first angle (lower part)
        :param theta2: The second angle (upper part)
        :param r: The radius of the ring
        :param color: The color the cell needs to get
        :return: None
        """

        self.ax.fill_between(
            x=np.arange(theta1, theta2, self.RING_RES),
            y1=r,
            y2=r + 1,
            color=color,
            interpolate=True,
            antialiased=True,
        )

    def show(self):
        plt.show()
