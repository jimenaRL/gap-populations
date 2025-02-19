import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

from gap.conf import ATTDICT


# Font & Latex definitions
mpl.rcParams['mathtext.fontset'] = 'cm'
mpl.rcParams['mathtext.rm'] = 'serif'
# mpl.rcParams['text.latex.preamble']=[r"\usepackage{amsmath}"]
fs = 16
figsize = (12, 12)
# dpi = 150
plt.rc('text', usetex=True)
plt.rc('font', family='sans-serif', size=fs)

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
    year,
    survey,
    paths,
    logger,
    show):

    users_coord = pd.concat([sources_coord, targets_coord])
    dims = list(users_coord.columns)
    Ndims = len(dims)
    nrows = int(Ndims/2) if Ndims % 2 == 0 else int(Ndims/2) + 1

    fig, axes = plt.subplots(nrows=nrows, ncols=2, figsize=figsize)
    for i, ax in enumerate(axes.flatten()):
        if i < Ndims:
            dim = dims[i]
            x = users_coord[dim]
            x0 = len(x)
            filtered = x[~is_outlier(x, thresh=35)]
            if len(filtered) < x0:
                print(f"{country}: drop {x0 - len(filtered)} points in axis {dim}.")
            filtered.plot.hist(ax=ax, bins=100)
            s = ATTDICT[survey][dim].replace(" – ", "-").replace("_", "-").replace("_", "-").replace(" ", "-")
            ax.set_xlim((-1, 11))
            ax.set_xlabel(f"$\delta_{{{s}}}$", fontsize=fs+5)
            ax.set_ylabel('')
            ax.set_xticks([0, 2.5, 5, 7.5, 10])
            ax.tick_params(axis='y', labelsize=fs)
            plt.locator_params(axis='y', nbins=3)
            ax.tick_params(axis='x', labelsize=fs)
            ax.tick_params(axis='y', labelsize=fs)
        else:
            ax.set_ylabel('')
            plt.tick_params(
                which='both',
                bottom=False,
                left=False,
                labelbottom=False,
                labelleft=False)

    # title
    title = f'{country.capitalize()} {year}\n{survey}'
    fig.suptitle(title, fontweight='normal', fontsize=fs, x=0.5, y=0.99)

    fig.tight_layout()

    for path in paths:
        fig.savefig(path, dpi=300)
        logger.info(
            f"VALIDATION: distribution plot saved at {path}")

    if show:
        plt.show()
