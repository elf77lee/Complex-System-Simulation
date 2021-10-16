import numpy as np


class CircularGrid:
    """"
    Creates grid object that holds ring objects. Allow to easily calculating the neighbours of the dynamic grid
    by calling get neighbours
    :param NUM_OF_RINGS: Number of rings that are in the grid
    :param CELLS_PER_RING: Number of cells that are added in every new ring.
    :param beforestep: Optional parameter, expects a function that will be called before handling every step
    :param step: Optional parameter, expects a function that will be called during handling every step
    :param afterstepstep: Optional parameter, expects a function that will be called after handling every step
    """
    def __init__(
        self, NUM_OF_RINGS, CELLS_PER_RING, beforestep=None, step=None, afterstep=None
    ):

        self.NUM_OF_RINGS = NUM_OF_RINGS  # total amount of rings in the plot
        self.CELLS_PER_RING = CELLS_PER_RING  # amount of cell for each ring, x cells are added for each ring
        self.rings = []
        self.beforestep = beforestep
        self.step = step
        self.afterstep = afterstep
        self.max_id = 0

        # create rings
        for i in range(self.NUM_OF_RINGS):
            new_ring = Ring(i, self)
            self.rings.append(new_ring)

    def announce_beforestep(self):
        """" Callback the beforestep function for every cell"""

        # check if there is a beforestepfunction defined
        if not self.beforestep:
            return

        self = self.beforestep(self)

    def announce_step(self):
        """" Callback the step function for every cell"""

        # check if there is a beforestepfunction defined
        if not self.step:
            return

        self = self.step(self)

    def announce_afterstep(self):
        """" Call the step function for every cell"""

        # check if there is a beforestepfunction defined
        if not self.afterstep:
            return

        self = self.afterstep(self)

    def get_ring(self, ring_id):
        """ Returns a ring object for a given ring id"""
        return self.rings[ring_id]

    def get_cell(self, ring_id, cell_id):
        """ Returns a cell object for a given ring and cell id"""
        ring = self.rings[ring_id]
        max_value = ring.num_of_children
        return ring.children[cell_id % max_value]

    def get_neighbours(self, cell):
        """ Returns a list of cell objects which are neighbours of the given input cell"""
        # find cell in the ring below with overlapping theta

        neighbours = []

        # find neighbours in lower ring
        if cell.parent.id > 0:
            for i in range(cell.id - self.CELLS_PER_RING, cell.id + 1):
                guess = self.get_cell(cell.parent.id - 1, i)
                if (guess.theta1 <= cell.theta1 < guess.theta2) or (
                        cell.theta1 < guess.theta1 < cell.theta2
                ):
                    neighbours.append(guess)

        # add left and right neighbour
        neighbours.append(self.get_cell(cell.parent.id, cell.id - 1))
        neighbours.append(self.get_cell(cell.parent.id, cell.id + 1))

        # find neighbours in upper ring
        if cell.parent.id + 1 < self.NUM_OF_RINGS:
            for i in range(cell.id, cell.id + 1 + self.CELLS_PER_RING):
                guess = self.get_cell(cell.parent.id + 1, i)
                if (guess.theta1 <= cell.theta1 < guess.theta2) or (
                        cell.theta1 < guess.theta1 < cell.theta2
                ):
                    neighbours.append(guess)
        return neighbours


class Ring:
    """"
    Ring objects that holds cells objects. Is used to order the cells in the grid object;
    :param ring_id: The id. Should match the position in the grid. Ring closes to the center should have id 0
    :param parent: Memory reference to the circular grid object.
    """
    def __init__(self, ring_id, parent):
        self.id = ring_id
        self.parent = parent
        self.children = []
        self.num_of_children = (ring_id + 1) * self.parent.CELLS_PER_RING
        self.offset = 0

        # fill ring with grid cells
        for i in range(self.num_of_children):
            new_cell = Cell(self, i)
            self.children.append(new_cell)

    def __repr__(self):
        """" Represent id instead of memory reference for easy debugging"""
        return "<Ring id:%s>" % (self.id)


class Cell:
    """"
    Cells objects that holds all the necessary information about each grid cell
    :param parent_ring: Memory reference to the ring object the cell belongs to.
    :param cell id: A
    """
    def __init__(self, parent_ring, cell_id, age=0):

        self.parent = parent_ring
        self.id = cell_id
        self.current_age = age
        self.next_age = 0

        self.level = self.parent.id + 1
        delta = 2 * np.pi / (float(self.level * self.parent.parent.CELLS_PER_RING))
        self.theta1 = self.id * delta
        self.theta2 =  self.theta1 + delta
        # create unique identifier. Useful when cells need to evaluated outside of the ring object.
        self.unique_id = self.parent.parent.CELLS_PER_RING * self.parent.id + self.id

    def get_theta1(self):
        """"Returns the angle of polar coordinates of the start position"""
        return self.theta1 + self.parent.offset

    def get_theta2(self):
        """"Returns the angle of polar coordinates of the end position"""
        return self.theta2 + self.parent.offset

    def __repr__(self):
        """" Represent id instead of memory reference for easy debugging"""
        return "<Cell id:%s parent_ring:%s>" % (self.id, self.parent.id)
