import numpy as np


def starFormationRate(df, regenTime):
    """" Returns the number of new formed stars for each timeframe"""

    frames = df["t"].max()
    formationrate = np.zeros(frames)
    for i in range(frames):
        for index, row in df[(df.t == i) & (df.age == regenTime)].iterrows():
            formationrate[int(row["t"])] += 1

    return formationrate


def convergenceCheck(starformation):
    """Searches for the stable region of s. Returns the list starting from the stabilized point"""
    windowsize = int(len(starformation) / 10)
    if windowsize < 2:
        windowsize = 2

    starformation_reversed = list(np.flip(starformation))
    converged = False
    amplitude = 50
    i = 0

    while not converged:

        temp_starformation_first = starformation_reversed[i:windowsize + i]
        mean_first = np.array(temp_starformation_first).mean()
        i += 1
        temp_starformation_second = starformation_reversed[i:windowsize + i]

        mean_second = np.array(temp_starformation_second).mean()

        if abs(mean_first - mean_second) > amplitude:
            index = len(starformation) - i
            converged = True

        if windowsize + i == len(starformation):
            i = 0
            amplitude -= 1

    return starformation[index:]
