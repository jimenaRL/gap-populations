import os
import pandas as pd
import seaborn as sns

from itertools import combinations

from gap.bivariate_marginal import \
    visualize_ide, \
    visualize_att

from gap.distributions import distributions

from gap.conf import \
    CHES2019DEFAULTATTVIZ, \
    GPS2019DEFAULTATTVIZ, \
    CHES2023DEFAULTATTVIZ, \
    CHES2020DEFAULTATTVIZ, \
    COLORS

def make_palette(palette, parties):
    sorted(parties)
    if not palette:
        return dict(zip(parties, COLORS))
    return palette

def plot_ideological_embedding(
    SQLITE,
    INOUT,
    country,
    n_dims_to_viz,
    vizparams,
    show,
    logger):

    # Load data from ideological embedding
    ide_sources, ide_targets = INOUT.load_ide_embeddings(source='db')

    idevizparams = vizparams['ideological']
    mp_parties = SQLITE.getMpParties(['EPO'])
    targets_parties = mp_parties[['mp_pseudo_id', 'EPO_party_acronym']] \
        .rename(columns={'EPO_party_acronym': 'party'})

    # select parties to show
    # these are the ones from EPO that have at least one mapping in an availbale survey
    parties_to_show = SQLITE.getPartiesMapping(SQLITE.getAvailableSurveys())[SQLITE.getPartiesMapping(SQLITE.getAvailableSurveys()) \
        .drop('EPO_party_acronym', axis=1).isna().sum(axis=1) != len(SQLITE.getAvailableSurveys())].EPO_party_acronym.tolist()

    output_folder = os.path.join(INOUT.emb_folder, 'figures')
    os.makedirs(output_folder, exist_ok=True)

    palette = make_palette(vizparams['palette'], parties_to_show)

    for x, y in combinations(range(n_dims_to_viz), 2):
        visualize_ide(
            sources_coord_ide=ide_sources,
            targets_coord_ide=ide_targets,
            targets_parties=targets_parties,
            parties_to_show=parties_to_show,
            latent_dim_x=x,
            latent_dim_y=y,
            output_folders=[output_folder],
            logger=logger,
            show=show,
            palette=palette,
            **idevizparams
        )


def plot_1d_attitudinal_distributions(
    SQLITE,
    INOUT,
    country,
    year,
    survey,
    attdims,
    logger,
    show):

    SURVEYCOL = f'{survey.upper()}_party_acronym'

    att_sources, att_targets = INOUT.load_att_embeddings(source='db')

    att_sources = att_sources[attdims]
    att_targets = att_targets[attdims]

    valfolder = os.path.join(INOUT.att_folder, 'validations')

    os.makedirs(os.path.join(INOUT.att_folder, 'figures'), exist_ok=True)

    paths=[
        os.path.join(INOUT.att_folder, 'figures', f"distributions.png"),
        os.path.join(INOUT.att_folder, 'figures', f"distributions.pdf"),
    ]

    # show by dim distributions
    distributions(
        att_sources,
        att_targets,
        country,
        year,
        survey,
        paths,
        logger,
        show)

def plot_attitudinal_embedding(
    SQLITE,
    INOUT,
    dimspair,
    country,
    survey,
    vizparams,
    show,
    logger,
    missing_values_strategy
    ):

    SURVEYCOL = f'{survey.upper()}_party_acronym'

    att_sources, att_targets = INOUT.load_att_embeddings()

    mps_parties = SQLITE.getMpParties(['EPO', survey], dropna=True)

    # (1) show 2d figures

    # select parties create the color palette
    # these are the ones from EPO that have at least one mapping in an availbale survey
    parties_with_mapping = SQLITE.getPartiesMapping(SQLITE.getAvailableSurveys())[SQLITE.getPartiesMapping(SQLITE.getAvailableSurveys()) \
        .drop('EPO_party_acronym', axis=1).isna().sum(axis=1) != len(SQLITE.getAvailableSurveys())].EPO_party_acronym.tolist()

    party_mapping = SQLITE.getPartiesMapping(surveys=[survey])
    # use mapping to adapt palette to the party system survey
    if not vizparams['palette']:
        palette = make_palette(
            vizparams['palette'], parties_with_mapping)
    else:
        palette = vizparams['palette']

    color_data = palette.items()
    palette = pd.DataFrame.from_dict(color_data) \
        .rename(columns={0: 'EPO_party_acronym', 1: 'color'}) \
        .merge(party_mapping)
    _zip = zip(palette[SURVEYCOL], palette['color'])
    palette = {z[0]: z[1] for z in _zip}

    # Load parties attitudinal coordinates
    parties_coord_att = SQLITE.getPartiesAttitudes(survey, dimspair, missing_values_strategy)

    rename_cols = {SURVEYCOL: 'party'}
    att_targets.rename(columns=rename_cols, inplace=True)
    parties_coord_att.rename(columns=rename_cols, inplace=True)

    # When the map from EPO parties to the survey's parties is not injective,
    # keep only one match
    parties_coord_att.drop_duplicates(subset=['party'], inplace=True)

    # visualize attitudinal espaces
    dimpair_str = '_vs_'.join(dimspair)

    attvizparams = globals()[f"{survey.upper()}DEFAULTATTVIZ"]

    output_folder = os.path.join(INOUT.att_folder, 'figures')
    os.makedirs(output_folder, exist_ok=True)
    visualize_att(
        sources_coord_att=att_sources,
        targets_coord_att=att_targets,
        parties_coord_att=parties_coord_att,
        target_groups=mps_parties,
        dims=dict(zip(['x', 'y'], dimspair)),
        paths=[os.path.join(INOUT.att_folder, 'figures', f"{dimpair_str}.png")],
        show=show,
        palette=palette,
        survey=survey,
        logger=logger,
        **attvizparams
        )
