import os
import yaml
import pandas as pd
from string import Template
from itertools import combinations

from gap.inout import \
    get_ide_ndims, \
    set_output_folder_emb, \
    set_output_folder_att, \
    load_ide_embeddings, \
    load_att_embeddings

from gap.bivariate_marginal import \
    visualize_ide, \
    visualize_att

from gap.distributions import distributions

from gap.conf import \
    CHES2019DEFAULTATTVIZ, \
    GPS2019DEFAULTATTVIZ, \
    CHES2023DEFAULTATTVIZ

def plot_ideological_embedding(
    SQLITE,
    NB_MIN_FOLLOWERS,
    MIN_OUTDEGREE,
    country,
    survey,
    ideN,
    n_dims_to_viz,
    folder,
    emb_folder,
    vizparams,
    show,
    logger):

    # Load data from ideological embedding
    ide_sources, ide_targets = load_ide_embeddings(emb_folder, logger)

    # show by dim distributions
    distributions(
        ide_sources,
        ide_targets,
        "",
        country,
        show)

    palette = vizparams['palette']
    idevizparams = vizparams['ideological']
    mp_parties = SQLITE.getMpParties(['MMS', survey])
    targets_parties = mp_parties[['mp_pseudo_id', 'MMS_party_acronym']] \
        .rename(columns={'MMS_party_acronym': 'party'})

    # select parties to show
    _parties_to_show = mp_parties[~mp_parties[f'{survey.upper()}_party_acronym'].isna()]
    parties_to_show = _parties_to_show['MMS_party_acronym'].unique().tolist()

    d21_folder = os.path.join(f"exports/deliverableD21/ideological/{country}")
    output_folders = [emb_folder]

    for x, y in combinations(range(n_dims_to_viz), 2):
        visualize_ide(
            sources_coord_ide=ide_sources,
            targets_coord_ide=ide_targets,
            targets_parties=targets_parties,
            parties_to_show=parties_to_show,
            latent_dim_x=x,
            latent_dim_y=y,
            output_folders=output_folders,
            logger=logger,
            show=show,
            palette=palette,
            **idevizparams
        )

def plot_attitudinal_embedding(
    SQLITE,
    NB_MIN_FOLLOWERS,
    MIN_OUTDEGREE,
    ATTDIMS,
    country,
    ideN,
    survey,
    folder,
    emb_folder,
    att_folder,
    vizparams,
    show,
    logger):

    SURVEYCOL = f'{survey.upper()}_party_acronym'

    att_sources, att_targets = load_att_embeddings(att_folder, logger)

    mps_parties = SQLITE.getMpParties(['MMS', survey], dropna=True)

    # # (0) show by dim distributions
    # distributions(
    #     att_sources,
    #     att_targets,
    #     country,
    #     survey,
    #     show)

    # (1) show 2d figures

    # use mapping to adapt palette to the party system survey
    color_data = vizparams['palette'].items()
    palette = pd.DataFrame.from_dict(color_data) \
        .rename(columns={0: 'MMS_party_acronym', 1: 'color'}) \
        .merge(SQLITE.getPartiesMapping(surveys=[survey]))
    _zip = zip(palette[SURVEYCOL], palette['color'])
    palette = {z[0]: z[1] for z in _zip}

    parties_coord_att = SQLITE.getPartiesAttitudes(survey, ATTDIMS)

    rename_cols = {SURVEYCOL: 'party'}
    att_targets.rename(columns=rename_cols, inplace=True)
    parties_coord_att.rename(columns=rename_cols, inplace=True)

    # When the matchong betwwen MMS and the survey isnot injective,
    # keep only one match
    parties_coord_att.drop_duplicates(subset=['party'], inplace=True)

    # visualize attitudinal espaces
    for dimpair in combinations(ATTDIMS, 2):

        dimpair_str = '_vs_'.join(dimpair)
        #  FOR DEBUGGING
        if dimpair_str not in [
            # FOR TESTING
            # 'lrgen_vs_antielite_salience',
            # 'V4_Scale_vs_V6_Scale',
            # FOR MIRO VIZ
            # ches2019
            'lrgen_vs_antielite_salience',
            'lrgen_vs_lrecon',
            'galtan_vs_environment',
            'eu_position_vs_immigrate_policy',
            # gps2019
            'V6_Scale_vs_v14',
            'V4_Scale_vs_V6_Scale',
            'v12_vs_v13',
            'v10_vs_v20',
            # ches2023
            'lrecon_vs_antielite_salience',
            'lrecon_vs_energy_costs',
            'galtan_vs_supportUA',
            'eu_position_vs_refugees',
        ]:
            continue

        if dimpair_str in vizparams['attitudinal'][survey]:
            attvizparams = vizparams['attitudinal'][survey][dimpair_str]
        else:
            attvizparams = globals()[f"{survey.upper()}DEFAULTATTVIZ"]


        d21_folder = os.path.join(f"exports/deliverableD21/attitudinal/{country}")
        os.makedirs(d21_folder, exist_ok=True)
        paths = [
            os.path.join(att_folder, f"{dimpair_str}.png"),
            os.path.join(d21_folder, f"{dimpair_str}.png"),
        ]

        visualize_att(
            sources_coord_att=att_sources,
            targets_coord_att=att_targets,
            parties_coord_att=parties_coord_att,
            target_groups=mps_parties,
            dims=dict(zip(['x', 'y'], dimpair)),
            paths=paths,
            show=show,
            palette=palette,
            survey=survey,
            logger=logger,
            **attvizparams
            )
