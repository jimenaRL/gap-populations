import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def is_outlier(points, thresh=3.5):
    """
    Returns a boolean array with True if points are outliers and False 
    otherwise.

    Parameters:
    -----------
        points : An numobservations by numdimensions array of observations
        thresh : The modified z-score to use as a threshold. Observations with
            a modified z-score (based on the median absolute deviation) greater
            than this value will be classified as outliers.

    Returns:
    --------
        mask : A numobservations-length boolean array.

    References:
    ----------
        Boris Iglewicz and David Hoaglin (1993), "Volume 16: How to Detect and
        Handle Outliers", The ASQC Basic References in Quality Control:
        Statistical Techniques, Edward F. Mykytka, Ph.D., Editor.
    """
    points = points.values
    if len(points.shape) == 1:
        points = points[:, None]
    median = np.median(points, axis=0)
    diff = np.sum((points - median)**2, axis=-1)
    diff = np.sqrt(diff)
    med_abs_deviation = np.median(diff)

    modified_z_score = 0.6745 * diff / med_abs_deviation

    return modified_z_score > thresh

def distributions(
    sources_coord,
    targets_coord,
    country,
    survey,
    show=False):

    users_coord = pd.concat([sources_coord, targets_coord])
    dims = list(users_coord.drop(columns='entity').columns)
    ideN = len(users_coord.columns) - 1
    nrows = int(ideN/2) if ideN % 2 == 0 else int(ideN/2) + 1

    fig, axes = plt.subplots(nrows=nrows, ncols=2, figsize=(8, 6))
    for i in range(ideN):
        ax = axes.flatten()[i]
        dim = dims[i]
        x = users_coord[dim]
        x0 = len(x)
        filtered = x[~is_outlier(x, thresh=35)]
        if len(filtered) < x0:
            print(f"{country}: drop {x0 - len(filtered)} points in axis {dim}.")
        filtered.plot.hist(ax=ax, bins=100)
        ax.set_title(dim.replace('_', ' '))
    fig.suptitle(f"{country} - {survey}")
    fig.tight_layout()
    if show:
        plt.show()
