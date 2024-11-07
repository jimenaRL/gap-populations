from itertools import combinations

from gap.adjency_matrix import graphToAdjencyMatrix

import numpy as np
import pandas as pd

from linate import IdeologicalEmbedding
from sklearn.linear_model import Ridge

def create_ideological_embedding(
    SQLITE,
    INOUT,
    NB_MIN_FOLLOWERS,
    MIN_OUTDEGREE,
    ideN,
    logger):

    # Get data
    preprocessed_graph = SQLITE.getPreprocessedGraph(
        NB_MIN_FOLLOWERS,
        MIN_OUTDEGREE)

    # Build adjency matrix
    X, targets_pids, sources_pids, sources_map_pids = graphToAdjencyMatrix(
        preprocessed_graph, MIN_OUTDEGREE, logger, sparce=False)

    # Save social graph and target/source pseudo ids
    INOUT.save_experiment_data(
        X, targets_pids, sources_pids, sources_map_pids)

    # 2. Create ideological embeddings

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

    # homogenize columns order
    sources_embeddings = sources_embeddings[targets_embeddings.columns.tolist()]

    # Save sources/targets coordinates in ideological space and add pseudo ids
    INOUT.save_ide_embeddings(sources_embeddings, targets_embeddings)

def create_attitudinal_embedding(
    SQLITE,
    INOUT,
    ATTDIMS,
    survey,
    logger):


    SURVEYCOL = f'{survey.upper()}_party_acronym'

    # Load parties attitudinal coordinates
    parties_coord_att = SQLITE.getPartiesAttitudes(survey, ATTDIMS)

    # removed repeated parties
    parties_coord_att = parties_coord_att.groupby(SURVEYCOL).first().reset_index()

    # Load data from ideological embedding
    ide_followers, ide_mps =  INOUT.load_ide_embeddings()
    ide_followers_cp = ide_followers.copy()
    ide_mps_cp = ide_mps.copy()
    mps_parties = SQLITE.getMpParties(['MMS', survey], dropna=False)

    # drop mps with parties withou mapping and add parties to ideological positions
    mps_with_mapping = mps_parties[~mps_parties[SURVEYCOL].isna()]
    mps_without_mapping = mps_parties[mps_parties[SURVEYCOL].isna()]
    mssg = f"ATTITUDINAL EMBEDDINGS: found {len(mps_with_mapping)} "
    mssg += f"associated to parties mps with mapping in {survey}."
    logger.info(mssg)

    t0 = len(ide_mps)
    ide_mps_in_parties_with_valid_mapping = ide_mps.merge(
            mps_with_mapping,
            left_on="entity",
            right_on="mp_pseudo_id",
            how="inner"
        ) \
        .drop(columns="mp_pseudo_id")
    t1 = len(ide_mps_in_parties_with_valid_mapping)
    if t0 > t1:
        mm = f"ATTITUDINAL EMBEDDINGS: dropped {t0 - t1} mps out of {t0} in "
        mm += f"ideological embedding with no party in mapping, left {t1}."
        logger.info(mm)

    parties_available_survey = set(parties_coord_att[SURVEYCOL].unique())
    parties_mps = set(ide_mps_in_parties_with_valid_mapping[SURVEYCOL].unique())

    if len(parties_available_survey) < len(parties_mps):
        m = f"ATTITUDINAL EMBEDDINGS: there are less effectively available "
        m += f"parties in survey {survey}: "
        m += f"{parties_available_survey} that parties present in mps affilations "
        m += f"{parties_mps}. Dropping {parties_mps - parties_available_survey}."
        logger.info(m)
        cond = ide_mps_in_parties_with_valid_mapping[SURVEYCOL].isin(
            parties_available_survey)
        ide_mps_in_parties_with_valid_mapping = ide_mps_in_parties_with_valid_mapping[cond]

    # Fit ridge regression
    estimated_parties_coord_ide = ide_mps_in_parties_with_valid_mapping \
        .drop(columns=['entity', 'MMS_party_acronym']) \
        .groupby(SURVEYCOL) \
        .mean() \
        .reset_index()

    estimated_parties_coord_ide = estimated_parties_coord_ide.sort_values(by=SURVEYCOL)
    parties_coord_att = parties_coord_att.sort_values(by=SURVEYCOL)

    p1 = set(estimated_parties_coord_ide[SURVEYCOL].values.tolist())
    p2 = set(parties_coord_att[SURVEYCOL].values.tolist())
    if not p1 == p2:
        if p1.issubset(p2):
            mssg = f"ATTITUDINAL EMBEDDINGS: parties with estimated "
            mssg += f"ideological coordinates ({','.join(p1)}) "
            mssg += f"doesn't match parties with attitudinal annotations "
            mssg += f"({','.join(p2)}) for survey {survey}. "
            prompt = mssg + f"Parties: {','.join(p2 - p1)} will be ignored."
            # prompt += f"ignored. Do you want to continuate (yes/no): "
            # user_input = input(prompt)

            # while user_input.lower() != 'yes':
                # if user_input.lower() == 'no':
                    # exit()
                # else:
                    # user_input = input('Please type yes or no:')
        else:
            raise ValueError(mssg)

    parties_coord_att = parties_coord_att[parties_coord_att[SURVEYCOL].isin(p1)]

    if not p1 == p2:
        logger.info(mssg + f"Parties: {','.join(p2 - p1)} where ignored.")

    v1 = estimated_parties_coord_ide[SURVEYCOL].values
    v2 = parties_coord_att[SURVEYCOL].values
    assert (v1 != v2).sum() == 0

    X = estimated_parties_coord_ide.drop(columns=[SURVEYCOL]).values
    Y = parties_coord_att.drop(columns=[SURVEYCOL, 'MMS_party_acronym']).values

    assert (len(X) == len(Y))

    clf = Ridge(alpha=1.0)
    clf.fit(X, Y)

    intercept = clf.intercept_
    coefficients = clf.coef_

    follower_coord_att_values = clf.predict(ide_followers_cp.drop(columns=['entity']).values)
    mps_coord_att_values = clf.predict(ide_mps.drop(columns=['entity']).values)

    columns = parties_coord_att.drop(
        columns=["MMS_party_acronym", SURVEYCOL]).columns
    follower_coord_att = pd.DataFrame(
        data=follower_coord_att_values,
        columns=columns) \
        .assign(entity=ide_followers_cp.entity)
    mps_coord_att = pd.DataFrame(
        data=mps_coord_att_values,
        columns=columns) \
        .assign(entity=ide_mps.entity)

    # save results
    INOUT.save_att_embeddings(follower_coord_att, mps_coord_att)
    INOUT.save_affine_map(coefficients, intercept, columns)
