import numpy as np
from scipy import stats


def smallSamplesSpearmanr(x, y):
    """
    Small Samples Spearman Correlation Coefficient and p-value.
    See discussion at
        https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html
    about p-value calculation for small sized dataset samples (< 500 points).
    """

    # student-t degrees of freedom
    dof = len(x) - 2

    def statistic(x):
        """
        Explore all possible pairings by permuting `x`
        """
        rs = stats.spearmanr(x, y).correlation  # ignore pvalue
        transformed = rs * np.sqrt(dof / ((rs+1.0)*(1.0-rs)))
        return transformed

    # get statistics
    rs = stats.spearmanr(x, y).correlation

    # compute null distribution
    ref = stats.permutation_test(
        (x,), statistic, alternative='two-sided', permutation_type='pairings')

    # mssg = "Computed exact Spearman Rho test null distribution of "
    # mssg += f"{len(ref.null_distribution)} permutations."
    # print(mssg)

    # get pvalue
    pvalue = ref.pvalue

    return rs, pvalue