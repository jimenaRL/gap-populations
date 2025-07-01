from itertools import combinations

from gap.adjency_matrix import graphToAdjencyMatrix

import numpy as np
import pandas as pd

from linate import IdeologicalEmbedding
from sklearn.linear_model import Ridge

def joinParties(parties, joinseq='\n\t'):
    return '\n\t'+joinseq.join(parties)+'\n'

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
    N_survey,
    logger,
    embeddings_source,
    ignore_errors=True):

    SURVEYCOL = f'{survey.upper()}_party_acronym'

    # Load parties attitudinal coordinates
    parties_coord_att = SQLITE.getPartiesAttitudes(survey, ATTDIMS)

    # removed repeated parties
    parties_coord_att = parties_coord_att.groupby(SURVEYCOL).first().reset_index()

    # Load data from ideological embedding
    ide_mps, ide_followers =  INOUT.load_ide_embeddings(source=embeddings_source)
    ide_followers_cp = ide_followers.copy()
    ide_mps_cp = ide_mps.copy()
    mps_parties = SQLITE.getMpParties(['EPO', survey], dropna=False)

    # drop mps with parties withou mapping and add parties to ideological positions
    mps_with_mapping = mps_parties[~mps_parties[SURVEYCOL].isna()]
    mps_without_mapping = mps_parties[mps_parties[SURVEYCOL].isna()]
    mssg = f"ATTITUDINAL EMBEDDINGS: found {len(mps_with_mapping)} mps that "
    mssg += f"are associated to a party having a mapping in {survey} survey."
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
        mm += f"ideological embedding that are not associated to a party"
        mm += f"having a mapping in {survey} survey. Left {t1}."
        logger.info(mm)

    parties_available_survey = set(parties_coord_att[SURVEYCOL].unique())
    parties_mps = set(ide_mps_in_parties_with_valid_mapping[SURVEYCOL].unique())

    if not set(parties_mps).issubset(parties_available_survey):
        m = f"ATTITUDINAL EMBEDDINGS: there are parties in mps affilations "
        m += f"{joinParties(parties_mps)} that are not present in survey "
        m += f"{survey} {joinParties(parties_available_survey)}"
        m += f"Dropping {parties_mps - parties_available_survey}."
        logger.info(m)
        new_candidate_N_survey = len(parties_available_survey) - 1
        if not ignore_errors:
            user_input = input(
                f"Do you want to continuate (yes/no):")
            while user_input.lower() != 'yes':
                if user_input.lower() == 'no':
                    exit()
                else:
                    user_input = input('Please type yes or no:')
        cond = ide_mps_in_parties_with_valid_mapping[SURVEYCOL].isin(
            parties_available_survey)
        ide_mps_in_parties_with_valid_mapping = ide_mps_in_parties_with_valid_mapping[cond]
        if N_survey != new_candidate_N_survey:
            N_survey = new_candidate_N_survey
            logger.info(f"N_survey value vas modified to {N_survey}.")


    # Fit ridge regression
    estimated_parties_coord_ide = ide_mps_in_parties_with_valid_mapping \
        .drop(columns=['entity', 'EPO_party_acronym']) \
        .groupby(SURVEYCOL) \
        .mean() \
        .reset_index()

    estimated_parties_coord_ide = estimated_parties_coord_ide.sort_values(by=SURVEYCOL)
    parties_coord_att = parties_coord_att.sort_values(by=SURVEYCOL)

    partiesIde = set(estimated_parties_coord_ide[SURVEYCOL].values.tolist())
    partiesAtt = set(parties_coord_att[SURVEYCOL].values.tolist())

    if not partiesIde == partiesAtt:
        mssg = f"ATTITUDINAL EMBEDDINGS: parties with ideological coordinates "
        mssg += f"doesn't match parties with attitudinal annotations.\n"
        mssg += f"IDE COORDINATES: {joinParties(partiesIde)}"
        mssg += f"ATT COORDINATES: {joinParties(partiesAtt)}"
        if not partiesAtt.issubset(partiesIde):
            mssg += f"These parties are excedding and will be ignored:"
            mssg += f"{joinParties(partiesAtt - partiesIde)}"
            logger.info(mssg)
            if not ignore_errors:
                new_candidate_N_survey = len(partiesIde) - 1
                user_input = input("Do you want to continuate (yes/no):")
                while user_input.lower() != 'yes':
                    if user_input.lower() == 'no':
                        exit()
                    else:
                        user_input = input('Please type yes or no:')

                parties_coord_att = parties_coord_att[parties_coord_att[SURVEYCOL].isin(partiesIde)]
                if N_survey != new_candidate_N_survey:
                    N_survey = new_candidate_N_survey
                    logger.info(f"N_survey value vas modified to {N_survey}.")

                if not partiesIde == partiesAtt:
                    logger.info(f"Parties: {','.join(partiesAtt - partiesIde)} where ignored.")

        else:  # not partiesIde.issubset(partiesAtt)
            e = "Found unexpected condition "
            e += "'not partiesIde.issubset(partiesAtt)' with"
            e += f"partiesIde: {joinParties(partiesIde)}"
            e += "and"
            e += f"with partiesAtt: {joinParties(partiesAtt)}"
            raise ValueError(e)

    v1 = estimated_parties_coord_ide[SURVEYCOL].values
    v2 = parties_coord_att[SURVEYCOL].values
    if not (v1 != v2).sum() == 0:
        e = f"Parties attitudinal coordinates from survey {v2} and estimated "
        e += f"parties attitudinal coordinates {v1} must coincide to proceed "
        e += "to Ridge regression."
        raise ValueError(e)

    X = estimated_parties_coord_ide.drop(columns=[SURVEYCOL]).values
    Y = parties_coord_att.drop(columns=[SURVEYCOL, 'EPO_party_acronym']).values
    assert (len(X) == len(Y))

    # make the projection of the ideological embedding onto the first N_survey
    # dimensions
    X = X[:, :N_survey]

    # the following check should be redundant, just to check that the correct
    # value was computed in the pipeline for N_survey
    assert N_survey == len(X) - 1

    clf = Ridge(alpha=1.0)
    clf.fit(X, Y)

    intercept = clf.intercept_
    coefficients = clf.coef_

    # make the projection of the ideological embedding onto the first N_survey
    # dimensions and perfoem map
    ide_values_followers = ide_followers_cp.drop(columns=['entity']).values[:, :N_survey]
    ide_values_mps = ide_mps.drop(columns=['entity']).values[:, :N_survey]

    follower_coord_att_values = clf.predict(ide_values_followers)
    mps_coord_att_values = clf.predict(ide_values_mps)

    columns = parties_coord_att.drop(
        columns=["EPO_party_acronym", SURVEYCOL]).columns
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
