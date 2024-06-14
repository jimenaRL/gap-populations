import os
import copy
import yaml
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix


def graphToAdjencyMatrix(graph, min_outdegree, logger, sparce=False):
    """
    # Format data from sqlite graph res and build (sparse) matrix
    """

    logger.info(f"Building adjency matrix... ")

    sources = [link[1] for link in graph]
    targets = [link[0] for link in graph]

    # create sparse matrix
    n_i, rows_id = pd.factorize(targets)
    n_j, columns_id = pd.factorize(sources)
    n_in_j, tups = pd.factorize(list(zip(n_j, n_i)))

    ntwrk_csr = csr_matrix((np.bincount(n_in_j), tuple(zip(*tups))))

    # remove sources with too low out degree
    out_degrees_j = ntwrk_csr.sum(axis=1)
    idx_valid_j = np.argwhere(out_degrees_j >= min_outdegree)[:, 0]
    j0 = ntwrk_csr.shape[0]
    ntwrk_csr = ntwrk_csr[idx_valid_j, :]
    j1 = ntwrk_csr.shape[0]
    columns_id = columns_id[idx_valid_j]

    assert ntwrk_csr.shape == (len(columns_id), len(rows_id))
    mssg = f"Drop {j0 - j1} of {j0} sources ({100*(j0 - j1)/j0:.2f}%) "
    mssg += f"with outdegree less than {min_outdegree}, keeped {j1}."
    logger.info(mssg)

    mssg0 = f"Found {ntwrk_csr.nnz} links, from {len(columns_id)} sources "
    mssg0 += f"to {len(rows_id)} targets."
    logger.info(mssg0)

    # remove and keep repeated sources (rows)
    old_ntwrk = copy.deepcopy(ntwrk_csr)
    old_columns_id = copy.deepcopy(columns_id)
    values, unique_idx_j, inverse = np.unique(
        ntwrk_csr.toarray(), axis=0, return_index=True, return_inverse=True)

    ja = ntwrk_csr.shape[0]
    ntwrk_csr = ntwrk_csr[unique_idx_j, :]
    jb = ntwrk_csr.shape[0]
    columns_id = columns_id[unique_idx_j]

    assert np.abs(values - ntwrk_csr).sum() == 0
    assert np.abs(old_ntwrk - ntwrk_csr[inverse]).sum() == 0


    # TO DO; DOCUMENT !!!!!!!
    # quitte hard to explain but must be done
    # check np.unique doc at
    # https://numpy.org/doc/stable/reference/generated/numpy.unique.html
    # ['original_columns_id', 'idx_inv']
    mapp = np.array([old_columns_id, old_columns_id[unique_idx_j][inverse]]).T


    assert ntwrk_csr.shape == (len(columns_id), len(rows_id))
    mssg = f"Drop {ja - jb} of {ja} repeated sources "
    mssg += f"({100*(ja - jb)/ja:.2f}%), keeped {jb}."
    logger.info(mssg)

    # remove targets (columns) with no source associated
    idx_invalid_i = np.argwhere((np.abs(ntwrk_csr).sum(axis=0) == 0).tolist()[0])[:, 0]
    invalid_rows_id = rows_id[idx_invalid_i]

    idx_valid_i = np.argwhere((np.abs(ntwrk_csr).sum(axis=0) != 0).tolist()[0])[:, 0]

    ia = ntwrk_csr.shape[1]
    ntwrk_csr = ntwrk_csr[:, idx_valid_i]
    ib = ntwrk_csr.shape[1]
    rows_id = rows_id[idx_valid_i]

    assert ntwrk_csr.shape == (len(columns_id), len(rows_id))
    mssg = f"Drop {ia - ib} targets with no sources associated "
    mssg += f"({100*(ia - ib)/ia:.2f}%), keeped {ib}:\n{invalid_rows_id}"

    # checking if final network is bipartite:
    nb_shared = len(np.intersect1d(rows_id, columns_id))
    if not nb_shared == 0:
        raise ValueError(
            f"Created graph is not bipartited, found {nb_shared} common nodes.")

    mssg1 = f"Found {ntwrk_csr.nnz} links, from {len(columns_id)} unique sources "
    mssg1 += f"to {len(rows_id)} unique targets."


    logger.info(mssg)
    logger.info(mssg1)

    if sparce:
        return ntwrk_csr, rows_id, columns_id, mapp

    return ntwrk_csr.toarray(), rows_id, columns_id, mapp

