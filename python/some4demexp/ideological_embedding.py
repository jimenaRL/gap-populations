import numpy as np
import pandas as pd

from linate import IdeologicalEmbedding
from some4demexp.graph import graphToAdjencyMatrix
from some4demexp.inout import \
    load_experiment_data, \
    save_ide_embeddings, \
    save_experiment_data


def create_ideological_embedding(
    SQLITE,
    NB_MIN_FOLLOWERS,
    MIN_OUTDEGREE,
    ideN,
    folder,
    emb_folder,
    logger):

    # Get data
    preprocessed_graph = SQLITE.getPreprocessedGraph(
        NB_MIN_FOLLOWERS,
        MIN_OUTDEGREE)

    # Build adjency matrix
    X, targets_pids, sources_pids, sources_map_pids = graphToAdjencyMatrix(
        preprocessed_graph, MIN_OUTDEGREE, logger, sparce=False)

    # Save social graph and target/source pseudo ids
    save_experiment_data(
        X, targets_pids, sources_pids, sources_map_pids, folder, logger)


    # 2. Create ideological embeddings
    X, targets_pids, sources_pids, sources_map_pids = load_experiment_data(folder)

    # Create and fit ideological embedding
    model = IdeologicalEmbedding(
        n_latent_dimensions=ideN,
        check_input=True,
        engine='auto',
        force_bipartite=True,
        force_full_rank=False,
        in_degree_threshold=NB_MIN_FOLLOWERS,
        out_degree_threshold=None,
        random_state=None,
        standardize_mean=True,
        standardize_std=False,
    )
    model.fit(X)

    targets_embeddings = model.ideological_embedding_target_latent_dimensions_ \
        .reset_index() \
        .drop(columns=["target_id"]) \
        .assign(entity=targets_pids)

    sources_embeddings = model.ideological_embedding_source_latent_dimensions_ \
        .reset_index() \
        .drop(columns=["source_id"]) \
        .assign(entity=sources_pids)

    # reintegrate repeated sources
    # TO DO: DOCUMENT THE PROCESS !!!!!!!
    # quitte hard to explain but must be done
    # ['original_columns_id', 'idx_inv']

    l0 = len(sources_map_pids)
    sources_map_pids = pd.DataFrame(
        data=sources_map_pids,
        columns=['original_columns_id', 'idx_inv'])
    sources_map_pids = sources_map_pids.merge(
        sources_embeddings,
        left_on='idx_inv',
        right_on='entity',
        how='left') \
        .drop(columns=['idx_inv', 'entity']) \
        .rename(columns={'original_columns_id': 'entity'})

    assert l0 == len(sources_map_pids)
    assert sources_map_pids.latent_dimension_0.isnull().sum() == 0

    sources_embeddings = sources_map_pids

    assert sources_embeddings.duplicated().sum() == 0

    # Save sources/targets coordinates in ideological space and add pseudo ids    
    save_ide_embeddings(sources_embeddings, targets_embeddings, emb_folder, logger)

