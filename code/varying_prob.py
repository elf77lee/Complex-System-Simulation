# Produces animations and saves data to csv for propagation probabilities [0.1, 0.2, ... , 0.6]

from visualise import Visualise
from model import Model
from analyse import *
import matplotlib.pyplot as plt
import random
import pandas as pd

REGEN_TIME = 10
MAX_RANDOM_STARS = 5
NUM_OF_RINGS = 8
CELLS_PER_RING = 4
TIMESTEP = 1
SIMDURATION = 50
PROPAGATION_SPEED = 1
prop_probabilities = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
INITIAL_STARS = 20

# Loop throuh all probabilities
for probability in prop_probabilities:

    model = Model(REGEN_TIME, probability, MAX_RANDOM_STARS, PROPAGATION_SPEED)
    model.bind_grid(NUM_OF_RINGS, CELLS_PER_RING)
    model.bind_scheduler()

    # Initialize random stars first
    for i in range(INITIAL_STARS):
        ring = random.choice(model.grid.rings)
        cell = random.choice(ring.children)

        while cell.current_age > 0:
            ring = random.choice(model.grid.rings)
            cell = random.choice(ring.children)

        cell.current_age = REGEN_TIME

    model.scheduler.start(TIMESTEP, SIMDURATION)
    df = pd.DataFrame(model.scheduler.history.tolist())
    starsformed = starFormationRate(df, REGEN_TIME)
    conv = convergenceCheck(starsformed)

    plotter = Visualise(model.grid)
    plotter.animate(df, probability)
    df.to_csv(f"prob2_{probability}.csv")
