# Class that handles the scheduling of the simulation, i.e. when each model and agent step happens.

import numpy as np
from tqdm import tqdm


class Scheduler:
    def __init__(self, grid, timestep=0, iteration_callback=None):
        """ Manages the timesteps on the circular grid
        :param grid: the Circular grid object
        :param timestep: time to wait between each step, only usefull is visualing data. Should be zero otherwise
        :param iteration_callback: Function that gets called after a completed iteration.
        """

        self.grid = grid
        self.timestep = timestep
        self.iteration_callback = iteration_callback
        self.started = False

        self.history = []
        self.timestamp = 0

    def start(self, dt, t_end) -> None:
        """ 
        Starts the simulation 
        :param dt: Timestep size
        :param t_end: end time of the simulation
        :return: None
        """
        print("Starting simulation...")
        for t in tqdm(np.arange(0, t_end, dt)):
            self.timestamp = t
            self.grid.announce_beforestep()
            self.grid.announce_afterstep()
            self.grid.announce_step()
            self.history = np.concatenate(
                (self.history, self.get_snapshot()), axis=None
            )

        return

    def get_snapshot(self) -> np.array:
        """
        :return: array of dictionaries with all the cell states
        """
        data = []
        for ring in self.grid.rings:
            for cell in ring.children:
                celldata = {
                    "t": self.timestamp,
                    "id": cell.id,
                    "age": cell.current_age,
                    "parent_ring": cell.parent.id,
                    "theta1": cell.get_theta1(),
                    "theta2": cell.get_theta2(),
                }
                data.append(celldata)
        return np.array(data)

    def pause(self):
        """
        Pauses the current simulation after finishing current iteration
        """
        self.started = False

