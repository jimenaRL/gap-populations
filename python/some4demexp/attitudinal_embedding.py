from itertools import combinations

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge

from some4demexp.inout import \
    load_ide_embeddings, \
    save_att_embeddings

def create_attitudinal_embedding(
    SQLITE,
    NB_MIN_FOLLOWERS,
    MIN_OUTDEGREE,
    ATTDIMS,
    ideN,
    survey,
    folder,
    emb_folder,
    att_folder,
    logger):


    SURVEYCOL = f'{survey.upper()}_party_acronym'

    # Load parties attitudinal coordinates
    parties_coord_att = SQLITE.getPartiesAttitudes(survey, ATTDIMS)

    # removed repeated parties
    parties_coord_att = parties_coord_att.groupby(SURVEYCOL).first().reset_index()

    # Load data from ideological embedding
    ide_followers, ide_mps = load_ide_embeddings(emb_folder, logger)
    ide_followers_cp = ide_followers.copy()
    ide_mps_cp = ide_mps.copy()
    mps_parties = SQLITE.getMpParties(['MMS', survey], dropna=False)

    # drop mps with parties withou mapping and add parties to ideological positions
    mps_with_mapping = mps_parties[~mps_parties[SURVEYCOL].isna()]
    mps_without_mapping = mps_parties[mps_parties[SURVEYCOL].isna()]
    mssg = f"Found {len(mps_with_mapping)} "
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
        mm = f"Dropped {t0 - t1} mps out of {t0} in ideological embedding "
        mm += f"with no party in mapping, left {t1}."
        logger.info(mm)

    parties_available_survey = set(parties_coord_att[SURVEYCOL].unique())
    parties_mps = set(ide_mps_in_parties_with_valid_mapping[SURVEYCOL].unique())

    if len(parties_available_survey) < len(parties_mps):
        m = f"There are less effetively available parties in survey {survey}: "
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

    assert (len(estimated_parties_coord_ide[SURVEYCOL].values) == len(parties_coord_att[SURVEYCOL].values))
    assert (estimated_parties_coord_ide[SURVEYCOL].values != parties_coord_att[SURVEYCOL].values).sum() == 0

    X = estimated_parties_coord_ide.drop(columns=[SURVEYCOL]).values
    Y = parties_coord_att.drop(columns=[SURVEYCOL, 'MMS_party_acronym']).values

    assert (len(X) == len(Y))

    clf = Ridge(alpha=1.0)
    clf.fit(X, Y)

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
    save_att_embeddings(
        follower_coord_att,
        mps_coord_att,
        att_folder,
        logger)